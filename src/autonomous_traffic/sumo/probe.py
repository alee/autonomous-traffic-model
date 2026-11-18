"""SUMO checkpoint engineering fixture; not a Phoenix traffic simulation."""

import hashlib
import importlib.metadata
import json
import random
import subprocess
import xml.etree.ElementTree as ET


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tuples(value):
    return tuple(tuples(x) for x in value) if isinstance(value, list) else value


def probe(output, sumo, netgenerate):
    import sumolib
    import traci

    output.mkdir(parents=True, exist_ok=True)
    network = output / "fixture.net.xml"
    subprocess.run(
        [
            netgenerate,
            "--grid",
            "--grid.number",
            "3",
            "--grid.length",
            "120",
            "--tls.set",
            "B1",
            "--no-turnarounds",
            "true",
            "--output-file",
            str(network),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    net = sumolib.net.readNet(str(network))
    edges = sorted(net.getEdges(), key=lambda e: e.getID())
    possibilities = []
    for first in edges:
        for last in edges:
            path, cost = net.getShortestPath(first, last)
            if path and len(path) >= 4:
                possibilities.append((cost, tuple(e.getID() for e in path)))
    _, selected = max(possibilities)
    lane = selected[0] + "_0"
    routes = output / "fixture.rou.xml"
    xml = ET.Element("routes")
    ET.SubElement(
        xml,
        "vType",
        id="fixtureCar",
        accel="2",
        decel="4.5",
        emergencyDecel="9",
        sigma="0",
        tau="1",
        length="5",
        minGap="2.5",
        maxSpeed="10",
        personCapacity="4",
        carFollowModel="Krauss",
    )
    ET.SubElement(xml, "route", id="route", edges=" ".join(selected))
    car = ET.SubElement(
        xml, "vehicle", id="car0", type="fixtureCar", route="route", depart="0"
    )
    ET.SubElement(
        car,
        "stop",
        lane=lane,
        endPos="10",
        duration="2",
        triggered="true",
        expected="rider0",
    )
    person = ET.SubElement(xml, "person", id="rider0", depart="0", departPos="10")
    ET.SubElement(
        person, "ride", **{"from": selected[0], "to": selected[-1], "lines": "car0"}
    )
    ET.SubElement(
        xml, "vehicle", id="car1", type="fixtureCar", route="route", depart="3"
    )
    parked = ET.SubElement(
        xml, "vehicle", id="parked", type="fixtureCar", route="route", depart="6"
    )
    ET.SubElement(parked, "stop", lane=lane, endPos="40", duration="80", parking="true")
    ET.SubElement(
        xml, "vehicle", id="future", type="fixtureCar", route="route", depart="90"
    )
    ET.indent(xml)
    ET.ElementTree(xml).write(routes, encoding="utf-8", xml_declaration=True)
    packages = {
        name: importlib.metadata.version(name)
        for name in ["eclipse-sumo", "traci", "sumolib", "sumo-data"]
    }
    inputs = {
        "network_sha256": digest(network),
        "routes_sha256": digest(routes),
        "packages": packages,
    }
    common = [
        sumo,
        "--net-file",
        str(network),
        "--route-files",
        str(routes),
        "--step-length",
        "0.5",
        "--seed",
        "42",
        "--save-state.rng",
        "true",
        "--save-state.transportables",
        "true",
        "--save-state.precision",
        "17",
        "--time-to-teleport",
        "-1",
        "--collision.action",
        "warn",
        "--collision.check-junctions",
        "true",
        "--no-step-log",
        "true",
        "--duration-log.disable",
        "true",
    ]
    cuts = [30.0, 60.0]

    def launch(resume=None):
        args = common[:]
        rng = random.Random(731)
        state = {
            "messages": [{"deliver_at": 65, "message_id": "m0"}],
            "reservations": [{"vehicle": "car0", "until": 70}],
            "delivered": [],
            "fault": {"active": False, "started": False, "ended": False},
            "departed": [],
            "arrived": [],
            "random_counter": 0,
            "random_sum": 0,
            "last_observation": None,
        }
        if resume is not None:
            saved = json.loads((output / f"adapter-{resume:g}.json").read_text())
            if saved["inputs"] != inputs:
                raise ValueError("Checkpoint input/package mismatch")
            state = saved["adapter"]
            rng.setstate(tuples(saved["rng_state"]))
            args += [
                "--load-state",
                str(output / f"state-{resume:g}.xml"),
                "--begin",
                str(resume),
            ]
        traci.start(args, verbose=False)
        trace = []
        try:
            while traci.simulation.getTime() < 160:
                now = traci.simulation.getTime()
                if now in cuts and resume is None:
                    traci.simulation.saveState(str(output / f"state-{now:g}.xml"))
                    (output / f"adapter-{now:g}.json").write_text(
                        json.dumps(
                            {
                                "time": now,
                                "inputs": inputs,
                                "adapter": state,
                                "rng_state": rng.getstate(),
                            },
                            sort_keys=True,
                        )
                        + "\n"
                    )
                cars = traci.vehicle.getIDList()
                if now >= 15 and not state["fault"]["started"] and "car1" in cars:
                    traci.vehicle.slowDown("car1", 0, 5)
                    state["fault"].update(started=True, active=True)
                if (
                    now >= 40
                    and state["fault"]["started"]
                    and not state["fault"]["ended"]
                ):
                    if "car1" in cars:
                        traci.vehicle.setSpeed("car1", -1)
                    state["fault"].update(active=False, ended=True)
                state["delivered"].extend(
                    m["message_id"] for m in state["messages"] if m["deliver_at"] <= now
                )
                state["messages"] = [
                    m for m in state["messages"] if m["deliver_at"] > now
                ]
                state["reservations"] = [
                    r for r in state["reservations"] if r["until"] > now
                ]
                state["random_counter"] += 1
                state["random_sum"] += rng.randrange(10_000)
                traci.simulationStep()
                state["departed"].extend(traci.simulation.getDepartedIDList())
                state["arrived"].extend(traci.simulation.getArrivedIDList())
                vehicles = {
                    vid: {
                        "position": traci.vehicle.getPosition(vid),
                        "speed": traci.vehicle.getSpeed(vid),
                        "road": traci.vehicle.getRoadID(vid),
                        "lane_position": traci.vehicle.getLanePosition(vid),
                        "route_index": traci.vehicle.getRouteIndex(vid),
                        "persons": traci.vehicle.getPersonIDList(vid),
                        "stop_state": traci.vehicle.getStopState(vid),
                    }
                    for vid in sorted(traci.vehicle.getIDList())
                }
                persons = {
                    pid: {
                        "position": traci.person.getPosition(pid),
                        "vehicle": traci.person.getVehicle(pid),
                        "stage": traci.person.getStage(pid).type,
                    }
                    for pid in sorted(traci.person.getIDList())
                }
                lights = {
                    lid: {
                        "phase": traci.trafficlight.getPhase(lid),
                        "next_switch": traci.trafficlight.getNextSwitch(lid),
                        "state": traci.trafficlight.getRedYellowGreenState(lid),
                    }
                    for lid in traci.trafficlight.getIDList()
                }
                state["last_observation"] = {
                    "time": traci.simulation.getTime(),
                    "vehicle_ids": sorted(vehicles),
                }
                record = {
                    "time": traci.simulation.getTime(),
                    "vehicles": vehicles,
                    "persons": persons,
                    "lights": lights,
                    "adapter": copy_state(state),
                    "collision_count": traci.simulation.getCollidingVehiclesNumber(),
                }
                trace.append(json.loads(json.dumps(record, sort_keys=True)))
        finally:
            traci.close()
        return trace

    baseline = launch()
    checks = []
    for cut in cuts:
        resumed = launch(cut)
        expected = [r for r in baseline if r["time"] > cut]
        equal = resumed == expected
        first = None
        if not equal:
            for a, b in zip(resumed, expected):
                if a != b:
                    first = {
                        "time": a["time"],
                        "different_sections": [key for key in a if a[key] != b[key]],
                    }
                    break
            if first is None:
                first = {"lengths": [len(resumed), len(expected)]}
        (output / f"resumed-{cut:g}.json").write_text(
            json.dumps(resumed, indent=2) + "\n"
        )
        checks.append(
            {
                "checkpoint_time_s": cut,
                "samples_compared": len(expected),
                "exact_observed_trace_match": equal,
                "first_difference": first,
            }
        )
    (output / "uninterrupted.json").write_text(json.dumps(baseline, indent=2) + "\n")
    coverage = {
        "rider_carried": any(
            "rider0" in v["persons"]
            for row in baseline
            for v in row["vehicles"].values()
        ),
        "parked_vehicle": any(
            v["stop_state"] & 2 for row in baseline for v in row["vehicles"].values()
        ),
        "future_vehicle_departed": any(
            "future" in row["adapter"]["departed"] for row in baseline
        ),
        "active_fault_at_first_checkpoint": json.loads(
            (output / "adapter-30.json").read_text()
        )["adapter"]["fault"]["active"],
        "inflight_message_at_both_checkpoints": all(
            json.loads((output / f"adapter-{cut:g}.json").read_text())["adapter"][
                "messages"
            ]
            for cut in cuts
        ),
        "reservation_at_both_checkpoints": all(
            json.loads((output / f"adapter-{cut:g}.json").read_text())["adapter"][
                "reservations"
            ]
            for cut in cuts
        ),
        "traffic_light_present": any(row["lights"] for row in baseline),
    }
    result = {
        "status": "fixture_only_not_phoenix_validation",
        "packages": packages,
        "inputs": inputs,
        "coverage": coverage,
        "checks": checks,
        "all_observed_checks_pass": all(c["exact_observed_trace_match"] for c in checks)
        and all(coverage.values()),
        "limits": [
            "single synthetic grid and simple explicit dynamics",
            "same Linux platform and engine build",
            "observed traces and adapter state compared; unobserved engine state not proved complete",
            "no collision/safety validity or Phoenix performance claim",
        ],
    }
    (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["all_observed_checks_pass"] else 1


def copy_state(value):
    return json.loads(json.dumps(value))
