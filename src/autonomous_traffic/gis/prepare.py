"""Bounded OSM acquisition, explicit SUMO conversion, and traceable metric geometry."""

import json
import math
import shutil
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from ..htc.inputs import digest, xml_root
from ..htc.plan import write_json

MAX_SOURCE_BYTES = 32 * 1024 * 1024
ENDPOINT = "https://overpass-api.de/api/interpreter"


def projection(crs):
    try:
        import pyproj
    except ImportError as exc:
        raise ValueError("Network preparation requires the optional geo extra") from exc
    pyproj.network.set_network_enabled(False)
    target = pyproj.CRS(crs)
    if not target.is_projected or any(a.unit_name != "metre" for a in target.axis_info):
        raise ValueError("An explicit projected CRS with metre units is required")
    return (
        pyproj.Transformer.from_crs("EPSG:4326", target, always_xy=True),
        pyproj.Transformer.from_crs(target, "EPSG:4326", always_xy=True),
    )


def bbox(value):
    if (
        not isinstance(value, list)
        or len(value) != 4
        or any(type(v) not in (int, float) or not math.isfinite(v) for v in value)
    ):
        raise ValueError("Bounding boxes require four finite coordinates")
    w, s, e, n = value
    if not -180 <= w < e <= 180 or not -85 <= s < n <= 85:
        raise ValueError("Use a non-dateline-crossing WGS84 box within latitude ±85")
    return value


def corners(box):
    w, s, e, n = box
    return [(w, s), (e, s), (e, n), (w, n)]


def envelope(points):
    return [
        min(p[0] for p in points),
        min(p[1] for p in points),
        max(p[0] for p in points),
        max(p[1] for p in points),
    ]


def expand(box, margin):
    return [box[0] - margin, box[1] - margin, box[2] + margin, box[3] + margin]


def plan(config_path, output, benchmark=None):
    config_path, output = Path(config_path), Path(output)
    if output.exists():
        raise ValueError("Use a fresh network plan directory")
    config = json.loads(config_path.read_text())
    if config["schema_version"] != "1" or config["geometry_status"] not in {
        "proposed",
        "reviewed",
    }:
        raise ValueError("Declare plan version and geometry review status")
    if benchmark:
        scenario = json.loads(Path(benchmark).read_text())
        config["context_margin_m"] = scenario["candidate_aoi"]["context_buffer_m"]
    aoi = bbox(config["aoi_bbox_wgs84"])
    for key in ["context_margin_m", "download_margin_m"]:
        if (
            type(config[key]) not in (int, float)
            or not math.isfinite(config[key])
            or config[key] < 0
        ):
            raise ValueError("Metric margins must be finite and nonnegative")
    forward, inverse = projection(config["metric_crs"])
    xy = envelope([forward.transform(*p, errcheck=True) for p in corners(aoi)])
    context = expand(xy, config["context_margin_m"])
    fetch = envelope(
        [
            inverse.transform(*p, errcheck=True)
            for p in corners(expand(context, config["download_margin_m"]))
        ]
    )
    bbox(fetch)
    if (fetch[2] - fetch[0]) * (fetch[3] - fetch[1]) > 0.01:
        raise ValueError(
            "Initial direct Overpass fetch budget is 0.01 square degrees; prepare a larger offline source explicitly"
        )
    w, s, e, n = fetch
    query = f'[out:xml][timeout:45];(way["highway"]({s},{w},{n},{e});relation["type"="restriction"]({s},{w},{n},{e}););(._;>>;);out body;'
    record = {
        "schema_version": "1",
        "study_id": config["study_id"],
        "config_sha256": digest(config_path),
        "benchmark_sha256": digest(benchmark) if benchmark else None,
        "context_margin_source": "benchmark candidate_aoi.context_buffer_m"
        if benchmark
        else "network configuration",
        "geometry_status": config["geometry_status"],
        "metric_crs": config["metric_crs"],
        "aoi_bbox_wgs84": aoi,
        "aoi_xy": xy,
        "context_xy": context,
        "fetch_bbox_wgs84": fetch,
        "context_margin_m": config["context_margin_m"],
        "download_margin_m": config["download_margin_m"],
        "context_method": "projected AOI-corner envelope expanded on each axis; not a rounded polygon buffer",
        "endpoint": ENDPOINT,
        "query": query,
        "traffic_ready": False,
    }
    features = []
    for label, box in [("aoi", xy), ("context", context)]:
        ring = [list(inverse.transform(*p, errcheck=True)) for p in corners(box)]
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "role": label,
                    "geometry_status": config["geometry_status"],
                },
                "geometry": {"type": "Polygon", "coordinates": [ring + [ring[0]]]},
            }
        )
    output.mkdir(parents=True)
    write_json(output / "plan.json", record)
    write_json(
        output / "scope.geojson", {"type": "FeatureCollection", "features": features}
    )
    (output / "query.overpassql").write_text(query + "\n")
    return record


