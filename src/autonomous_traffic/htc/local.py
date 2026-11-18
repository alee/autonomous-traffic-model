"""Local task orchestration using the same isolated worker contract as HTCondor."""

import json
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .inputs import code_digest
from .plan import preflight
from .worker import run_task


def run_local(batch, jobs=1, sumo=None):
    batch = Path(batch).resolve()
    if type(jobs) is not int or not 1 <= jobs <= 32:
        raise ValueError("Local concurrency must be between 1 and 32")
    preflight(batch)
    plan = json.loads((batch / "plan.json").read_text())
    if plan["code_sha256"] != code_digest():
        raise ValueError(
            "Worker source changed since planning; prepare a new immutable batch"
        )
    if any((batch / "results").iterdir()):
        raise ValueError(
            "Local results already exist; do not overwrite an earlier batch attempt"
        )

    def execute(row):
        tid = row["task_id"]
        with tempfile.TemporaryDirectory(prefix="traffic-local-") as temp:
            receipt, code = run_task(
                batch / "tasks" / f"{tid}.json",
                batch / "bundles" / row["bundle_name"],
                Path(temp) / "result",
                sumo,
            )
            shutil.copyfile(
                Path(temp) / "result.tar.gz", batch / "results" / f"{tid}.tar.gz"
            )
            return {"task_id": tid, "status": receipt["status"], "exit_code": code}

    with ThreadPoolExecutor(max_workers=jobs) as executor:
        outcomes = list(executor.map(execute, plan["tasks"]))
    return {
        "execution": "local_native_not_container_or_pool",
        "jobs": jobs,
        "task_count": len(outcomes),
        "succeeded": sum(r["exit_code"] == 0 for r in outcomes),
        "failed": sum(r["exit_code"] != 0 for r in outcomes),
        "runs": outcomes,
    }
