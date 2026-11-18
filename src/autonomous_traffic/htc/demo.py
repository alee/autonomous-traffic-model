"""Small synthetic grid for local HTC workflow validation, separate from Phoenix."""

import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from .inputs import digest
from .plan import write_json


def create_demo(output, netgenerate=None):
    import sumolib

    output = Path(output).resolve()
    if output.exists():
        raise ValueError("Use a new demo input directory")
    binary = netgenerate or shutil.which("netgenerate")
    if not binary:
        raise ValueError("The demo requires the optional SUMO tools")
    output.mkdir(parents=True)
    network = output / "grid.net.xml"
    subprocess.run(
        [
            binary,
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
    paths = []
    for first in net.getEdges():
        for last in net.getEdges():
            route, cost = net.getShortestPath(first, last)
            if route and len(route) >= 4:
                paths.append((cost, tuple(e.getID() for e in route)))
    route = max(paths)[1]
    cases = []
    for speed in [8.0, 12.0]:
        for headway in [1.0, 1.5]:
            name = f"speed-{int(speed)}-tau-{str(headway).replace('.', 'p')}"
            folder = output / name
            folder.mkdir()
            shutil.copyfile(network, folder / "network.net.xml")
            root = ET.Element("routes")
            ET.SubElement(
                root,
                "vType",
                id="probe",
                maxSpeed=str(speed),
                tau=str(headway),
                sigma="0.1",
                accel="2",
                decel="4.5",
                length="5",
                minGap="2.5",
            )
            ET.SubElement(root, "route", id="r", edges=" ".join(route))
            ledger = []
            for index, (departure, persons) in enumerate([(0, 2), (4, 0), (155, 1)]):
                vid = f"vehicle-{index}"
                ET.SubElement(
                    root,
                    "vehicle",
                    id=vid,
                    type="probe",
                    route="r",
                    depart=str(departure),
                )
                ledger.append(
                    {
                        "vehicle_id": vid,
                        "person_count": persons,
                        "request_time_s": departure,
                        "initial": False,
                    }
                )
            ET.indent(root)
            ET.ElementTree(root).write(
                folder / "routes.xml", encoding="utf-8", xml_declaration=True
            )
            write_json(folder / "requests.json", ledger)

            def asset(p):
                return {"path": p, "sha256": digest(folder / p)}

            case = {
                "schema_version": "1",
                "case_id": name,
                "backend": "sumo-native",
                "purpose": "engineering_fixture",
                "review_status": "engineering_fixture",
                "engine_version": "1.28.0",
                "parameters": {
                    "vehicle_max_speed_mps": speed,
                    "following_headway_s": headway,
                },
                "parameter_bindings": {
                    "vehicle_max_speed_mps": {
                        "path": "routes.xml",
                        "xpath": ".//vType[@id='probe']",
                        "attribute": "maxSpeed",
                    },
                    "following_headway_s": {
                        "path": "routes.xml",
                        "xpath": ".//vType[@id='probe']",
                        "attribute": "tau",
                    },
                },
                "network": asset("network.net.xml"),
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
                    "gis_source": "synthetic netgenerate grid; no Phoenix GIS",
                    "initial_parameterization": "engineering fixture only; not the accepted Coronado initialization",
                    "scope": "3x3 grid; empty start explicitly restricted to fixture",
                    "input_realization_id": "three-fixed-vehicle-requests-v1",
                },
            }
            write_json(folder / "case.json", case)
            cases.append(f"{name}/case.json")
    sweep = {
        "schema_version": "1",
        "sweep_id": "headless-fixture",
        "cases": cases,
        "axes": {
            "vehicle_max_speed_mps": [8.0, 12.0],
            "following_headway_s": [1.0, 1.5],
        },
        "replicates": 2,
        "base_seed": 20261117,
        "seed_scope": "sumo_engine_only",
        "resources": {
            "cpus": 1,
            "memory_mb": 2048,
            "disk_mb": 4096,
            "wall_time_s": 3600,
        },
    }
    write_json(output / "sweep.json", sweep)
    return {
        "sweep": str(output / "sweep.json"),
        "case_count": 4,
        "task_count": 8,
        "purpose": "engineering_fixture",
    }
