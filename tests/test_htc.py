import copy
import io
import json
import os
import shutil
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from autonomous_traffic.htc.collect import collect  # noqa: E402
from autonomous_traffic.htc.inputs import (  # noqa: E402
    bundle_case,
    digest,
    unpack_bundle,
    validate_case,
)
from autonomous_traffic.htc.plan import preflight, prepare  # noqa: E402
from autonomous_traffic.htc.worker import run_task, summarize  # noqa: E402


def tiny_case(root, name="case-a", speed=8.0):
    root.mkdir(parents=True)
    (root / "net.net.xml").write_text("<net/>")
    (root / "routes.xml").write_text(
        f'<routes><vType id="v" maxSpeed="{speed}"/><vehicle id="v0" depart="0"/></routes>'
    )
    (root / "requests.json").write_text(
        json.dumps(
            [
                {
                    "vehicle_id": "v0",
                    "person_count": 2,
                    "request_time_s": 0,
                    "initial": False,
                }
            ]
        )
    )

    def asset(f):
        return {"path": f, "sha256": digest(root / f)}

    case = {
        "schema_version": "1",
        "case_id": name,
        "backend": "sumo-native",
        "purpose": "engineering_fixture",
        "review_status": "engineering_fixture",
        "engine_version": "1.28.0",
        "parameters": {"speed": speed},
        "parameter_bindings": {
            "speed": {
                "path": "routes.xml",
                "xpath": ".//vType[@id='v']",
                "attribute": "maxSpeed",
            }
        },
        "network": asset("net.net.xml"),
        "routes": [asset("routes.xml")],
        "additional": [],
        "request_ledger": asset("requests.json"),
        "initialization": {"mode": "explicit_empty_fixture"},
        "simulation": {
            "begin_s": 0,
            "end_s": 160,
            "step_length_s": 0.5,
            "time_to_teleport_s": -1,
            "collision_action": "warn",
            "check_junction_collisions": True,
            "collision_min_gap_factor": 0,
        },
        "provenance": {
            "gis_source": "synthetic syntax fixture",
            "initial_parameterization": "fixture",
            "scope": "not traffic data",
            "input_realization_id": "fixed-v0",
        },
    }
    (root / "case.json").write_text(json.dumps(case))
    return case


class HTCTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.case = tiny_case(self.root / "case")
        self.path = self.root / "case/case.json"

    def tearDown(self):
        self.temp.cleanup()

    def save_case(self, case):
        self.path.write_text(json.dumps(case))

    def sweep(self):
        value = {
            "schema_version": "1",
            "sweep_id": "test",
            "cases": ["case/case.json"],
            "axes": {"speed": [8.0]},
            "replicates": 2,
            "base_seed": 11,
            "seed_scope": "sumo_engine_only",
            "resources": {
                "cpus": 1,
                "memory_mb": 512,
                "disk_mb": 512,
                "wall_time_s": 60,
            },
        }
        p = self.root / "sweep.json"
        p.write_text(json.dumps(value))
        return p, value

    def test_transfer_digest_and_parameter_binding_are_checked(self):
        validate_case(self.path)
        c = copy.deepcopy(self.case)
        c["parameters"]["speed"] = 12.0
        self.save_case(c)
        with self.assertRaisesRegex(ValueError, "binding mismatch"):
            validate_case(self.path)
        self.save_case(self.case)
        (self.root / "case/routes.xml").write_text("<routes/>")
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            validate_case(self.path)

    def test_traffic_experiment_cannot_silently_use_empty_start(self):
        c = copy.deepcopy(self.case)
        c.update(purpose="traffic_experiment", review_status="accepted")
        self.save_case(c)
        with self.assertRaisesRegex(ValueError, "Empty starts"):
            validate_case(self.path)

    def test_fresh_state_rejects_saved_rng_instead_of_ignoring_seed(self):
        state = self.root / "case/state.xml"
        state.write_text('<snapshot time="0"><rngState/></snapshot>')
        c = copy.deepcopy(self.case)
        c["initialization"] = {
            "mode": "fresh_sumo_state",
            "state": {"path": "state.xml", "sha256": digest(state)},
        }
        self.save_case(c)
        with self.assertRaisesRegex(ValueError, "RNG"):
            validate_case(self.path)

    def test_archive_is_reproducible_and_rejects_path_traversal(self):
        a, b = self.root / "a.tar.gz", self.root / "b.tar.gz"
        bundle_case(self.path, a)
        os.utime(self.path, (1000000, 1000000))
        bundle_case(self.path, b)
        self.assertEqual(digest(a), digest(b))
        attack = self.root / "attack.tar.gz"
        with tarfile.open(attack, "w:gz") as archive:
            info = tarfile.TarInfo("../escape")
            info.size = 1
            archive.addfile(info, io.BytesIO(b"x"))
        with self.assertRaises(ValueError):
            unpack_bundle(attack, self.root / "unpacked")
        self.assertFalse((self.root / "escape").exists())

    def test_factorial_design_requires_all_prepared_cells(self):
        source, value = self.sweep()
        value["axes"]["speed"].append(12.0)
        source.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "exactly cover"):
            prepare(source, self.root / "batch")
        self.assertFalse((self.root / "batch").exists())

    def test_oversized_design_is_rejected_before_cartesian_expansion(self):
        source, value = self.sweep()
        value["axes"] = {"a": list(range(100)), "b": list(range(100))}
        source.write_text(json.dumps(value))
        with patch("autonomous_traffic.htc.plan.itertools.product") as expand:
            with self.assertRaisesRegex(ValueError, "10,000"):
                prepare(source, self.root / "batch")
            expand.assert_not_called()
        self.assertFalse((self.root / "batch").exists())

    def test_plan_is_stable_has_no_submit_file_without_image_and_detects_tampering(
        self,
    ):
        source, _ = self.sweep()
        a = prepare(source, self.root / "batch-a")
        b = prepare(source, self.root / "batch-b")
        self.assertEqual(a["tasks"], b["tasks"])
        self.assertFalse((self.root / "batch-a/sweep.submit").exists())
        self.assertTrue((self.root / "batch-a/sweep.submit.in").exists())
        with patch("autonomous_traffic.htc.plan.shutil.which", return_value=None):
            self.assertEqual(
                preflight(self.root / "batch-a")["condor_parser"], "not_available"
            )
        task = self.root / "batch-a/tasks" / f"{a['tasks'][0]['task_id']}.json"
        task.write_text("{}")
        with self.assertRaisesRegex(ValueError, "changed"):
            preflight(self.root / "batch-a")

    def test_immutable_image_required_for_rendered_submit(self):
        source, _ = self.sweep()
        with self.assertRaisesRegex(ValueError, "immutable"):
            prepare(source, self.root / "bad", image="docker://worker:latest")
        plan = prepare(
            source,
            self.root / "batch",
            image="docker://example.invalid/worker@sha256:" + "a" * 64,
        )
        self.assertTrue(plan["submit_rendered"])
        text = (self.root / "batch/sweep.submit").read_text()
        self.assertIn("universe = container", text)
        self.assertIn("transfer_output_remaps", text)
        self.assertNotIn("checkpoint_exit_code", text)

    def test_unknown_routes_or_people_counts_fail_validation(self):
        p = self.root / "case/requests.json"
        for row in [
            {
                "vehicle_id": "other",
                "person_count": 2,
                "request_time_s": 0,
                "initial": False,
            },
            {
                "vehicle_id": "v0",
                "person_count": -1,
                "request_time_s": 0,
                "initial": False,
            },
        ]:
            p.write_text(json.dumps([row]))
            c = copy.deepcopy(self.case)
            c["request_ledger"]["sha256"] = digest(p)
            self.save_case(c)
            with self.assertRaises(ValueError):
                validate_case(self.path)

    def test_unfinished_requests_remain_in_summary(self):
        path = self.root / "tripinfo.xml"
        path.write_text(
            '<tripinfos><tripinfo id="a" arrival="20" depart="1"/><tripinfo id="b" arrival="-1" depart="5"/></tripinfos>'
        )
        requests = {
            "a": {"initial": False, "request_time_s": 0, "person_count": 2},
            "b": {"initial": False, "request_time_s": 4, "person_count": 0},
            "c": {"initial": False, "request_time_s": 10, "person_count": 1},
        }
        result = summarize(path, requests, 30)
        self.assertEqual(result["completed_vehicles"], 1)
        self.assertEqual(result["unfinished_vehicles"], 2)
        self.assertEqual(result["unfinished_accumulated_request_time_s"], 46)
        self.assertEqual(
            result["person_weighted_mean_completed_request_to_arrival_s"], 20
        )

    def test_missing_results_and_failed_workers_are_not_successful(self):
        source, _ = self.sweep()
        batch = self.root / "batch"
        plan = prepare(source, batch)
        report = collect(batch, self.root / "collection")
        self.assertFalse(report["complete"])
        self.assertEqual(report["counts"]["missing"], 2)
        row = plan["tasks"][0]
        task = batch / "tasks" / f"{row['task_id']}.json"
        bad = self.root / "wrong.tar.gz"
        bad.write_bytes(b"not a bundle")
        receipt, code = run_task(task, bad, self.root / "run")
        self.assertEqual(code, 2)
        self.assertEqual(receipt["status"], "failed")
        shutil.copyfile(
            self.root / "run.tar.gz", batch / "results" / f"{row['task_id']}.tar.gz"
        )
        report = collect(batch, self.root / "collection-2")
        self.assertEqual(report["counts"]["failed"], 1)
        self.assertEqual(report["counts"]["missing"], 1)
