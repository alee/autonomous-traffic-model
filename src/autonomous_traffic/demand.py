"""Materialize the accepted hypothetical benchmark without routing it."""

import platform
from fractions import Fraction

from .randomness import random_stream


def largest_remainder(total, fractions):
    weights = {int(k): Fraction(str(v)) for k, v in fractions.items()}
    if sum(weights.values()) != 1 or any(v < 0 for v in weights.values()):
        raise ValueError("Occupancy fractions must be nonnegative and sum to one")
    counts = {
        k: (total * v).numerator // (total * v).denominator for k, v in weights.items()
    }
    rank = sorted(weights, key=lambda k: (-(total * weights[k] - counts[k]), k))
    for k in rank[: total - sum(counts.values())]:
        counts[k] += 1
    return counts


def relative_us(clock, start):
    def seconds(value):
        h, m, s = map(int, value.split(":"))
        if not (0 <= h <= 167 and 0 <= m < 60 and 0 <= s < 60):
            raise ValueError("Invalid local clock")
        return h * 3600 + m * 60 + s

    return (seconds(clock) - seconds(start)) * 1_000_000


def materialize(config, seed):
    if config["status"] not in {
        "accepted-hypothetical-benchmark",
        "configured-hypothetical-scenario",
    }:
        raise ValueError(
            "Only an accepted benchmark or explicit configured hypothetical variant may be materialized"
        )
    hh = config["households"]
    households, residents, by_household = [], [], {}
    for size_key, count in sorted(hh["size_counts"].items(), key=lambda x: int(x[0])):
        size = int(size_key)
        if size <= 0 or not isinstance(count, int) or count < 0:
            raise ValueError(
                "Household sizes/counts must be positive/nonnegative integers"
            )
        for _ in range(count):
            hid = f"hh-{len(households):05d}"
            ids = [f"resident-{len(residents) + j:05d}" for j in range(size)]
            by_household[hid] = ids
            households.append(
                {
                    "household_id": hid,
                    "resident_ids": ids,
                    "size": size,
                    "origin_access_id": None,
                }
            )
            residents.extend(
                {"person_id": pid, "household_id": hid, "initial_location": "home"}
                for pid in ids
            )
    if (
        len(households) != hh["count"]
        or len(residents) != hh["resident_persons_derived"]
    ):
        raise ValueError("Household and resident totals disagree")
    parties = []
    available = set(by_household)
    party_rng = random_stream(seed, "resident_party_membership")
    demand = config["resident_trips"]
    for size_key, count in sorted(
        demand["party_counts_by_persons"].items(), key=lambda x: -int(x[0])
    ):
        size = int(size_key)
        if (
            size < 1
            or size > config["vehicle_service"]["resident_seat_capacity"]
            or count < 0
        ):
            raise ValueError("Invalid resident party or seat capacity")
        eligible = sorted(hid for hid in available if len(by_household[hid]) >= size)
        if len(eligible) < count:
            raise ValueError("Too few eligible distinct households")
        for hid in party_rng.sample(eligible, count):
            available.remove(hid)
            parties.append((hid, sorted(party_rng.sample(by_household[hid], size))))
    if len(parties) != demand["vehicle_trip_requests_derived"]:
        raise ValueError("Resident request total disagrees")
    if sum(len(p[1]) for p in parties) != demand["persons_derived"]:
        raise ValueError("Resident passenger total disagrees")
    if len(parties) != demand["distinct_departing_households"]:
        raise ValueError("Distinct departing household total disagrees")
    destinations = [
        kind
        for kind, count in sorted(demand["destinations"].items())
        for _ in range(count)
    ]
    windows = [
        window
        for window in demand["departure_vehicle_counts"]
        for _ in range(window["count"])
    ]
    if len(windows) != len(parties) or len(destinations) != len(parties):
        raise ValueError("Departure windows/destination allocation disagree")
    random_stream(seed, "resident_destination_classes").shuffle(destinations)
    random_stream(seed, "resident_departure_windows").shuffle(windows)
    start = config["accepted_context"]["start_local"]
    stop_us = relative_us(config["demand_horizon"]["stop_local"], start)
    time_rng = random_stream(seed, "resident_departure_times")
    trips, service_vehicles = [], []
    for i, ((hid, persons), kind, window) in enumerate(
        zip(parties, destinations, windows)
    ):
        low, high = (
            relative_us(window["from_local"], start),
            relative_us(window["to_local"], start),
        )
        if not 0 <= low < high <= stop_us:
            raise ValueError("Invalid resident departure window")
        vid, tid = f"resident-av-{i:05d}", f"resident-trip-{i:05d}"
        trips.append(
            {
                "trip_id": tid,
                "household_id": hid,
                "person_ids": persons,
                "vehicle_id": vid,
                "departure_elapsed_us": time_rng.randrange(low, high),
                "destination_class": kind,
                "origin_access_id": None,
                "destination_access_id": None,
                "route": None,
            }
        )
        service_vehicles.append(
            {
                "vehicle_id": vid,
                "household_id": hid,
                "seat_capacity": config["vehicle_service"]["resident_seat_capacity"],
                "initial_state": "prepositioned_not_on_road",
                "trip_id": tid,
            }
        )
    if (
        len(service_vehicles)
        != config["vehicle_service"]["resident_prepositioned_vehicle_count"]
    ):
        raise ValueError("Prepositioned vehicle supply disagrees")
    trips.sort(key=lambda t: (t["departure_elapsed_us"], t["trip_id"]))
    external_cfg = config["external_future_arrivals"]
    n_external = sum(w["derived_count"] for w in external_cfg["counts_by_window"])
    if n_external != external_cfg["total_vehicle_requests"]:
        raise ValueError("External arrival total disagrees")
    occupancies = largest_remainder(
        n_external, config["initial_road_loading"]["vehicle_occupancy_fractions"]
    )
    sizes = [k for k, n in sorted(occupancies.items()) for _ in range(n)]
    random_stream(seed, "external_occupancies").shuffle(sizes)
    ext_times = random_stream(seed, "external_departure_times")
    ext_trips, ext_people = [], []
    index = 0
    for window in external_cfg["counts_by_window"]:
        low, high = (
            relative_us(window["from_local"], start),
            relative_us(window["to_local"], start),
        )
        if not 0 <= low < high <= stop_us:
            raise ValueError("Invalid external departure window")
        expected = Fraction(high - low, 3_600_000_000) * Fraction(
            str(window["vehicles_per_hour"])
        )
        if expected != window["derived_count"]:
            raise ValueError("External rates/window counts disagree")
        for _ in range(window["derived_count"]):
            size = sizes[index]
            if size > config["vehicle_service"]["external_vehicle_seat_capacity"]:
                raise ValueError("External occupancy exceeds seats")
            pids = [f"external-person-{len(ext_people) + j:05d}" for j in range(size)]
            ext_people.extend(
                {
                    "person_id": pid,
                    "household_id": None,
                    "initial_location": "outside_context",
                    "resident": False,
                }
                for pid in pids
            )
            ext_trips.append(
                {
                    "trip_id": f"external-trip-{index:05d}",
                    "vehicle_id": f"external-av-{index:05d}",
                    "person_ids": pids,
                    "departure_elapsed_us": ext_times.randrange(low, high),
                    "origin_gateway_id": None,
                    "destination_gateway_id": None,
                    "route": None,
                }
            )
            index += 1
    ext_trips.sort(key=lambda t: (t["departure_elapsed_us"], t["trip_id"]))
    passenger_ids = [pid for t in trips + ext_trips for pid in t["person_ids"]]
    if len(passenger_ids) != len(set(passenger_ids)):
        raise ValueError("Person assigned to multiple requests")
    summary = {
        "status": "materialized_unrouted_hypothetical_demand",
        "execution_ready": False,
        "benchmark_id": config["proposal_id"],
        "seed": seed,
        "randomness": {
            "generator": "Python random.Random (MT19937)",
            "python": platform.python_version(),
            "stream_derivation": "sha256(traffic-demand-v1:<seed>:<stream_name>) interpreted as big-endian integer",
            "time_resolution": "integer microseconds; future engine step alignment requires explicit resolution",
        },
        "households": len(households),
        "resident_persons": len(residents),
        "resident_vehicle_requests": len(trips),
        "resident_travelers": demand["persons_derived"],
        "residents_without_scheduled_departure": len(residents)
        - demand["persons_derived"],
        "prepositioned_resident_vehicles": len(service_vehicles),
        "external_future_requests": len(ext_trips),
        "external_future_persons": len(ext_people),
        "external_occupancy_counts": {
            str(k): v for k, v in sorted(occupancies.items())
        },
        "total_future_vehicle_requests": len(trips) + len(ext_trips),
        "initial_on_road_vehicle_count": None,
        "unresolved": [
            "AOI polygon and extracted lane lengths",
            "origin/destination access and boundary gateways",
            "physical initial road population and prior trip histories",
            "routes, controls and vehicle dynamics",
            "operator assignments and policy-visible observation profiles",
        ],
    }
    return {
        "households": households,
        "residents": residents,
        "resident_trips": trips,
        "resident_service_vehicles": service_vehicles,
        "external_trips": ext_trips,
        "external_people": ext_people,
        "summary": summary,
    }
