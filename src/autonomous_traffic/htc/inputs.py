"""Prepared, immutable SUMO inputs; GIS conversion and scientific review precede jobs."""

import gzip
import hashlib
import json
import math
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

MAX_INPUT_BYTES = 256 * 1024 * 1024


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def code_digest():
    root = Path(__file__).resolve().parents[1]
    return hashlib.sha256(
        canonical(
            {
                p.relative_to(root).as_posix(): digest(p)
                for p in sorted(root.rglob("*.py"))
            }
        )
    ).hexdigest()


def relative_path(value):
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or any(x in value for x in [",", "\n", "\r"])
    ):
        raise ValueError("Input paths must be nonempty portable relative paths")
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts or ":" in value:
        raise ValueError(f"Input path escapes bundle: {value}")
    return value


def xml_root(path):
    data = path.read_bytes()
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("Prepared XML may not contain DTDs or entities")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid prepared XML {path.name}: {exc}") from exc
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] == "include":
            raise ValueError("Expand XML includes before packaging inputs")
        for key, value in node.attrib.items():
            if key.lower() in {"file", "href"}:
                relative_path(value)
    return root


def assets(case):
    result = [
        case["network"],
        case["request_ledger"],
        *case["routes"],
        *case["additional"],
    ]
    if case["initialization"]["mode"] == "fresh_sumo_state":
        result.append(case["initialization"]["state"])
    return result


