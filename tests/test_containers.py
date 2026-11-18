import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_htc import tiny_case

from autonomous_traffic.htc.inputs import digest
from autonomous_traffic.htc.plan import preflight, prepare

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "container_transport", ROOT / "scripts/containers.py"
)
transport = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transport)


class ContainerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def sweep(self):
        tiny_case(self.root / "case")
        path = self.root / "sweep.json"
        path.write_text(
            json.dumps(
                {
                    "schema_version": "1",
                    "sweep_id": "sif-test",
                    "cases": ["case/case.json"],
                    "axes": {"speed": [8.0]},
                    "replicates": 1,
                    "base_seed": 7,
                    "seed_scope": "sumo_engine_only",
                    "resources": {
                        "cpus": 1,
                        "memory_mb": 512,
                        "disk_mb": 2048,
                        "wall_time_s": 60,
                    },
                }
            )
        )
        return path

    def test_sif_is_content_staged_and_mutation_blocks_preflight(self):
        # Deliberately not a runtime image: this test covers staging identity only.
        image = self.root / "fixture.sif"
        image.write_bytes(b"staging-only-fixture")
        plan = prepare(self.sweep(), self.root / "batch", sif=image)
        asset = plan["image_asset"]
        self.assertEqual(asset["sha256"], digest(image))
        self.assertIn(asset["sha256"], plan["container_image"])
        text = (self.root / "batch/sweep.submit").read_text()
        self.assertIn("HasSingularity", text)
        self.assertNotIn("apptainer exec", (self.root / "batch/worker.sh").read_text())
        self.assertNotIn(
            "images/",
            next(
                line
                for line in text.splitlines()
                if line.startswith("transfer_input_files")
            ),
        )
        with patch("autonomous_traffic.htc.plan.shutil.which", return_value=None):
            preflight(self.root / "batch")
        (self.root / "batch" / asset["path"]).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "SIF image changed"):
            preflight(self.root / "batch")

    def test_osdf_requires_content_named_image_and_is_not_claimed_verified(self):
        sweep = self.sweep()
        with self.assertRaisesRegex(ValueError, "immutable"):
            prepare(sweep, self.root / "bad", image="osdf:///ospool/data/current.sif")
        image = "osdf:///ospool/ap23/data/example/worker-" + "a" * 64 + ".sif"
        result = prepare(sweep, self.root / "batch", image=image)
        self.assertEqual(result["image_asset"]["delivery"], "osdf")
        self.assertIn("not downloaded", result["image_asset"]["validation"])
        with self.assertRaisesRegex(ValueError, "either"):
            prepare(sweep, self.root / "both", image=image, sif="anything.sif")

    def test_workspace_outputs_cannot_overwrite_or_recurse_into_inputs(self):
        source = self.root / "source"
        source.mkdir()
        with self.assertRaisesRegex(ValueError, "outside"):
            transport.workspaces(str(source), source / "nested")
        with self.assertRaisesRegex(ValueError, "fresh"):
            transport.workspaces("-", source)

    def test_docker_application_failure_exports_workspace_and_removes_only_its_container(
        self,
    ):
        calls = []

        def fake(args, **kwargs):
            calls.append(args)
            result = ""
            if args[:3] == ["docker", "image", "inspect"]:
                result = json.dumps(
                    [{"Id": "sha256:fixed", "Architecture": "amd64", "Os": "linux"}]
                )
            elif args[:2] == ["docker", "create"]:
                result = "test-created-container\n"
            elif args[:2] == ["docker", "inspect"]:
                result = json.dumps([{"State": {"Status": "exited", "ExitCode": 17}}])
            return subprocess.CompletedProcess(args, 0, stdout=result, stderr="")

        output = self.root / "output with spaces"
        with patch.object(transport.subprocess, "run", side_effect=fake):
            code = transport.execute(
                "docker",
                "local:tag",
                "-",
                output,
                ["autonomous-traffic", "bad-command"],
            )
        self.assertEqual(code, 17)
        create = next(c for c in calls if c[:2] == ["docker", "create"])
        self.assertIn("sha256:fixed", create)
        self.assertEqual(create[create.index("--network") + 1], "none")
        self.assertIn("--read-only", create)
        self.assertIn(
            [
                "docker",
                "cp",
                "--archive",
                "test-created-container:/work/.",
                str(output),
            ],
            calls,
        )
        self.assertEqual(
            calls[-1],
            ["docker", "rm", "--force", "--volumes", "test-created-container"],
        )
        receipt = json.loads(next((output / ".container-runs").iterdir()).read_text())
        self.assertEqual(receipt["exit_code"], 17)

    def test_docker_export_failure_cannot_report_success(self):
        calls = []

        def fake(args, **kwargs):
            calls.append(args)
            result = ""
            if args[:3] == ["docker", "image", "inspect"]:
                result = json.dumps(
                    [{"Id": "sha256:fixed", "Architecture": "amd64", "Os": "linux"}]
                )
            elif args[:2] == ["docker", "create"]:
                result = "export-failure-container"
            elif args[:2] == ["docker", "inspect"]:
                result = json.dumps([{"State": {"Status": "exited", "ExitCode": 0}}])
            elif args[:3] == ["docker", "cp", "--archive"]:
                raise subprocess.CalledProcessError(1, args)
            return subprocess.CompletedProcess(args, 0, stdout=result, stderr="")

        output = self.root / "export-failed"
        with patch.object(transport.subprocess, "run", side_effect=fake):
            self.assertNotEqual(
                transport.execute(
                    "docker", "tag", "-", output, ["autonomous-traffic", "doctor"]
                ),
                0,
            )
        self.assertEqual(
            calls[-1],
            ["docker", "rm", "--force", "--volumes", "export-failure-container"],
        )
        receipt = json.loads(next((output / ".container-runs").iterdir()).read_text())
        self.assertIn("error", receipt)

    def test_apptainer_clean_environment_keeps_input_and_records_failure(self):
        image = self.root / "test.sif"
        image.write_bytes(b"test")
        source = self.root / "input"
        source.mkdir()
        (source / "keep.txt").write_text("preserve")
        output = self.root / "output"
        with patch.object(
            transport.subprocess, "run", return_value=subprocess.CompletedProcess([], 9)
        ) as run:
            code = transport.execute(
                "apptainer",
                str(image),
                str(source),
                output,
                ["autonomous-traffic", "doctor"],
            )
        self.assertEqual(code, 9)
        self.assertEqual(
            (source / "keep.txt").read_text(), (output / "keep.txt").read_text()
        )
        self.assertIn("--cleanenv", run.call_args.args[0])
        self.assertIn("--containall", run.call_args.args[0])