def record_source(osm_file, output, requested_bbox, source_uri, query=None):
    osm_file, output = Path(osm_file), Path(output)
    if output.exists():
        raise ValueError("Use a fresh source directory")
    if osm_file.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("OSM source exceeds preparation budget")
    root = xml_root(osm_file)
    if root.tag != "osm" or root.findall("remark") or root.findall("error"):
        raise ValueError("OSM response is invalid or carries an Overpass error/remark")
    coverage = bbox(requested_bbox)
    output.mkdir(parents=True)
    shutil.copyfile(osm_file, output / "source.osm.xml")
    record = {
        "schema_version": "1",
        "source_uri": source_uri,
        "requested_bbox_wgs84": coverage,
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": digest(output / "source.osm.xml"),
        "attribution": "© OpenStreetMap contributors",
        "license": "ODbL-1.0",
        "license_url": "https://opendatacommons.org/licenses/odbl/1-0/",
        "copyright_url": "https://www.openstreetmap.org/copyright",
        "osm_base": root.find("meta").attrib.get("osm_base")
        if root.find("meta") is not None
        else None,
        "query": query,
        "coverage_note": "Requested extent is acquisition metadata, not a guarantee of map completeness",
    }
    write_json(output / "source.json", record)
    return record


def fetch(plan_path, output):
    import tempfile

    p = json.loads(Path(plan_path).read_text())
    if Path(output).exists():
        raise ValueError("Use a fresh source directory")
    if p["endpoint"] != ENDPOINT:
        raise ValueError("Use the documented public Overpass endpoint")
    url = p["endpoint"] + "?" + urllib.parse.urlencode({"data": p["query"]})
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "autonomous-traffic-model/0.1 bounded research GIS preparation"
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read(MAX_SOURCE_BYTES + 1)
    if len(data) > MAX_SOURCE_BYTES:
        raise ValueError("OSM source exceeds bounded download budget")
    with tempfile.TemporaryDirectory(prefix="traffic-osm-") as temp:
        local = Path(temp) / "source.osm.xml"
        local.write_bytes(data)
        return record_source(local, output, p["fetch_bbox_wgs84"], url, p["query"])


