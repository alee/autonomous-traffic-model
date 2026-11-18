"""Explicit, traceable scenario variants; accounting checks are not scientific approval."""

import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

from .demand import materialize, relative_us

DERIVED = {
    "households.count",
    "households.resident_persons_derived",
    "resident_trips.distinct_departing_households",
    "resident_trips.persons_derived",
    "resident_trips.vehicle_trip_requests_derived",
    "external_future_arrivals.total_vehicle_requests",
    "vehicle_service.resident_prepositioned_vehicle_count",
}


def merge(target, changes, prefix=""):
    for key, value in changes.items():
        name = f"{prefix}.{key}".strip(".")
        if key not in target or name in DERIVED:
            raise ValueError(f"Unknown or derived scenario field: {name}")
        if isinstance(value, dict) and isinstance(target[key], dict):
            # Histograms are complete replacements, so obsolete categories cannot survive.
            if name in {
                "households.size_counts",
                "resident_trips.party_counts_by_persons",
                "initial_road_loading.vehicle_occupancy_fractions",
            }:
                target[key] = copy.deepcopy(value)
            else:
                merge(target[key], value, name)
        else:
            target[key] = copy.deepcopy(value)


def configure(base, output, overrides=None, start_local=None):
    base, output = Path(base), Path(output)
    if output.exists():
        raise ValueError("Use a fresh scenario output; the base is never overwritten")
    raw = base.read_bytes()
    config = json.loads(raw)
    if config["status"] not in {
        "accepted-hypothetical-benchmark",
        "configured-hypothetical-scenario",
    }:
        raise ValueError("A hypothetical benchmark/scenario is required")
    before = config["accepted_context"]["start_local"]
    shift = 0
    if start_local is not None:
        # Scenario starts are ordinary local clocks; future endpoints may use 24+ service hours.
        start_seconds = relative_us(start_local, "00:00:00") // 1_000_000
        if not 0 <= start_seconds < 86400:
            raise ValueError("Start must be a local clock within one day")
        shift = relative_us(start_local, before) // 1_000_000

        def move(value):
            seconds = relative_us(value, "00:00:00") // 1_000_000 + shift
            if seconds < 0:
                raise ValueError("Shift would move an endpoint before the service day")
            h, rest = divmod(seconds, 3600)
            m, s = divmod(rest, 60)
            return f"{h:02d}:{m:02d}:{s:02d}"

        for group in [
            config["resident_trips"]["departure_vehicle_counts"],
            config["external_future_arrivals"]["counts_by_window"],
        ]:
            for window in group:
                for key in ["from_local", "to_local"]:
                    window[key] = move(window[key])
        for key, value in config["demand_horizon"].items():
            if value is not None:
                config["demand_horizon"][key] = move(value)
        config["accepted_context"]["start_local"] = start_local
    patch_raw = Path(overrides).read_bytes() if overrides else b"{}"
    patch = json.loads(patch_raw)
    if not isinstance(patch, dict) or any(
        k in patch
        for k in [
            "status",
            "acceptance",
            "parameterization",
            "execution_ready",
            "evidence_class",
        ]
    ):
        raise ValueError(
            "Overrides must be scenario inputs, not readiness/approval metadata"
        )
    if "start_local" in patch.get("accepted_context", {}):
        raise ValueError(
            "Use --start-local to shift the complete schedule consistently"
        )
    merge(config, patch)
    hh, trips = config["households"], config["resident_trips"]
    for histogram in [hh["size_counts"], trips["party_counts_by_persons"]]:
        if not histogram or any(
            not str(k).isdigit() or int(k) < 1 or type(v) is not int or v < 0
            for k, v in histogram.items()
        ):
            raise ValueError(
                "Histogram sizes/counts must be positive/nonnegative integers"
            )
    hh["count"] = sum(hh["size_counts"].values())
    hh["resident_persons_derived"] = sum(
        int(k) * v for k, v in hh["size_counts"].items()
    )
    n = sum(trips["party_counts_by_persons"].values())
    trips["vehicle_trip_requests_derived"] = trips["distinct_departing_households"] = n
    trips["persons_derived"] = sum(
        int(k) * v for k, v in trips["party_counts_by_persons"].items()
    )
    config["vehicle_service"]["resident_prepositioned_vehicle_count"] = n
    ext = config["external_future_arrivals"]
    for w in ext["counts_by_window"]:
        hours = Fraction(relative_us(w["to_local"], w["from_local"]), 3_600_000_000)
        number = hours * Fraction(str(w["vehicles_per_hour"]))
        if hours <= 0 or number < 0 or number.denominator != 1:
            raise ValueError(
                "External rates and windows must produce nonnegative integer counts"
            )
        w["derived_count"] = int(number)
    ext["total_vehicle_requests"] = sum(
        w["derived_count"] for w in ext["counts_by_window"]
    )
    density = config["initial_road_loading"]["target"]
    if type(density) not in (float, int) or not math.isfinite(density) or density < 0:
        raise ValueError("Road loading must be finite and nonnegative")
    start = config["accepted_context"]["start_local"]
    stop, end = (
        relative_us(config["demand_horizon"][k], start)
        for k in ["stop_local", "end_local"]
    )
    if not 0 < stop <= end:
        raise ValueError("Require start < demand stop <= run end")
    analysis = config["demand_horizon"]["analysis_start_local"]
    if analysis is not None and not 0 <= relative_us(analysis, start) <= stop:
        raise ValueError("Analysis start must lie between start and demand stop")
    config["status"] = "configured-hypothetical-scenario"
    config["evidence_class"] = "hypothetical"
    config["execution_ready"] = False
    config.pop("acceptance", None)
    config["parameterization"] = {
        "base_sha256": hashlib.sha256(raw).hexdigest(),
        "overrides_sha256": hashlib.sha256(patch_raw).hexdigest(),
        "start_shift_s": shift,
        "review": "configured variant; accounting validation does not imply scientific approval",
    }
    materialize(config, 0)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(config, indent=2, allow_nan=False) + "\n")
    return {
        "output": str(output),
        "status": config["status"],
        "start_local": start,
        "demand_stop_elapsed_s": stop / 1e6,
        "run_end_elapsed_s": end / 1e6,
        "road_density_vehicles_per_lane_km": density,
    }
