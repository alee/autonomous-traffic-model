"""Execute one immutable native-SUMO case offline and return a bounded result archive."""

import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from .inputs import canonical, code_digest, digest, unpack_bundle, validate_case
from .plan import write_json


def summarize(path, requests, end_s):
    observed = {}
    for _, element in ET.iterparse(path, events=("end",)):
        if element.tag == "tripinfo":
            vid = element.attrib["id"]
            if vid in observed or vid not in requests:
                raise ValueError("Unexpected or duplicate tripinfo vehicle")
            observed[vid] = dict(element.attrib)
            element.clear()
    durations = []
    person_total = 0
    person_time = 0.0
    entered = 0
    completed = 0
    unfinished_wait = 0.0
    for vid, request in requests.items():
        info = observed.get(vid, {})
        arrival = float(info.get("arrival", -1))
        departed = float(info.get("depart", -1))
        entered += request["initial"] or departed >= 0
        if arrival >= 0:
            duration = arrival - request["request_time_s"]
            if duration < 0 or not math.isfinite(duration):
                raise ValueError("Invalid completed request time")
            durations.append(duration)
            completed += 1
            person_total += request["person_count"]
            person_time += duration * request["person_count"]
        else:
            unfinished_wait += end_s - request["request_time_s"]
    durations.sort()
    return {
        "requested_vehicles": len(requests),
        "entered_vehicles": entered,
        "completed_vehicles": completed,
        "unfinished_vehicles": len(requests) - completed,
        "unfinished_fraction": (len(requests) - completed) / len(requests)
        if requests
        else None,
        "mean_completed_request_to_arrival_s": sum(durations) / len(durations)
        if durations
        else None,
        "p95_completed_request_to_arrival_s_nearest_rank": durations[
            math.ceil(0.95 * len(durations)) - 1
        ]
        if durations
        else None,
        "requested_persons_ledger": sum(r["person_count"] for r in requests.values()),
        "completed_persons_ledger": person_total,
        "person_weighted_mean_completed_request_to_arrival_s": person_time
        / person_total
        if person_total
        else None,
        "unfinished_accumulated_request_time_s": unfinished_wait,
        "person_accounting": "ledger weighted; carried persons are not independently verified by this native backend",
        "safety_interpretation": "engine event counts only; no collision-avoidance or injury claim",
    }


