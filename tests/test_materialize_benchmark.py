import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "materializer", ROOT / "scripts/materialize_benchmark.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MaterializeTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(
            (
                ROOT / "omf-artifacts/implementation/scenarios/coronado-benchmark.json"
            ).read_text()
        )

    def test_population_parties_accounting_and_reproducibility(self):
        data = module.materialize(self.config, 20261117)
        self.assertEqual(data, module.materialize(self.config, 20261117))
        self.assertEqual(len(data["households"]), 1000)
        self.assertEqual(len(data["residents"]), 2300)
        requests = data["resident_trips"]
        self.assertEqual(len(requests), 380)
        people = [p for t in requests for p in t["person_ids"]]
        self.assertEqual(len(people), 460)
        self.assertEqual(len(set(people)), 460)
        self.assertEqual(len({t["household_id"] for t in requests}), 380)
        households = {
            h["household_id"]: set(h["resident_ids"]) for h in data["households"]
        }
        for trip in requests:
            self.assertTrue(set(trip["person_ids"]) <= households[trip["household_id"]])
            self.assertLess(len(trip["person_ids"]), 5)
            self.assertTrue(0 <= trip["departure_elapsed_us"] < 25_200_000_000)
        self.assertEqual(len(data["external_trips"]), 510)
        self.assertEqual(len(data["external_people"]), 560)
        self.assertFalse(
            set(people) & {p["person_id"] for p in data["external_people"]}
        )
        self.assertIsNone(data["summary"]["initial_on_road_vehicle_count"])

    def test_different_seed_preserves_marginals_but_changes_realization(self):
        a, b = module.materialize(self.config, 1), module.materialize(self.config, 2)
        self.assertNotEqual(a["resident_trips"], b["resident_trips"])
        for key in [
            "resident_travelers",
            "resident_vehicle_requests",
            "external_future_requests",
        ]:
            self.assertEqual(a["summary"][key], b["summary"][key])

    def test_rejects_impossible_parties_and_inconsistent_demand(self):
        cases = []
        for change in ["unaccepted", "population", "windows", "capacity"]:
            c = copy.deepcopy(self.config)
            if change == "unaccepted":
                c["status"] = "proposed-not-accepted"
            elif change == "population":
                c["households"]["resident_persons_derived"] = 1
            elif change == "windows":
                c["resident_trips"]["departure_vehicle_counts"][0]["count"] += 1
            else:
                c["vehicle_service"]["resident_seat_capacity"] = 2
            cases.append(c)
        for c in cases:
            with self.assertRaises(ValueError):
                module.materialize(c, 0)

    def test_fraction_allocation_and_no_stream_consumption_coupling(self):
        self.assertEqual(
            module.largest_remainder(510, {"0": 0.05, "1": 0.8, "2": 0.15}),
            {0: 26, 1: 408, 2: 76},
        )
        baseline = module.random_stream(7, "demand").random()
        other = module.random_stream(7, "policy")
        for _ in range(1000):
            other.random()
        self.assertEqual(baseline, module.random_stream(7, "demand").random())


if __name__ == "__main__":
    unittest.main()
