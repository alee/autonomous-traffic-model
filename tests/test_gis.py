import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from autonomous_traffic.gis.audit import clipped_length, components
from autonomous_traffic.gis.prepare import build, plan, record_source

ROOT = Path(__file__).resolve().parents[1]
HAS_GEO = bool(importlib.util.find_spec("pyproj"))
HAS_ENGINE = bool(shutil.which("netconvert") and importlib.util.find_spec("sumolib"))
OSM = """<osm version="0.6">
<node id="1" lon="-112.065" lat="33.470"/><node id="2" lon="-112.060" lat="33.470"/>
<node id="3" lon="-112.055" lat="33.470"/><node id="4" lon="-112.060" lat="33.475"/>
<way id="10"><nd ref="1"/><nd ref="2"/><nd ref="3"/><tag k="highway" v="residential"/><tag k="lanes" v="2"/><tag k="maxspeed" v="25 mph"/></way>
<way id="20"><nd ref="2"/><nd ref="4"/><tag k="highway" v="residential"/><tag k="oneway" v="yes"/></way>
</osm>"""


class GeometryTests(unittest.TestCase):
    def test_segment_clipping_conserves_lengths_with_reentry_and_diagonal(self):
        box = [0, 0, 10, 10]
        self.assertEqual(clipped_length([(-5, 5), (15, 5), (-5, 5)], box), 20)
        self.assertEqual(clipped_length([(0, -5), (0, 15)], box), 10)
        self.assertEqual(clipped_length([(-5, -5), (-1, -1)], box), 0)
        self.assertAlmostEqual(clipped_length([(-5, -5), (15, 15)], box), 200**0.5)

    def test_directed_components_do_not_invent_reverse_reachability(self):
        graph = {"a": {"b"}, "b": {"a", "c"}, "c": set(), "d": set()}
        self.assertEqual([len(g) for g in components(graph)], [3, 1])
        self.assertEqual([len(g) for g in components(graph, True)], [2, 1, 1])


@unittest.skipUnless(HAS_GEO, "Optional geo environment not installed")
class GISTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = json.loads(
            (
                ROOT / "omf-artifacts/implementation/gis/coronado-network.proposed.json"
            ).read_text()
        )
        self.path = self.root / "config.json"
        self.path.write_text(json.dumps(self.config))

    def test_metric_buffer_and_scenario_context_are_explicit(self):
        scenario = json.loads(
            (
                ROOT / "omf-artifacts/implementation/scenarios/coronado-benchmark.json"
            ).read_text()
        )
        scenario["candidate_aoi"]["context_buffer_m"] = 500
        s = self.root / "scenario.json"
        s.write_text(json.dumps(scenario))
        value = plan(self.path, self.root / "plan", s)
        self.assertAlmostEqual(value["aoi_xy"][0] - value["context_xy"][0], 500)
        self.assertIsNotNone(value["benchmark_sha256"])
        self.assertFalse(value["traffic_ready"])

    def test_invalid_geometry_and_source_digest_fail_before_conversion(self):
        for key, value in [
            ("aoi_bbox_wgs84", [-111, 33, -112, 34]),
            ("metric_crs", "EPSG:4326"),
            ("context_margin_m", -1),
        ]:
            c = dict(self.config)
            c[key] = value
            self.path.write_text(json.dumps(c))
            with self.assertRaises(ValueError):
                plan(self.path, self.root / "bad")
        self.path.write_text(json.dumps(self.config))
        plan(self.path, self.root / "plan")
        raw = self.root / "raw.xml"
        raw.write_text(OSM)
        record_source(
            raw,
            self.root / "source",
            [-112.2, 33.4, -112, 33.6],
            "fixture:synthetic-osm",
        )
        (self.root / "source/source.osm.xml").write_text("<osm/>")
        with self.assertRaisesRegex(ValueError, "digest"):
            build(
                self.root / "plan/plan.json",
                self.root / "source",
                self.root / "network",
            )

    def test_source_coverage_and_scenario_context_cannot_silently_change(self):
        plan(self.path, self.root / "plan")
        raw = self.root / "raw.xml"
        raw.write_text(OSM)
        record_source(
            raw,
            self.root / "narrow",
            [-112.065, 33.469, -112.055, 33.476],
            "fixture:small",
        )
        with self.assertRaisesRegex(ValueError, "does not cover"):
            build(self.root / "plan/plan.json", self.root / "narrow", self.root / "bad")
        record_source(
            raw, self.root / "source", [-112.2, 33.4, -112, 33.6], "fixture:source"
        )
        scenario = json.loads(
            (
                ROOT / "omf-artifacts/implementation/scenarios/coronado-benchmark.json"
            ).read_text()
        )
        scenario["candidate_aoi"]["context_buffer_m"] = 500
        path = self.root / "scenario.json"
        path.write_text(json.dumps(scenario))
        with self.assertRaisesRegex(ValueError, "context changed"):
            build(
                self.root / "plan/plan.json",
                self.root / "source",
                self.root / "bad",
                path,
            )
        self.assertFalse((self.root / "bad").exists())

    def test_overpass_partial_error_is_never_accepted_as_a_source(self):
        raw = self.root / "partial.xml"
        raw.write_text("<osm><remark>timeout</remark></osm>")
        with self.assertRaisesRegex(ValueError, "remark"):
            record_source(
                raw, self.root / "source", [-112.2, 33.4, -112, 33.6], "fixture:partial"
            )
        self.assertFalse((self.root / "source").exists())

    @unittest.skipUnless(HAS_ENGINE, "Optional SUMO environment not installed")
    def test_offline_conversion_and_audit_preserve_oneway_and_count_contract(self):
        plan(self.path, self.root / "plan")
        raw = self.root / "raw.xml"
        raw.write_text(OSM)
        record_source(
            raw,
            self.root / "source",
            [-112.2, 33.4, -112, 33.6],
            "fixture:synthetic-osm",
        )
        result = build(
            self.root / "plan/plan.json",
            self.root / "source",
            self.root / "network",
            ROOT / "omf-artifacts/implementation/scenarios/coronado-benchmark.json",
        )
        audit = json.loads((self.root / "network/audit.json").read_text())
        self.assertGreater(audit["lane_km"]["context"], 0)
        self.assertLessEqual(
            audit["lane_km"]["context"], audit["lane_km"]["retained_network"] + 1e-8
        )
        self.assertEqual(audit["osm_source_audit"]["missing_way_node_refs"], [])
        self.assertFalse(result["traffic_ready"])
        import sumolib

        net = sumolib.net.readNet(str(self.root / "network/network.net.xml"))
        self.assertTrue(net.hasEdge("20"))
        self.assertFalse(net.hasEdge("-20"))
