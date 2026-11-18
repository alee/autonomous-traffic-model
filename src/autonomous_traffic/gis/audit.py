"""Passenger-lane topology and geometric coverage diagnostics, without automatic repairs."""

import math
from collections import Counter
from pathlib import Path

from ..htc.inputs import xml_root


def clipped_length(shape, box):
    """Liang–Barsky clipping, summed over all polyline segments (metres)."""
    total = 0.0
    for (x, y), (u, v) in zip(shape, shape[1:]):
        dx, dy = u - x, v - y
        lo, hi = 0.0, 1.0
        for p, q in [
            (-dx, x - box[0]),
            (dx, box[2] - x),
            (-dy, y - box[1]),
            (dy, box[3] - y),
        ]:
            if p == 0:
                if q < 0:
                    break
            elif p < 0:
                lo = max(lo, q / p)
            else:
                hi = min(hi, q / p)
            if lo > hi:
                break
        else:
            total += max(0.0, hi - lo) * math.hypot(dx, dy)
    return total


def components(graph, strong=False):
    """Iterative traversal avoids recursion limits for large road graphs."""
    reverse = {k: set() for k in graph}
    for a, values in graph.items():
        for b in values:
            reverse[b].add(a)
    if not strong:
        graph = {k: graph[k] | reverse[k] for k in graph}
    seen = set()
    order = []
    for start in graph:
        if start in seen:
            continue
        seen.add(start)
        stack = [(start, iter(graph[start]))]
        while stack:
            node, neighbours = stack[-1]
            try:
                other = next(neighbours)
                if other not in seen:
                    seen.add(other)
                    stack.append((other, iter(graph[other])))
            except StopIteration:
                order.append(node)
                stack.pop()
    seen = set()
    groups = []
    for start in reversed(order):
        if start in seen:
            continue
        group = []
        stack = [start]
        seen.add(start)
        while stack:
            node = stack.pop()
            group.append(node)
            for other in reverse[node] if strong else graph[node]:
                if other not in seen:
                    seen.add(other)
                    stack.append(other)
        groups.append(sorted(group))
    return sorted(groups, key=lambda g: (-len(g), g[0]))


def audit(network, plan, osm=None):
    try:
        import sumolib
    except ImportError as exc:
        raise ValueError("Network audit requires the optional sumo extra") from exc
    xml_root(Path(network))
    net = sumolib.net.readNet(str(network), withInternal=True)
    import pyproj

    expected_crs = pyproj.CRS(plan["metric_crs"])
    if not expected_crs.equals(
        pyproj.CRS(net.getGeoProj().srs), ignore_axis_order=True
    ):
        raise ValueError("Converted projection does not match the planned metric CRS")
    offset = net.getLocationOffset()
    boxes = {
        name: [
            box[0] + offset[0],
            box[1] + offset[1],
            box[2] + offset[0],
            box[3] + offset[1],
        ]
        for name, box in [("aoi", plan["aoi_xy"]), ("context", plan["context_xy"])]
    }
    lanes = {
        lane.getID(): lane
        for edge in net.getEdges(withInternal=False)
        for lane in edge.getLanes()
        if lane.allows("passenger")
    }
    if not lanes:
        raise ValueError("Converted network has no passenger-permitted external lanes")
    graph = {name: set() for name in lanes}
    lengths = {"retained_network": 0.0, "aoi": 0.0, "context": 0.0}
    anomalies = []
    details = []
    for name, lane in sorted(lanes.items()):
        shape = lane.getShape()
        geom = sum(math.dist(a, b) for a, b in zip(shape, shape[1:]))
        declared = lane.getLength()
        if geom <= 0 or declared <= 0 or not math.isfinite(geom + declared):
            anomalies.append(name)
            continue
        row = {"lane_id": name, "edge_id": lane.getEdge().getID(), "length_m": declared}
        lengths["retained_network"] += declared / 1000
        for role, box in boxes.items():
            inside = declared * clipped_length(shape, box) / geom
            row[role + "_length_m"] = inside
            lengths[role] += inside / 1000
        details.append(row)
        for connection in lane.getOutgoing():
            target = connection.getToLane().getID()
            via = connection.getViaLaneID()
            if target in lanes and (not via or net.getLane(via).allows("passenger")):
                graph[name].add(target)
    edge_graph = {lane.getEdge().getID(): set() for lane in lanes.values()}
    for a, targets in graph.items():
        edge_graph[lanes[a].getEdge().getID()].update(
            lanes[b].getEdge().getID() for b in targets
        )
    edge_weak = components(edge_graph)
    weak, strong = components(graph), components(graph, strong=True)
    incoming = Counter(b for values in graph.values() for b in values)
    report = {
        "schema_version": "1",
        "status": "diagnostics_require_review",
        "traffic_ready": False,
        "geometry_status": plan["geometry_status"],
        "metric_crs": plan["metric_crs"],
        "lane_km": lengths,
        "lane_length_method": "SUMO declared external passenger-lane length allocated by clipped polyline fraction; internal junction lanes excluded",
        "lane_details": details,
        "invalid_geometry_lanes": anomalies,
        "passenger_lane_graph": {
            "vertices": len(graph),
            "arcs": sum(map(len, graph.values())),
            "weak_components": len(weak),
            "strong_components": len(strong),
            "weak_component_sizes": [len(g) for g in weak],
            "largest_strong_component_size": len(strong[0]),
            "lanes_without_incoming": sorted(k for k in graph if not incoming[k]),
            "lanes_without_outgoing": sorted(k for k in graph if not graph[k]),
            "weak_components_lanes": weak,
            "interpretation": "Lane-connection graph; no lane-change arcs. Boundary lanes and terminal lanes are diagnostics, not automatic errors or selected gateways.",
        },
        "passenger_edge_graph": {
            "vertices": len(edge_graph),
            "weak_components": len(edge_weak),
            "weak_component_sizes": [len(g) for g in edge_weak],
            "weak_components_edges": edge_weak,
            "interpretation": "Union of allowed lane connections by edge; does not prove feasible lane changes or origin-destination reachability.",
        },
        "native_tls_count": len(net.getTrafficLights()),
        "limitations": [
            "No topology repair or largest-component pruning performed.",
            "Default typemap and generated native control programs require review; not empirical signal timings.",
            "Geometry/connectivity do not validate speeds, lanes, legal/time-dependent access or routing demand.",
            "AOI is a proposed projected rectangular envelope; retained edges and download padding extend beyond context.",
            "No resident endpoints, routes, physical initialization, controllers or faults are produced.",
        ],
    }
    if osm:
        root = xml_root(Path(osm))
        nodeids = {n.attrib["id"] for n in root.findall("node")}
        ways = root.findall("way")
        highways = []
        missing = []
        for way in ways:
            tags = {t.attrib["k"]: t.attrib["v"] for t in way.findall("tag")}
            missing.extend(
                (way.attrib["id"], n.attrib["ref"])
                for n in way.findall("nd")
                if n.attrib["ref"] not in nodeids
            )
            if "highway" in tags:
                highways.append(tags)
        report["osm_source_audit"] = {
            "nodes": len(nodeids),
            "ways": len(ways),
            "highway_ways": len(highways),
            "relations": len(root.findall("relation")),
            "missing_way_node_refs": missing,
            "highway_ways_without_tags": {
                key: sum(key not in t for t in highways)
                for key in ["lanes", "maxspeed", "oneway"]
            },
            "interpretation": "Absent source tags may trigger converter inference. Missing oneway does not prove two-way access; legal defaults and road types matter.",
        }
    return report
