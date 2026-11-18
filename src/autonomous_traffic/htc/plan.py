"""Enumerate prepared cases and replicates; render non-submitting HTCondor batches."""

import hashlib
import itertools
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

from .inputs import bundle_case, canonical, code_digest, digest

NAME = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")
IMAGE = re.compile(r"docker://[A-Za-z0-9._:/-]+@sha256:[a-f0-9]{64}\Z")


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n")


def prepare(sweep_path, output, image=None):
    sweep_path, output = Path(sweep_path).resolve(), Path(output).resolve()
    sweep = json.loads(sweep_path.read_text())
    if sweep["schema_version"] != "1" or not NAME.fullmatch(sweep["sweep_id"]):
        raise ValueError("Invalid sweep identity/version")
    if output.exists():
        raise ValueError("Use a new batch directory; existing batches are immutable")
    count, base = sweep["replicates"], sweep["base_seed"]
    if (
        type(count) is not int
        or not 1 <= count <= 10000
        or type(base) is not int
        or base < 0
        or base + count - 1 > 2147483647
    ):
        raise ValueError("Invalid replicate count/engine seed range")
    if sweep["resources"]["wall_time_s"] > 32400:
        raise ValueError(
            "The initial application worker wall-time guard is at most 32400 seconds; pool limits may be lower"
        )
    if sweep["seed_scope"] != "sumo_engine_only":
        raise ValueError(
            "Prepared inputs are immutable; this backend seeds only the engine. Prepare separate demand realizations explicitly."
        )
    if image is not None and not IMAGE.fullmatch(image):
        raise ValueError(
            "Use an immutable docker://registry/image@sha256:<digest> reference"
        )
    resources = sweep["resources"]
    for key in ["memory_mb", "disk_mb", "wall_time_s"]:
        if type(resources[key]) is not int or resources[key] < 1:
            raise ValueError("Resource limits must be positive integers")
    if type(resources["cpus"]) is not int or resources["cpus"] != 1:
        raise ValueError("Initial worker supports one CPU per independent run")
    axes = sweep["axes"]
    if not axes or any(not isinstance(v, list) or not v for v in axes.values()):
        raise ValueError("Declare a nonempty finite factorial design")
    if math.prod(len(v) for v in axes.values()) * count > 10000:
        raise ValueError(
            "Initial batches are limited to 10,000 tasks; pilot and partition larger designs explicitly"
        )
    expected = {
        canonical(dict(zip(sorted(axes), values)))
        for values in itertools.product(*(axes[k] for k in sorted(axes)))
    }
    if len(expected) != math.prod(len(v) for v in axes.values()):
        raise ValueError("Duplicate parameter levels")
    from .inputs import validate_case

    cases = {}
    for rel in sweep["cases"]:
        source = (sweep_path.parent / rel).resolve()
        case, _, _ = validate_case(source)
        key = canonical(case["parameters"])
        if key in cases or not NAME.fullmatch(case["case_id"]):
            raise ValueError("Duplicate parameter cell/invalid case ID")
        cases[key] = (source, case)
    if set(cases) != expected:
        raise ValueError(
            f"Prepared cases must exactly cover design: {len(expected - set(cases))} missing, {len(set(cases) - expected)} extra"
        )
    if len({v[1]["case_id"] for v in cases.values()}) != len(cases):
        raise ValueError("Case IDs must be unique")
    # All input checks precede creation of a batch that could be submitted.
    for name in ["tasks", "bundles", "logs", "results"]:
        (output / name).mkdir(parents=True, exist_ok=True)
    fingerprint = code_digest()
    tasks = []
    for key, (source, case) in sorted(cases.items()):
        bundle = output / "bundles" / f"{case['case_id']}.tar.gz"
        bundle_case(source, bundle)
        for replicate in range(count):
            identity = {
                "case_sha256": digest(source),
                "code_sha256": fingerprint,
                "replicate": replicate,
                "seed": base + replicate,
            }
            tid = "task-" + hashlib.sha256(canonical(identity)).hexdigest()[:24]
            task = {
                "schema_version": "1",
                "task_id": tid,
                "case_id": case["case_id"],
                "parameters": case["parameters"],
                "replicate": replicate,
                "seed": base + replicate,
                "seed_scope": sweep["seed_scope"],
                "bundle_name": bundle.name,
                "bundle_sha256": digest(bundle),
                "case_sha256": digest(source),
                "code_sha256": fingerprint,
                "wall_time_s": resources["wall_time_s"],
                "purpose": case["purpose"],
            }
            write_json(output / "tasks" / f"{tid}.json", task)
            tasks.append(task)
    worker = output / "worker.sh"
    worker.write_text(
        '#!/bin/sh\nset -eu\nexport PYTHONDONTWRITEBYTECODE=1\nexec autonomous-traffic htc-run "$@"\n'
    )
    worker.chmod(0o755)
    (output / "jobs.tsv").write_text(
        "".join(f"{t['task_id']} {t['case_id']}\n" for t in tasks)
    )
    submit = f"""# Generated batch: run condor_submit -dry-run classads.txt sweep.submit on the access point first.
universe = container
container_image = {image or "REPLACE_WITH_IMMUTABLE_WORKER_IMAGE"}
executable = worker.sh
arguments = --task $(task_id).json --bundle $(case_id).tar.gz --output result
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = tasks/$(task_id).json,bundles/$(case_id).tar.gz
transfer_output_files = result.tar.gz
transfer_output_remaps = "result.tar.gz=results/$(task_id).tar.gz"
output = logs/$(task_id).$(ClusterId).$(ProcId).out
error = logs/$(task_id).$(ClusterId).$(ProcId).err
log = logs/events.log
request_cpus = 1
request_memory = {resources["memory_mb"]}MB
request_disk = {resources["disk_mb"]}MB
requirements = (OpSys == "LINUX") && (Arch == "X86_64")
environment = "OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1"
on_exit_hold = (ExitBySignal =?= True) || (ExitCode =!= 0)
+JobDurationCategory = "Medium"
queue task_id,case_id from jobs.tsv
"""
    submit_name = "sweep.submit" if image else "sweep.submit.in"
    (output / submit_name).write_text(submit)
    plan = {
        "schema_version": "1",
        "sweep_id": sweep["sweep_id"],
        "status": "prepared_not_submitted",
        "container_image": image,
        "submit_file": submit_name,
        "submit_rendered": image is not None,
        "control_files": {
            name: digest(output / name)
            for name in ["worker.sh", "jobs.tsv", submit_name]
        },
        "pool_preflight": "not_run",
        "task_count": len(tasks),
        "resources": resources,
        "axes": axes,
        "replicates": count,
        "base_seed": base,
        "seed_scope": sweep["seed_scope"],
        "code_sha256": fingerprint,
        "tasks": [
            {
                "task_id": t["task_id"],
                "task_sha256": digest(output / "tasks" / f"{t['task_id']}.json"),
                "case_id": t["case_id"],
                "bundle_name": t["bundle_name"],
                "bundle_sha256": t["bundle_sha256"],
                "parameters": t["parameters"],
                "replicate": t["replicate"],
                "seed": t["seed"],
            }
            for t in tasks
        ],
    }
    write_json(output / "plan.json", plan)
    return plan


