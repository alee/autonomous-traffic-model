# Initial conditions and area of interest
Version: 0.7 | Date: 2026-11-17 | Status: draft, unresolved inputs | Authority: OMFA

## Purpose and accepted choices

The model starts quiescent at 03:00 America/Phoenix and develops through individual actors generated from occupancy-based inputs. Quiescence means low activity; it does not establish an empty road network. The user retained checkpoint continuation and requested a configurable geographic area of interest (AOI) for computational tractability. These decisions supersede the prior 06:00 empty-start proposal while retaining the overall citywide research question.

## Unresolved scientific inputs

The user clarified three distinct inputs: road occupancy, people per vehicle, and people per household (or equivalent aggregates). Include all three; none substitutes for the others. The clarification itself did not supply numbers. The subsequent user-accepted Coronado benchmark below now supplies scoped hypothetical household, vehicle and road-density values; empirical support, precise geometry and physical realization remain unresolved.

| Input | Meaning | Role |
|---|---|---|
| Road occupancy | Road loading at the initial time, with its precise measurement and units declared | Constrains the initial vehicles already on road links; do not conflate density, spatial occupied fraction, and detector time occupancy |
| Vehicle occupancy | Number of people carried per vehicle, by relevant class/time/trip | Converts vehicle movements into person movements and supports person-based outcomes; include empty autonomous repositioning when modeled |
| Household population | People per household, or a distribution/aggregate preserving resident totals | Constrains resident population available for trip-demand construction; a population count alone does not specify departures, destinations, or mode |

Keep initial on-road travelers, people at homes/other locations, external travelers, and later requests consistent. An on-road person is not simultaneously available for another trip. Household size is not a count of vehicles, and the same population can produce different traffic under different departure, mode, sharing, and destination assumptions. Input household aggregates may support synthesis of individual actors; do not require identifiable household microdata. The distribution or aggregate-to-individual rule remains a scientific choice. Initial road users can be visitors or through travelers and need not all be assigned to resident AOI households.

Initial individual actors need feasible physical states, trip identities, origins/destinations, routes/progress, occupancy, operator/participation and health/behavior assignments, and applicable observation/control history. Preserve their pre-03:00 trip timing where relevant. Future trip requests must not duplicate already-active trips. The means of constructing a physically/control-consistent initial population remain unresolved, rather than being replaced with uniformly placed vehicles or zero queues.

## Spatial and temporal scope

Choose a reporting AOI plus the surrounding simulated context, external demand and boundary flows. Record the actual extent and the scope of claims. Changing AOI can alter demand, route opportunities, bottlenecks, and boundary effects; preserve rate meanings and test expanded context. Computational efficiency does not justify silently deleting traffic, closing boundaries, or claiming citywide effects from a subarea.

03:00 is the accepted start. The earlier hypothetical 10:00 demand stop and 11:00 end can remain configurable draft bounds, not observed Phoenix demand times. The analysis/buildup cutoff has not been selected. Record the complete trajectory and maintain original request times and unfinished demand even when analysis windows differ.

## Continuation and comparison

A checkpoint preserves the complete physical, information, controller, event, random, and accounting state at an identified scheduler boundary. A seed and vehicle coordinates alone are insufficient. Resume at the saved absolute time without rebuilding initial actors, reinjecting prior demand, or resetting waits. Exact continuation requires compatible policy/model/input state; switching control policy at a checkpoint is a distinct intervention requiring an explicit state treatment.

For matched fresh comparisons, freeze the realized initial actors, future demand, and exogenous assignments. Preserve policy-specific control initialization as an explicit difference. Existing assumptions on hidden intent, bounded physics, participation, and fault/adversary separation continue to apply.

## Scientific readiness and handoff

Implementation representation can proceed with unresolved fields visibly null. Synthetic household/person/request materialization is implemented for the accepted benchmark. The physical on-road state remains non-executable until geometry, routes, prior trip history and control/dynamics profiles are resolved. OMFB owns the parameter schema, reference resolution, and checkpoint/initialization verification contract. Uncertainty and evaluation artifacts carry initial-state and boundary limitations. The separate engineering fixture and Python package do not establish empirical traffic validity; see implementation/python-stack-verification.md.

## Acceptance and current benchmark (0.6)
The user accepted the reviewable Coronado first accounting benchmark on 2026-11-17, including its 1,000 m context, 1,000-household/2,300-resident synthetic population, 380 resident vehicle requests carrying 460 people, 510 external arrivals, 2 vehicles/lane-km initial external road target, prepositioned resident AV service, and deferred pedestrian/transit demand. These are accepted hypothetical experimental inputs, not measured Phoenix facts. The active machine-readable recipe is implementation/scenarios/coronado-benchmark.json. The proposal file remains historical. Geographic extraction, routing, initial physical on-road states, controller/dynamics and operator profiles still need completion. Demand materialization does not resolve those gaps.
