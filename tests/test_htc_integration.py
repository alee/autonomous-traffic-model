import csv
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from autonomous_traffic.htc.collect import collect  # noqa: E402
from autonomous_traffic.htc.demo import create_demo  # noqa: E402
from autonomous_traffic.htc.local import run_local  # noqa: E402
from autonomous_traffic.htc.plan import prepare  # noqa: E402

HAS_ENGINE = bool(
    shutil.which("sumo")
    and shutil.which("netgenerate")
    and importlib.util.find_spec("sumolib")
)


@unittest.skipUnless(HAS_ENGINE, "SUMO optional integration environment not installed")
class HTCIntegration(unittest.TestCase):
    def test_serial_parallel_and_missing_returned_results(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            create_demo(root / "inputs")
            a, b = root / "serial", root / "parallel"
            first = prepare(root / "inputs/sweep.json", a)
            second = prepare(root / "inputs/sweep.json", b)
            self.assertEqual(first["tasks"], second["tasks"])
            self.assertEqual(run_local(a, jobs=1)["succeeded"], 8)
            self.assertEqual(run_local(b, jobs=2)["succeeded"], 8)
            self.assertTrue(collect(a, root / "serial-collection")["complete"])
            self.assertTrue(collect(b, root / "parallel-collection")["complete"])
            serial_bytes = (root / "serial-collection/metrics.csv").read_bytes()
            self.assertEqual(
                serial_bytes, (root / "parallel-collection/metrics.csv").read_bytes()
            )
            serial = (root / "serial-collection/metrics.csv").read_text()
            parallel = (root / "parallel-collection/metrics.csv").read_text()
            self.assertEqual(serial, parallel)
            rows = list(csv.DictReader(parallel.splitlines()))
            self.assertEqual(len(rows), 8)
            self.assertTrue(all(int(r["requested_vehicles"]) == 3 for r in rows))
            self.assertTrue(all(int(r["unfinished_vehicles"]) >= 1 for r in rows))
            evidence = os.environ.get("HTC_TEST_EVIDENCE")
            if evidence:
                target = Path(evidence)
                target.mkdir(parents=True)
                shutil.copytree(root / "inputs", target / "inputs")
                shutil.copytree(b, target / "batch")
                shutil.copytree(root / "parallel-collection", target / "collection")
                (target / "serial-metrics.csv").write_bytes(serial_bytes)
                (target / "verification.json").write_text(
                    json.dumps(
                        {
                            "serial_parallel_metrics_equal": True,
                            "case_count": 4,
                            "replicates": 2,
                            "tasks_per_batch": 8,
                            "total_local_native_executions": 16,
                        },
                        indent=2,
                    )
                    + "\n"
                )
            returned = next((b / "results").iterdir())
            returned.unlink()
            self.assertEqual(
                collect(b, root / "incomplete-collection")["counts"]["missing"], 1
            )