def preflight(batch):
    batch = Path(batch).resolve()
    plan = json.loads((batch / "plan.json").read_text())
    for name, expected in plan["control_files"].items():
        if digest(batch / name) != expected:
            raise ValueError("Batch control file changed: " + name)
    for row in plan["tasks"]:
        for path, expected in [
            (batch / "tasks" / f"{row['task_id']}.json", row["task_sha256"]),
            (batch / "bundles" / row["bundle_name"], row["bundle_sha256"]),
        ]:
            if digest(path) != expected:
                raise ValueError(f"Batch input changed: {path.name}")
    checks = {
        "task_count": len(plan["tasks"]),
        "input_digests": "passed",
        "container_image_configured": bool(plan["container_image"]),
        "condor_parser": "not_available",
        "submitted": False,
    }
    submit = shutil.which("condor_submit")
    if submit and not plan["submit_rendered"]:
        checks["condor_parser"] = "not_run_missing_image"
    if submit and plan["submit_rendered"]:
        result = subprocess.run(
            [submit, "-dry-run", "classads.txt", plan["submit_file"]],
            cwd=batch,
            capture_output=True,
            text=True,
        )
        checks.update(
            condor_parser="passed" if result.returncode == 0 else "failed",
            stdout=result.stdout,
            stderr=result.stderr,
        )
        if result.returncode:
            raise ValueError("HTCondor syntax preflight failed: " + result.stderr)
    return checks
