"""Validate returned task identities and retain failed/missing runs in aggregation."""

import csv
import hashlib
import json
import tarfile
from pathlib import Path

from .inputs import canonical
from .plan import write_json


def read_member(archive, name):
    member = archive.getmember(name)
    if not member.isfile() or member.size > 4 * 1024 * 1024:
        raise ValueError("Invalid/oversized result metadata")
    with archive.extractfile(member) as stream:
        data = stream.read()
    return data, json.loads(data)


def collect(batch, output):
    batch, output = Path(batch).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError("Use a new collection directory")
    plan = json.loads((batch / "plan.json").read_text())
    entries = []
    rows = []
    for expected in plan["tasks"]:
        tid = expected["task_id"]
        entry = {
            "task_id": tid,
            "case_id": expected["case_id"],
            "replicate": expected["replicate"],
            "seed": expected["seed"],
        }
        result = batch / "results" / f"{tid}.tar.gz"
        if not result.exists():
            entry["status"] = "missing"
        else:
            try:
                with tarfile.open(result, "r:gz") as archive:
                    _, run = read_member(archive, "run.json")
                    if (
                        run["task_id"] != tid
                        or run["task_sha256"] != expected["task_sha256"]
                        or run.get("bundle_sha256") != expected["bundle_sha256"]
                        or run["code_sha256"] != plan["code_sha256"]
                    ):
                        raise ValueError(
                            "Returned run identity/input fingerprint mismatch"
                        )
                    entry["status"] = run["status"]
                    if run["status"] == "succeeded":
                        data, metrics = read_member(archive, "metrics.json")
                        canonical(metrics)
                        if hashlib.sha256(data).hexdigest() != run["metrics_sha256"]:
                            raise ValueError("Returned metrics digest mismatch")
                        for key in [
                            "task_id",
                            "case_id",
                            "parameters",
                            "replicate",
                            "seed",
                        ]:
                            if metrics[key] != expected[key]:
                                raise ValueError(
                                    "Returned metrics identity/parameters mismatch"
                                )
                        rows.append(
                            {
                                **metrics,
                                "parameters": json.dumps(
                                    metrics["parameters"], sort_keys=True
                                ),
                            }
                        )
                    elif run["status"] == "failed":
                        entry["error"] = run.get("error", "unknown failure")
                    else:
                        raise ValueError("Unknown returned status")
            except (KeyError, ValueError, OSError, tarfile.TarError) as exc:
                entry.update(status="invalid", error=str(exc))
        entries.append(entry)
    counts = {
        status: sum(e["status"] == status for e in entries)
        for status in ["succeeded", "failed", "missing", "invalid"]
    }
    report = {
        "sweep_id": plan["sweep_id"],
        "expected_tasks": len(entries),
        "counts": counts,
        "complete": counts["succeeded"] == len(entries),
        "runs": entries,
        "interpretation": "Per-run metrics only; no automatic Pareto ranking or scientific robustness claim. Missing/failed tasks are not discarded.",
    }
    output.mkdir(parents=True)
    write_json(output / "collection.json", report)
    if rows:
        with (output / "metrics.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=sorted(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    return report
