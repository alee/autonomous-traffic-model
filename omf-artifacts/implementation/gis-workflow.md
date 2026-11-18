# Parameterized scenarios and GIS preparation

OMFB · 2026-11-17 · implemented preparation slice; geographic proposal unreviewed

The clock, household composition, passenger occupancy, road-loading target and demand windows live in scenario JSON. **03:00 is a benchmark value, not a runtime constant.** The accepted benchmark remains a preserved baseline; parameterized variants have their own content identity and configured/unreviewed status. GIS preparation is separate from actor placement and HTC workers.

## Configure a scenario

```sh
uv sync --locked --extra sumo --extra geo
uv run --locked --extra sumo --extra geo autonomous-traffic scenario-configure --base omf-artifacts/implementation/scenarios/coronado-benchmark.json --start-local 04:00:00 --overrides omf-artifacts/implementation/gis/scenario-overrides.example.json --output runs/scenario-0400.json
```

`--start-local` shifts all resident/external departure windows, demand stop, run end and any analysis start by the same offset. Durations and generated elapsed trip times are preserved for a fixed seed. It changes clock labels; it does not infer different traffic volumes for a different hour. To study time-of-day changes, explicitly supply different demand windows/rates too. Start uses a local HH:MM:SS clock within a day. Future endpoints use service-day hours above 23 for midnight rollover: a 22:00 start moves the baseline stop/end to 29:00/30:00 (05:00/06:00 next day). The parser supports up to 167:59:59 as an implementation guard. No dated timezone/DST/UTC conversion is performed.

The optional overrides file contains ordinary nested JSON fields from the baseline. Histograms replace the entire old histogram, including removed categories. Lists, such as time windows, replace the entire list. Unknown mapping keys, direct overrides of the listed derived totals, and approval/readiness metadata are rejected. A clock-start edit in the overrides is rejected; use the schedule-shifting flag.

Editable input examples:

| Inputs | Validation / derivation |
|---|---|
| `households.size_counts` | Derive household and resident totals; retain feasible distinct-household party assignment |
| `resident_trips.party_counts_by_persons` | Derive vehicle requests, travelers and parked service supply; explicit departure/destination counts must still sum to requests |
| `initial_road_loading.target` | Finite nonnegative vehicles per eligible lane-km; no physical placement is implied |
| `initial_road_loading.vehicle_occupancy_fractions` | Full replacement; nonnegative fractions sum to one and respect external seat capacity |
| `external_future_arrivals.counts_by_window` | From/to clocks and vehicles/hour determine integer derived counts; fractional vehicles are rejected |
| `candidate_aoi.context_buffer_m` | Explicit scenario context; pass the variant to `network-plan --benchmark` to use it |
| `demand_horizon` and resident departure windows | Explicit horizon consistency and request-accounting checks; no automatic profile rescaling |

The effective file includes base/override digests and shift magnitude. Its status is `configured-hypothetical-scenario`, execution readiness stays false, and the original acceptance record is not inherited as approval of a new variant. `materialize --config runs/scenario-0400.json ...` can generate its unrouted demand. Accounting validation does not establish scientific adequacy. Changing household or request histograms can require matching explicit windows/destinations; errors are reported rather than silently balancing them.

## Prepare and acquire a network

```sh
uv run --locked --extra sumo --extra geo autonomous-traffic network-plan --config omf-artifacts/implementation/gis/coronado-network.proposed.json --benchmark runs/scenario-0400.json --output runs/network-plan
uv run --locked --extra sumo --extra geo autonomous-traffic network-fetch --plan runs/network-plan/plan.json --output runs/network-source
uv run --locked --extra sumo --extra geo autonomous-traffic network-build --plan runs/network-plan/plan.json --source runs/network-source --benchmark runs/scenario-0400.json --output runs/network-build
```

Use a fresh directory for each attempt. Fetching occurs only through the explicit preparation command. All conversion/audit work thereafter is offline; HTC workers neither download GIS nor import pyproj. If an OSM export is already available, `network-import --osm FILE --bbox=WEST,SOUTH,EAST,NORTH --source-uri URL --output DIR` records it for offline use. The supplied bbox is the original requested source coverage; it is an acquisition assertion, not a completeness guarantee.

The geometry configuration currently supports a WGS84 rectangular AOI and an explicit metric projected CRS. For Coronado, EPSG:32612 (UTM zone 12N) supports metre measurements. AOI corner coordinates are projected into an axis-aligned metric envelope; context expands that envelope on each side. This is a documented rectangular approximation, not an exact named-road polygon or a rounded polygon buffer. The supplied Coronado proposal derives its candidate coordinates from downloaded OSM road intersections; divided carriageways and curved road boundaries need review. It does not fill or replace the benchmark's null accepted polygon.

`network-plan --benchmark` takes context margin from that scenario, recording its digest. Without a benchmark, it uses the explicit GIS configuration margin. `network-build --benchmark` rejects inconsistent context margins. The 100 m download margin is topology padding, separate from the reporting context. Overpass queries request highway ways, restriction relations and referenced geometry. Query footprint (0.01 square degrees), response size (32 MiB) and timeouts are initial preparation guards, not service quotas or scientific AOI limits. Larger extents need a deliberate offline-extract extension. Partial responses containing Overpass remarks/errors are rejected.

## Conversion and audit

SUMO 1.28.0 converts the recorded source with an explicit projection and clipping request. Ramp guessing, signal guessing, junction joining and geometry simplification are disabled. The installed default OSM typemap can still infer lanes, speeds and access from road type. Existing signal locations can produce synthesized static programs; these are not observed Phoenix signal timings. Retain converter warnings for review. No largest-component pruning or road deletion is used as an audit repair.

The audit records passenger-permitted external lane lengths, excluding internal junction lanes. Length inside AOI/context is the declared SUMO lane length multiplied by the fraction of its polyline inside the projected box. It also reports total retained-network lane-km, since full edge tails and download padding can extend beyond context. It records lane-connection components, an edge-level union of those connections, missing source node references, absent lane/speed/oneway tags, geometry anomalies and native signal counts. Lane topology omits lane-change arcs; edge aggregation does not prove feasible lane changes or complete origin–destination reachability. Dead ends and separate components are diagnostics, not automatic errors or declared gateways.

An optional benchmark yields a **conditional** initial vehicle count by its density × context lane-km, rounded half up. This is not physical initialization: it supplies no vehicle positions, histories, routes, occupancy assignments or overlap resolution. The result remains unready even when conversion succeeds.

## Current data and limits

See [GIS verification](gis-verification-report.md). The downloaded OSM snapshot and converted network are retained locally under `runs/coronado-gis/`; reviewed acquisition metadata, compact audit summaries, plan and logs are under `gis-verification/`. Raw inputs and large derived files are ignored by Git. Preserve/archive their exact bytes and licensing with any distributed study; re-querying Overpass retrieves a changing dataset.

Before using the network for traffic: review the proposed boundary and conversion warnings, legal/access/direction and control assumptions, disconnected components and the eligible road inventory. Resolve household access, gateways, complete routes, physical 03:00 occupancy and histories, and tested operator/policy/fault adapters. Existing HTC fixture evidence predates this source extension and remains scoped to its recorded code fingerprint; rebuild the worker image for new package source.

Primary implementation references: [SUMO OSM import](https://sumo.dlr.de/docs/Networks/Import/OpenStreetMap.html), [pyproj](https://pyproj4.github.io/pyproj/stable/), [OSM attribution](https://www.openstreetmap.org/copyright), and [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/). These support import/projection/stewardship mechanics, not completeness or empirical traffic validity.