def validate_case(path):
    path = Path(path).resolve()
    case = json.loads(path.read_text())
    if case["schema_version"] != "1" or case["backend"] != "sumo-native":
        raise ValueError("Only prepared sumo-native case format 1 is supported")
    if case["purpose"] not in {"engineering_fixture", "traffic_experiment"}:
        raise ValueError("Declare the case purpose")
    if case["purpose"] == "traffic_experiment" and case["review_status"] != "accepted":
        raise ValueError("Traffic cases require accepted scientific preparation/review")
    if not isinstance(case["parameters"], dict) or any(
        type(v) not in (str, bool, int, float) for v in case["parameters"].values()
    ):
        raise ValueError("Prepared parameter cells must contain concrete scalar values")
    canonical(case["parameters"])
    sim = case["simulation"]
    for key in [
        "begin_s",
        "end_s",
        "step_length_s",
        "time_to_teleport_s",
        "collision_min_gap_factor",
    ]:
        if type(sim[key]) not in (int, float) or not math.isfinite(sim[key]):
            raise ValueError(f"Invalid simulation number: {key}")
    if not 0 <= sim["begin_s"] < sim["end_s"] or sim["step_length_s"] <= 0:
        raise ValueError("Invalid simulation horizon or step")
    if sim["time_to_teleport_s"] != -1 or sim["collision_action"] != "warn":
        raise ValueError(
            "This backend requires explicit no-teleport/warn-only accounting; other collision aftermath needs an adapter"
        )
    if (
        not isinstance(sim["check_junction_collisions"], bool)
        or sim["collision_min_gap_factor"] < 0
    ):
        raise ValueError("Invalid collision observation settings")
    steps = (sim["end_s"] - sim["begin_s"]) / sim["step_length_s"]
    if abs(steps - round(steps)) > 1e-8:
        raise ValueError(
            "Simulation horizon must align with the explicitly selected step"
        )
    if case["engine_version"] != "1.28.0":
        raise ValueError("The initial tested worker targets SUMO 1.28.0")
    declared = {}
    for item in assets(case):
        rel = relative_path(item["path"])
        candidate = path.parent / rel
        if (
            candidate.is_symlink()
            or not candidate.is_file()
            or not candidate.resolve().is_relative_to(path.parent)
        ):
            raise ValueError(f"Missing/nonportable input: {rel}")
        if rel in declared and declared[rel] != item["sha256"]:
            raise ValueError("Conflicting input digests")
        if digest(candidate) != item["sha256"]:
            raise ValueError(f"Input digest mismatch: {rel}")
        declared[rel] = item["sha256"]
    if sum((path.parent / p).stat().st_size for p in declared) > MAX_INPUT_BYTES:
        raise ValueError(
            "Input bundle exceeds direct-transfer budget; design OSDF staging before scaling"
        )
    if not case["routes"]:
        raise ValueError("Explicit route inputs are required")
    roots = {p: xml_root(path.parent / p) for p in declared if p.endswith(".xml")}
    if (
        case["network"]["path"] not in roots
        or roots[case["network"]["path"]].tag != "net"
    ):
        raise ValueError("Provide a converted SUMO .net.xml, not raw GIS")
    ledger = json.loads((path.parent / case["request_ledger"]["path"]).read_text())
    requests = {}
    for row in ledger:
        vid = row["vehicle_id"]
        if not isinstance(vid, str) or not vid or vid in requests:
            raise ValueError("Duplicate/invalid request vehicle ID")
        count, when = row["person_count"], row["request_time_s"]
        if type(count) is not int or count < 0 or not isinstance(row["initial"], bool):
            raise ValueError("Invalid passenger count or initial flag")
        if (
            type(when) not in (int, float)
            or not math.isfinite(when)
            or when >= sim["end_s"]
        ):
            raise ValueError("Request time is outside declared horizon")
        if when < sim["begin_s"] and not row["initial"]:
            raise ValueError("Pre-horizon requests need explicit initial state/history")
        requests[vid] = row
    route_ids = set()
    for item in case["routes"]:
        root = roots.get(item["path"])
        if (
            root is None
            or root.tag != "routes"
            or root.findall("flow")
            or root.findall("trip")
            or root.findall("personFlow")
        ):
            raise ValueError(
                "Materialize explicit vehicle routes before job submission; flows/trips are unsupported"
            )
        for node in root.findall("vehicle"):
            if node.attrib["id"] in route_ids:
                raise ValueError("Duplicate routed vehicle")
            route_ids.add(node.attrib["id"])
    init = case["initialization"]
    if init["mode"] == "explicit_empty_fixture":
        if case["purpose"] != "engineering_fixture" or any(
            r["initial"] for r in ledger
        ):
            raise ValueError("Empty starts are restricted to engineering fixtures")
        state_ids = set()
    elif init["mode"] == "fresh_sumo_state":
        state = roots[init["state"]["path"]]
        if state.tag != "snapshot" or float(state.attrib["time"]) != sim["begin_s"]:
            raise ValueError("Initial state time does not match case begin")
        if any(n.tag.startswith("rng") for n in state.iter()):
            raise ValueError(
                "Fresh replicated initialization must not restore old RNG state; exact continuation is a separate contract"
            )
        state_ids = {n.attrib["id"] for n in state.findall("vehicle")}
        if state_ids != {r["vehicle_id"] for r in ledger if r["initial"]}:
            raise ValueError("Initial vehicle ledger does not match prepared state")
    else:
        raise ValueError("Unsupported physical initialization mode")
    if route_ids | state_ids != set(requests):
        raise ValueError(
            "Declared route/state IDs must exactly match the request ledger"
        )
    bindings = case["parameter_bindings"]
    if set(bindings) != set(case["parameters"]):
        raise ValueError("Every swept parameter must bind to a prepared XML attribute")
    for key, binding in bindings.items():
        root = roots.get(binding["path"])
        nodes = [] if root is None else root.findall(binding["xpath"])
        if not nodes:
            raise ValueError(f"Unresolved parameter binding: {key}")
        expected = case["parameters"][key]
        for node in nodes:
            actual = node.attrib[binding["attribute"]]
            if isinstance(expected, bool):
                equal = actual.lower() == str(expected).lower()
            elif isinstance(expected, (int, float)):
                equal = float(actual) == expected
            else:
                equal = actual == str(expected)
            if not equal:
                raise ValueError(f"Parameter binding mismatch: {key}")
    for key in [
        "gis_source",
        "initial_parameterization",
        "scope",
        "input_realization_id",
    ]:
        if not case["provenance"].get(key):
            raise ValueError(f"Missing input provenance: {key}")
    return case, requests, declared


def bundle_case(source, destination):
    source = Path(source)
    case, _, files = validate_case(source)
    with (
        Path(destination).open("wb") as raw,
        gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed,
    ):
        with tarfile.open(fileobj=compressed, mode="w") as archive:
            for src, rel in [
                (source, "case.json"),
                *((source.parent / p, p) for p in sorted(files)),
            ]:
                info = archive.gettarinfo(str(src), arcname=rel)
                info.mtime = info.uid = info.gid = 0
                info.uname = info.gname = ""
                info.mode = 0o444
                with src.open("rb") as data:
                    archive.addfile(info, data)
    return case


def unpack_bundle(bundle, target):
    target.mkdir()
    with tarfile.open(bundle, "r:gz") as archive:
        members = archive.getmembers()
        if (
            len({m.name for m in members}) != len(members)
            or sum(m.size for m in members) > MAX_INPUT_BYTES
        ):
            raise ValueError("Invalid or oversized input archive")
        for member in members:
            relative_path(member.name)
            if not member.isfile():
                raise ValueError("Only regular files are accepted in input archives")
            dest = target / member.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as source, dest.open("wb") as output:
                while block := source.read(1024 * 1024):
                    output.write(block)
    return target / "case.json"