def build(plan_path, source_dir, output, benchmark=None, netconvert=None):
    from .audit import audit

    plan_path, source_dir, output = Path(plan_path), Path(source_dir), Path(output)
    if output.exists():
        raise ValueError("Use a fresh network build directory")
    p = json.loads(plan_path.read_text())
    source = json.loads((source_dir / "source.json").read_text())
    osm = source_dir / "source.osm.xml"
    if osm.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("OSM source exceeds preparation budget")
    if digest(osm) != source["sha256"]:
        raise ValueError("OSM source digest mismatch")
    w, s, e, n = bbox(source["requested_bbox_wgs84"])
    a, b, c, d = p["fetch_bbox_wgs84"]
    if not w <= a < c <= e or not s <= b < d <= n:
        raise ValueError(
            "Acquired source does not cover planned context and download margin"
        )
    if benchmark:
        candidate = json.loads(Path(benchmark).read_text())
        if candidate["candidate_aoi"]["context_buffer_m"] != p["context_margin_m"]:
            raise ValueError(
                "Scenario context changed; prepare a matching network plan"
            )
    projection(p["metric_crs"])
    xml_root(osm)
    binary = netconvert or shutil.which("netconvert")
    if not binary:
        raise ValueError("netconvert is required; install the optional sumo extra")
    version = subprocess.check_output(
        [binary, "--version"], text=True, timeout=15
    ).splitlines()[0]
    if "1.28.0" not in version:
        raise ValueError("Network conversion requires SUMO 1.28.0")
    output.mkdir(parents=True)
    # No automatic repair, guessed ramps, geometry pruning or controller optimization.
    # Default typemap inference remains visible in source/network audit and converter logs.
    import pyproj

    proj = pyproj.Proj(p["metric_crs"]).srs
    command = [
        binary,
        "--osm-files",
        str(osm.resolve()),
        "--output-file",
        "network.net.xml",
        "--proj",
        proj,
        "--keep-edges.in-geo-boundary",
        ",".join(map(str, p["fetch_bbox_wgs84"])),
        "--geometry.remove",
        "false",
        "--junctions.join",
        "false",
        "--ramps.guess",
        "false",
        "--tls.guess",
        "false",
        "--tls.guess-signals",
        "false",
        "--tls.default-type",
        "static",
        "--xml-validation",
        "never",
    ]
    with (
        (output / "netconvert.stdout").open("w") as out,
        (output / "netconvert.stderr").open("w") as err,
    ):
        result = subprocess.run(
            command, cwd=output, stdout=out, stderr=err, timeout=180
        )
    receipt = {
        "schema_version": "1",
        "status": "failed",
        "engine": version,
        "command": command,
        "plan_sha256": digest(plan_path),
        "source_sha256": digest(osm),
        "engine_return_code": result.returncode,
        "benchmark_sha256": digest(benchmark) if benchmark else None,
        "traffic_ready": False,
    }
    write_json(output / "build.json", receipt)
    if result.returncode:
        raise ValueError("netconvert failed; inspect retained build logs")
    report = audit(output / "network.net.xml", p, osm)
    if benchmark:
        from decimal import ROUND_HALF_UP, Decimal

        config = json.loads(Path(benchmark).read_text())
        loading = config["initial_road_loading"]
        rate = loading["target"]
        if (
            loading["measure"] != "vehicles_per_lane_km"
            or type(rate) not in (int, float)
            or not math.isfinite(rate)
            or rate < 0
        ):
            raise ValueError(
                "Explicit finite nonnegative vehicles-per-lane-km target required"
            )
        lane_km = report["lane_km"]["context"]
        report["conditional_initial_road_target"] = {
            "vehicles_per_lane_km": rate,
            "context_lane_km": lane_km,
            "vehicle_count": int(
                (Decimal(str(rate)) * Decimal(str(lane_km))).quantize(
                    Decimal("1"), rounding=ROUND_HALF_UP
                )
            ),
            "status": "conditional on proposed geometry/conversion; no vehicles placed",
        }
    write_json(output / "audit.json", report)
    receipt.update(
        status="converted_unreviewed",
        network_sha256=digest(output / "network.net.xml"),
        audit_sha256=digest(output / "audit.json"),
        conversion_defaults="SUMO 1.28.0 default OSM typemap; omitted tags may be inferred; static signal timing synthesized, not observed",
    )
    write_json(output / "build.json", receipt)
    return {
        "status": receipt["status"],
        "traffic_ready": False,
        "lane_km": report["lane_km"],
        "passenger_lane_components": report["passenger_lane_graph"]["weak_components"],
        "conditional_initial_road_target": report.get(
            "conditional_initial_road_target"
        ),
    }
