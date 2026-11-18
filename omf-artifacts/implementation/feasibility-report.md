# Initial materialization and checkpoint feasibility report

Version: 0.1 | Date: 2026-11-17 | Authority: OMFB | Status: observed engineering evidence, not Phoenix validation

## Benchmark acceptance and generated demand

The user accepted the concrete Coronado accounting benchmark and its stated hypothetical assumptions/simplifications. The active recipe is scenarios/coronado-benchmark.json. The historical proposal remains at proposals/coronado-hypothetical-v1.json. Execution readiness is false: no AOI polygon/routable extract, physical initial road states, origins/destinations/routes, controls or operator profiles have been supplied.

scripts/materialize_benchmark.py (at repository root) generated files under generated/coronado-demand/: 1,000 households, 2,300 residents, 380 resident vehicle requests carrying 460 residents, 380 prepositioned service vehicles, 510 external future requests and 560 external future people. Integer largest-remainder allocation produces 26 empty, 408 one-person and 76 two-person external requests. Those 890 future requests exclude the still-unresolved initial on-road vehicle population. Household coordinates, gateways and routes are null, not invented. Resident travelers appear in only one request; external people have distinct IDs and are not added to resident totals.

Use from the repository root:

```sh
python scripts/materialize_benchmark.py --config omf-artifacts/implementation/scenarios/coronado-benchmark.json --output /tmp/coronado-demand --seed 20261117
python -m unittest discover -s tests -v
```

The generator uses Python 3.12.3 for this recorded realization, independent SHA-256-derived MT19937 streams, stable ID ordering and integer microsecond departure times. Record Python/algorithm version with results; no cross-version stream guarantee is claimed. Output manifest records input and output SHA-256 digests. Conflicting output files are rejected. Four tests passed: accounting/household consistency and repeatability; seed variation preserving marginals; inconsistent/unaccepted input rejection; and fraction/stream separation. The checked seed is 20261117. This is a materialized hypothetical request realization, not routed traffic or measured data.

## SUMO probe

An isolated temporary Python environment contained eclipse-sumo, traci, sumolib and sumo-data, all version 1.28.0. The test generated a 3x3 synthetic grid with one signal controller, simple explicit Krauss vehicle dynamics and 0.5 s steps. These are engineering-fixture settings, not the selected Phoenix scientific dynamics/timestep. It ran uninterrupted through 160 s, then restored at 30 s and 60 s. Full observed records matched exactly for 260 and 200 subsequent samples respectively.

Coverage passed for an actually carried rider, parked vehicle, future departure, signal state, an active speed intervention at the first save, a queued message at both saves, and an adapter-held reservation. Each saved pair contains native SUMO state and external adapter/RNG state. Original future inputs are loaded again. Engine RNG/person-state saving and high state precision are explicit. Observed vehicle/person positions and speeds, route progress, light state, arrival/departure lists, adapter state and collision counts were compared. Unobserved engine state was not proved complete.

Raw files in spike-results/sumo-1.28.0/ contain fixture network/routes, native states, adapter states, uninterrupted/resumed traces and summary.json. The summary records input digests and exact package versions. The same-platform test does not establish portability across versions, operating systems, threading, complex lane-changing/car-following, pedestrian models, or future adapter extensions. It does not establish physical fault realism, injury estimates, citywide scalability, or Phoenix validity. Native save-state limitations remain relevant to models not tested here.

To reproduce with a separately provisioned matching engine/TraCI environment:

```sh
python scripts/check_sumo_checkpoint.py --output /tmp/traffic-checkpoint-probe --sumo /path/to/sumo --netgenerate /path/to/netgenerate
```

Actual authoring commands used an isolated interpreter at /tmp/autonomous-traffic-sumo-spike/bin/python and the staged scripts; this temporary environment is not a project dependency installation. Exact installed packages were eclipse-sumo==1.28.0, traci==1.28.0, sumolib==1.28.0 and sumo-data==1.28.0. Package/environment release stewardship remains separate future work. The source fixture uses localhost TraCI; the execution sandbox needed a socket permission override. No real road system was accessed or controlled.

## Readiness and next work

The acceptance gate is resolved for this hypothetical accounting benchmark; no repeat approval of those choices is needed. Demand compilation and a scoped checkpoint probe are working. The Coronado model is not yet executable. Network extraction/audit and resolving the geometric/control/physical inputs are next. Preserve data licensing/source evidence, geographic scope, boundary flows, and rejected/unroutable demand. Return any required scientific redesign to OMFA rather than adapting it silently to engine convenience.
