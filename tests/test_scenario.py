import json
import tempfile
import unittest
from pathlib import Path

from autonomous_traffic.demand import materialize
from autonomous_traffic.scenario import configure

BASE = (
    Path(__file__).resolve().parents[1]
    / "omf-artifacts/implementation/scenarios/coronado-benchmark.json"
)


class ScenarioTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.base = json.loads(BASE.read_text())

    def test_shift_clock_across_midnight_preserves_elapsed_demand_and_population(self):
        before = BASE.read_bytes()
        out = self.root / "variant.json"
        configure(BASE, out, start_local="22:00:00")
        variant = json.loads(out.read_text())
        self.assertEqual(variant["demand_horizon"]["stop_local"], "29:00:00")
        self.assertEqual(variant["demand_horizon"]["end_local"], "30:00:00")
        self.assertEqual(materialize(variant, 7), materialize(self.base, 7))
        self.assertEqual(BASE.read_bytes(), before)
        self.assertNotIn("acceptance", variant)
        self.assertFalse(variant["execution_ready"])

    def test_explicit_density_occupancy_and_household_histograms_reconcile_totals(self):
        patch = self.root / "patch.json"
        patch.write_text(
            json.dumps(
                {
                    "households": {"size_counts": {"2": 1000}},
                    "resident_trips": {"party_counts_by_persons": {"1": 330, "2": 50}},
                    "initial_road_loading": {
                        "target": 4,
                        "vehicle_occupancy_fractions": {"0": 0, "1": 1},
                    },
                    "external_future_arrivals": {
                        "counts_by_window": [
                            {
                                "from_local": "03:00:00",
                                "to_local": "10:00:00",
                                "vehicles_per_hour": 2,
                            }
                        ]
                    },
                }
            )
        )
        out = self.root / "v.json"
        configure(BASE, out, patch)
        value = json.loads(out.read_text())
        data = materialize(value, 1)
        self.assertEqual(data["summary"]["resident_persons"], 2000)
        self.assertEqual(data["summary"]["resident_travelers"], 430)
        self.assertEqual(data["summary"]["external_future_requests"], 14)
        self.assertEqual(data["summary"]["external_future_persons"], 14)
        self.assertEqual(value["initial_road_loading"]["target"], 4)

    def test_unknown_derived_inconsistent_or_approval_overrides_fail(self):
        cases = [
            {"households": {"count": 1}},
            {"initial_road_loading": {"targte": 3}},
            {"status": "accepted-hypothetical-benchmark"},
            {"accepted_context": {"start_local": "04:00:00"}},
            {"resident_trips": {"destinations": {"internal_requests": 1}}},
            {"demand_horizon": {"end_local": "04:00:00"}},
        ]
        for i, patch in enumerate(cases):
            path = self.root / f"p{i}.json"
            path.write_text(json.dumps(patch))
            with self.assertRaises((ValueError, KeyError)):
                configure(BASE, self.root / f"v{i}.json", path)
            self.assertFalse((self.root / f"v{i}.json").exists())

    def test_output_cannot_replace_base(self):
        with self.assertRaisesRegex(ValueError, "fresh"):
            configure(BASE, BASE, start_local="04:00:00")