def run_task(task_path, bundle, output, sumo=None):
    task_path, bundle, output = (
        Path(task_path).resolve(),
        Path(bundle).resolve(),
        Path(output).resolve(),
    )
    archive = output.with_suffix(".tar.gz")
    if output.exists() or archive.exists():
        raise ValueError(
            "Use a fresh task output directory; do not overwrite an earlier attempt"
        )
    output.mkdir(parents=True)
    started = time.monotonic()
    receipt = {
        "schema_version": "1",
        "status": "failed",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "task_sha256": digest(task_path),
        "task_id": None,
        "code_sha256": code_digest(),
    }
    success = False
    try:
        task = json.loads(task_path.read_text())
        receipt.update(
            {
                k: task[k]
                for k in [
                    "task_id",
                    "case_id",
                    "parameters",
                    "replicate",
                    "seed",
                    "seed_scope",
                    "bundle_sha256",
                ]
            }
        )
        identity = {
            "case_sha256": task["case_sha256"],
            "code_sha256": task["code_sha256"],
            "replicate": task["replicate"],
            "seed": task["seed"],
        }
        if (
            task["schema_version"] != "1"
            or task["task_id"]
            != "task-" + hashlib.sha256(canonical(identity)).hexdigest()[:24]
        ):
            raise ValueError("Task identity mismatch")
        receipt["actual_bundle_sha256"] = digest(bundle)
        if (
            receipt["code_sha256"] != task["code_sha256"]
            or receipt["actual_bundle_sha256"] != task["bundle_sha256"]
        ):
            raise ValueError("Worker code or transferred input digest mismatch")
        if (
            task["seed_scope"] != "sumo_engine_only"
            or type(task["seed"]) is not int
            or not 0 <= task["seed"] <= 2147483647
        ):
            raise ValueError("Unsupported seed contract")
        if (
            type(task["wall_time_s"]) is not int
            or not 1 <= task["wall_time_s"] <= 32400
        ):
            raise ValueError(
                "Task wall time must be explicitly bounded at <=32400 seconds"
            )
        binary = sumo or shutil.which("sumo")
        if not binary:
            raise ValueError("SUMO is not installed in the worker image")
        version = subprocess.run(
            [binary, "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        ).stdout
        if not re.search(r"\bsumo\s+1\.28\.0\b", version):
            raise ValueError("Worker requires the prepared SUMO 1.28.0 build line")
        receipt["engine_version_output"] = version.splitlines()[0]
        with tempfile.TemporaryDirectory(prefix="traffic-input-") as temp:
            case_path = unpack_bundle(bundle, Path(temp) / "input")
            if digest(case_path) != task["case_sha256"]:
                raise ValueError("Prepared case identity mismatch")
            case, requests, _ = validate_case(case_path)
            if (
                case["parameters"] != task["parameters"]
                or case["case_id"] != task["case_id"]
                or case["purpose"] != task["purpose"]
            ):
                raise ValueError("Prepared case parameters/purpose mismatch")
            sim = case["simulation"]

            def path(item):
                return str(case_path.parent / item["path"])

            command = [
                binary,
                "--net-file",
                path(case["network"]),
                "--route-files",
                ",".join(path(a) for a in case["routes"]),
                "--begin",
                str(sim["begin_s"]),
                "--end",
                str(sim["end_s"]),
                "--step-length",
                str(sim["step_length_s"]),
                "--seed",
                str(task["seed"]),
                "--time-to-teleport",
                "-1",
                "--collision.action",
                "warn",
                "--collision.check-junctions",
                str(sim["check_junction_collisions"]).lower(),
                "--collision.mingap-factor",
                str(sim["collision_min_gap_factor"]),
                "--tripinfo-output",
                str(output / "tripinfo.xml"),
                "--tripinfo-output.write-unfinished",
                "true",
                "--tripinfo-output.write-undeparted",
                "true",
                "--collision-output",
                str(output / "collisions.xml"),
                "--xml-validation",
                "never",
                "--no-step-log",
                "true",
                "--duration-log.disable",
                "true",
            ]
            if case["additional"]:
                command += [
                    "--additional-files",
                    ",".join(path(a) for a in case["additional"]),
                ]
            if case["initialization"]["mode"] == "fresh_sumo_state":
                command += ["--load-state", path(case["initialization"]["state"])]
            receipt.update(
                prepared_provenance=case["provenance"],
                simulation=sim,
                command=command,
                initialization=case["initialization"]["mode"],
                input_realization_id=case["provenance"]["input_realization_id"],
            )
            with (
                (output / "sumo.stdout").open("w") as stdout,
                (output / "sumo.stderr").open("w") as stderr,
            ):
                result = subprocess.run(
                    command,
                    cwd=case_path.parent,
                    stdout=stdout,
                    stderr=stderr,
                    timeout=task["wall_time_s"],
                    env={
                        **os.environ,
                        "OMP_NUM_THREADS": "1",
                        "OPENBLAS_NUM_THREADS": "1",
                    },
                )
            receipt["engine_return_code"] = result.returncode
            if result.returncode:
                raise ValueError(
                    f"SUMO exited with code {result.returncode}; inspect sumo.stderr"
                )
            metrics = summarize(output / "tripinfo.xml", requests, sim["end_s"])
            metrics["registered_collision_events"] = len(
                ET.parse(output / "collisions.xml").getroot().findall("collision")
            )
            metrics.update(
                task_id=task["task_id"],
                case_id=task["case_id"],
                parameters=task["parameters"],
                replicate=task["replicate"],
                seed=task["seed"],
                seed_scope=task["seed_scope"],
            )
            write_json(output / "metrics.json", metrics)
            receipt.update(
                status="succeeded", metrics_sha256=digest(output / "metrics.json")
            )
            # Compact returned evidence; original inputs and per-job aggregate receipt remain immutable.
            (output / "tripinfo.xml").unlink()
            (output / "collisions.xml").unlink()
            success = True
    except Exception as exc:
        receipt["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        receipt["wall_time_s"] = time.monotonic() - started
        write_json(output / "run.json", receipt)
        with tarfile.open(archive, "w:gz") as packed:
            for p in sorted(output.iterdir()):
                if p.is_file():
                    packed.add(p, arcname=p.name, recursive=False)
    return receipt, 0 if success else 2
