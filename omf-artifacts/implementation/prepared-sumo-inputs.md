# Prepared GIS, initial state and parameter case contract

Version: 0.1 | Date: 2026-11-17 | Authority: OMFB | Status: implemented native-input contract

## Input handoff

The headless runtime consumes a directory containing case.json and immutable relative input files. It expects a SUMO .net.xml already converted from appropriate GIS, explicit vehicle route files, optional native additional/control XML, a JSON request ledger and, for a traffic experiment, a fresh physical initial-state snapshot. GIS conversion/topology/turn/lane/coordinate audits and scientific initialization are upstream responsibilities. Raw OSM, shapefiles or GeoPackages cannot simply be relabeled as a runnable SUMO network.

`htc-demo` emits complete engineering examples of the format, including sweep.json. These are executable syntax/engine fixtures, not real GIS, calibrated traffic, or substitutes for the accepted 03:00 Coronado state. The active accepted benchmark JSON remains unchanged and is not yet a prepared traffic case.

## case.json fields

| Field | Contract |
|---|---|
| schema_version / backend | `1` / `sumo-native` |
| case_id | Unique portable lowercase letters/digits/underscore/hyphen identifier |
| purpose / review_status | `engineering_fixture`, or `traffic_experiment` with `accepted` upstream review |
| engine_version | `1.28.0`, verified against the native worker binary |
| parameters | Concrete scalar parameter cell; all keys must have matching prepared XML attribute bindings |
| parameter_bindings | Each key supplies declared input path, ElementTree relative XPath and attribute. The prepared file value must match the cell value. Worker does not mutate parameters after checksumming |
| network / routes / additional | `{path, sha256}` references; one converted network, nonempty explicit route file list, optional native control/additional file list |
| request_ledger | A checksummed JSON array describing every routed/initial vehicle request exactly once |
| initialization | `fresh_sumo_state` and its checksummed `state` asset, or fixture-only `explicit_empty_fixture` |
| simulation | Explicit begin/end/step, disabled automatic teleportation (`-1`), warn-only collision aftermath, junction-check flag and collision gap threshold. Other aftermath/control semantics require a new adapter and scientific review |
| provenance | Nonempty GIS source, initial parameterization, geographic/claim scope and input_realization_id; keep the actual upstream datasets/licensing/CRS/conversion and parameter evidence with preparation |

Paths stay relative within the bundle; source assets are checksummed. No symlinks, path traversal, external XML entities or XML includes are accepted. Explicit individual vehicle records are required; materialize flows or unrouted trip templates beforehand. Parameter bindings establish the declared XML coupling, not scientific correctness of the behavior or unit choices. They do not implement a general household/demand rescaling compiler or a Python coordinator.

## Vehicle/person request accounting

Each ledger row is `{vehicle_id, person_count, request_time_s, initial}`. IDs must exactly match the union of explicit routed vehicles and initial snapshot vehicles. Passenger weights are nonnegative integers. Pre-horizon requests must be explicitly initial; preserve their original request/history times. Requests at/after the run end are outside the cohort and rejected. Parked future supply is not silently counted as initially moving traffic. Reconcile household/resident, carried-person and external populations upstream according to the accepted scientific model.

Runtime tripinfo is checked for unexpected/duplicate IDs. Initial and future requests not completed remain unfinished, including requests not yet inserted. Person metrics are labeled ledger-weighted: this initial backend does not independently verify person actors, boarding, household membership or every seat-capacity assignment. It must not be presented as full multimodal/population validation. Time windows, boundary completion and ledger weights need upstream scientific review.

## Fresh state versus continuation

A fresh 03:00 physical state must have snapshot time equal to the case begin and vehicle IDs consistent with the initial ledger. A snapshot with saved RNG state is rejected in this fresh-replication interface: restoring an old RNG would defeat a requested new engine seed. Preparation must deliberately distinguish a fresh physical realization from exact continuation; the worker will not strip RNG state silently.

Exact project checkpoint continuation also requires adapter beliefs, messages, reservations, cumulative accounting and original future inputs. The native HTC backend does not yet implement that complete continuation mode or an external Python coordination loop. Use the separate checkpoint fixture only for its stated evidence. Empty starts cannot be used for a traffic experiment merely because initial GIS/occupancy data are missing.

## Sweep design

`sweep.json` contains schema_version, sweep_id, paths to the prepared case manifests, axes, replicates, base_seed, seed_scope and resources. The planner requires full factorial case coverage with no duplicate cells/levels or extra cases. Replicate seeds are `base_seed + replicate_index`, deliberately paired across parameter cases and bounded to the tested native seed range. `seed_scope` is `sumo_engine_only`; future demand and initial inputs remain immutable. Prepare separate scientifically appropriate input-realization designs to vary those sources, rather than assuming an engine seed does so.

One CPU is requested per job. memory_mb, disk_mb and wall_time_s are positive explicit pilot/resource choices; the application guard is at most 32,400 seconds. Initial batches are capped at 10,000 tasks to require an explicit scaling decision after pilots. The 256 MiB direct-input budget and task cap are implementation safeguards, not OSPool global quotas or scientific parameters. Neither task preparation nor worker execution may silently shrink GIS scope, drop actors, or omit missing design cells to meet a compute budget.
