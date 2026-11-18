import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from autonomous_traffic.cli import main  # noqa: E402 -- allow tests from an uninstalled checkout

CONFIG = ROOT / "omf-artifacts/implementation/scenarios/coronado-benchmark.json"


class CliTests(unittest.TestCase):
    def test_materialization_matches_reviewed_output_hashes(self):
        with (
            tempfile.TemporaryDirectory() as temp,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            code = main(["materialize", "--config", str(CONFIG), "--output", temp])
            self.assertEqual(code, 0)
            actual = json.loads((Path(temp) / "files-manifest.json").read_text())
            recorded = json.loads(
                (
                    ROOT
                    / "omf-artifacts/implementation/generated/coronado-demand/files-manifest.json"
                ).read_text()
            )
            # Runtime version is recorded but patch-version metadata is not scientific output.
            actual_hashes = dict(actual["files"])
            recorded_hashes = dict(recorded["files"])
            actual_hashes.pop("summary.json")
            recorded_hashes.pop("summary.json")
            self.assertEqual(actual_hashes, recorded_hashes)
            self.assertEqual(actual["input_sha256"], recorded["input_sha256"])
            summary = json.loads((Path(temp) / "summary.json").read_text())
            expected = json.loads(
                (
                    ROOT
                    / "omf-artifacts/implementation/generated/coronado-demand/summary.json"
                ).read_text()
            )
            summary["randomness"].pop("python")
            expected["randomness"].pop("python")
            self.assertEqual(summary, expected)

    def test_input_error_reports_failure_without_output(self):
        with (
            tempfile.TemporaryDirectory() as temp,
            contextlib.redirect_stderr(io.StringIO()) as err,
        ):
            base = Path(temp)
            source = base / "broken.json"
            source.write_text("{invalid")
            target = base / "output"
            self.assertEqual(
                main(["materialize", "--config", str(source), "--output", str(target)]),
                2,
            )
            self.assertFalse(target.exists())
            self.assertIn("error:", err.getvalue())

    def test_output_conflict_preserves_existing_files(self):
        with (
            tempfile.TemporaryDirectory() as temp,
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            args = ["materialize", "--config", str(CONFIG), "--output", temp]
            self.assertEqual(main(args), 0)
            before = {p.name: p.read_bytes() for p in Path(temp).iterdir()}
            self.assertEqual(main(args + ["--seed", "7"]), 2)
            self.assertEqual(
                before, {p.name: p.read_bytes() for p in Path(temp).iterdir()}
            )

    def test_negative_seed_rejected(self):
        with (
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit) as exc,
        ):
            main(
                [
                    "materialize",
                    "--config",
                    str(CONFIG),
                    "--output",
                    "/unused",
                    "--seed",
                    "-1",
                ]
            )
        self.assertEqual(exc.exception.code, 2)

    def test_doctor_is_an_inventory_not_model_readiness(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(main(["doctor"]), 0)
        report = json.loads(out.getvalue())
        self.assertEqual(report["package_version"], "0.1.0")
        self.assertIn("does not establish model readiness", report["note"])

    def test_legacy_materialization_entry_point(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/materialize_benchmark.py"),
                    "--config",
                    str(CONFIG),
                    "--output",
                    temp,
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(result.stdout)["total_future_vehicle_requests"], 890
            )


if __name__ == "__main__":
    unittest.main()
