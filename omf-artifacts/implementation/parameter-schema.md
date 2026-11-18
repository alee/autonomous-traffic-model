# Initial conditions and run requests

Version: 0.2 | Date: 2026-11-17 | Authority: OMFB | Status: draft design, no loader or simulator

## Agreed workflow

The user refined the initial workflow to a quiescent 03:00 start, individual actors generated from occupancy-based inputs, checkpoint continuation, and a configurable area of interest for computational tractability. Encode this through a scenario recipe and two kinds of run request: generate a fresh quiescent state or restore a complete checkpoint. Quiescent does not imply an empty road network. Three input categories are accepted: road occupancy, persons per vehicle, and household population/aggregates. Detailed road measurement, actual rates/distributions, the actor-generation rule, and AOI extent remain unresolved; the draft leaves them null rather than deciding them silently.

The three example JSON files and accompanying schemas are design artifacts. They intentionally contain null references where network, demand, vehicle dynamics, and controller definitions remain unavailable. Structural validation does not make them executable. No initializer, checkpoint writer, loader, or simulation is implemented.

## Four distinct records

| Record | What it means | What it contains |
|---|---|---|
| Scenario recipe | The experimental world and external inputs | Clock, immutable input references, quiescent-state declaration, future demand and event schedules |
| Run request | The policy and random realization to apply | Scenario reference, policy definition, fresh/continuation mode, RNG configuration |
| Checkpoint | The complete realized state at a simulation instant | Vehicles, queues, controller memory, pending demand/events, messages, random streams, accounting |
| Resolved run record | What actually ran | Resolved input digests, code/environment identity, realized populations/events, parent checkpoint and output digests |

The resolved record and checkpoint payload formats will depend on the engine and are contracts below, not invented engine-specific serializations. Keep authored recipes human-editable and generated records immutable. Use JSON initially so examples, nulls, units, and schema checks are explicit. A future YAML interface must normalize to the same meaning without introducing defaults.

## Scenario recipe

See examples/phoenix-morning.scenario.json and schemas/scenario.schema.json. Asset paths are relative to the file containing the reference. Every executable asset needs its byte-level SHA-256, its schema/version, and an inspectable scientific source. Null means unresolved and prevents execution; it never means use an implicit default. Asset digests are not a claim of empirical quality.

| Field | Meaning / scientific source |
|---|---|
| clock | Seconds elapsed since hypothetical 03:00 local. The previously proposed 10:00 demand stop and 11:00 end remain provisional, now 25,200 s and 28,800 s after start. A separate analysis/buildup cutoff is unresolved. Source: user refinement and revised Phoenix case |
| spatial_scope | Configurable reporting AOI (bbox or polygon), context-buffer distance, and external-demand profile. No actual extent or buffer distance selected. Smaller AOIs limit inference; boundary flows and exported queues must remain visible |
| assets.network | Directed topology, stable node/link/lane/movement IDs, units, coordinates, capacities/storage, turn restrictions, grade separation, crossings, and regional boundary context. Source: ABM spec and Phoenix case |
| assets.demand | Immutable trip requests with persistent trip IDs, request times, origins/destinations, mode, occupancy, and boundary-trip classification. Source: ABM spec and evaluation report |
| assets.population | Assignment of vehicles/trips to operators, participation, behavior policy, initial health, dimensions/dynamics classes, sensing and communication profiles. Source: ABM spec and assumptions |
| assets.dynamics | Physical bounds and motion model configuration; no unsupported numerical kinematics supplied here |
| assets.environment | Initial exogenous road availability, weather/surface assumptions if represented, crossing/transit demand and fixed infrastructure definitions; controls chosen by policy remain separate |
| initialization | Quiescent at 03:00 with occupancy-conditioned individual actors. Initial occupancy/population and infrastructure/control profiles must define actual vehicles, routes, states, and any existing queues/messages/commitments; no assumption that each is zero |
| future_inputs | Scheduled trip arrivals plus bounded disturbances. Future demand is not part of the physical t=0 occupancy |
| checkpoints | Proposed capture times and the required schedule boundary; these are output requests, not extra initial conditions |

The initial snapshot is defined before t=0 scheduled inputs. Already active actors must carry their original request/departure times, destinations, route progress, and relevant control/observation state. Future demand must exclude those trips to prevent double counting. Requests exactly at t=0 enter through the normal demand process. Startup may precede an analysis window; analysis exclusions must not erase earlier waits or queue formation. At demand_stop_s no new requests are introduced; waiting requests remain. State at end_s is recorded without silently deleting unresolved demand or vehicles. These boundary conventions are explicit implementation proposals; confirm against the eventual scheduler before result interpretation.

The baseline example has no injected disturbance. A failure variant changes the scenario/event schedule and gets a distinct scenario identity. An S1 event, for example, can specify onset 16,200 s, duration 900 s, 1% of vehicles physically present at onset, persistent identities, and seed-controlled selection. Those values come from the hypothetical scenario register. An event schedule must preserve family, capability bounds, candidate population, selection rule, rounding/capping, end behavior, and scientific rationale. It cannot substitute a hidden arbitrary actor classifier.

Population descriptions must keep affiliation, cooperation, participation, health, and malicious intent separate. Ground-truth attributes are visible to the scenario engine/evaluator; driving and coordinating policies receive observations through their declared interfaces. A controller must never load the complete population definition as its observation state.

## Fresh runs and continuation

See examples/phoenix-morning.fresh-run.json and examples/phoenix-morning.resume-run.json. C0 identifies a candidate family, not an implemented algorithm. Its exact signal/control initialization, route policy, observation model, and fallback rules remain unresolved assets.

The example proposes checkpoints at 06:00 (10,800 s) and immediately before the normal 07:30 event opportunity (16,200 s). They enable examination after buildup and resumption near disturbances. Capture at a defined tick boundary before demand introduction and message delivery for that tick. A checkpoint also records the next scheduler phase, rather than relying only on its timestamp. Motion/coordination timestep alignment is checked later; no timestep is selected here.

For exact continuation, restore absolute elapsed time and pending-input cursors. Do not reset elapsed time to zero, resample actors/trips, or restart the buildup. Resumption at 10,800 s continues the original run through 28,800 s; it does not restart the eight-hour window. Counters preserve original request times and earlier waiting/travel. Analysis may select a post-checkpoint window while retaining prehistory needed for complete accounting.

## What a checkpoint must preserve

- Identity: checkpoint format/version, model and engine revision, scenario/input digests, complete policy and physical configuration identities, parent run, checkpoint digest, and precision/platform compatibility metadata.
- Time: absolute simulation time, timestep/index, schedule phase and next action, and each clock's next activation.
- Physical agents: persistent vehicle/trip IDs, position or supported link/lane progress, speed and any dynamic state needed by the integrator, route/progress, occupancy, operator, health, and behavior state.
- Queues and accounting: internal and boundary entry order, requested-but-not-entered trips, completed/unfinished IDs and cumulative counters. Derived queue data may be recomputed only if equality with saved state is checked.
- Infrastructure/control: movement service, signal phase and remaining time, coordinator reservations/leases, learned/adaptive estimates if any, local controller memory, and state of unavailable infrastructure.
- Information: each agent's observation history needed for decisions, stale beliefs, sent/in-flight messages and delivery order, acknowledgments, and commitments. Restoring truth is not restoring beliefs.
- Future: remaining demand, realized assignments, active disturbances and their residual duration, scheduled future events and cancellation state.
- Randomness: generator name/version and full state for every named stream, plus any counters for keyed random draws. A seed alone cannot restore streams already consumed.

No checkpoint is serializable/executable yet. The engine must reject incompatible snapshots explicitly; silently dropping an unrecognized state field breaks exact continuation. Input hashes must be checked against actual files, not merely compared with other unverified metadata.

## Comparing coordination policies

Use fresh runs with the same realized quiescent physical population, trip requests, operator assignments, and exogenous randomness as the default comparison. Policy-specific control initialization must be declared separately. Each policy creates its own subsequent buildup and checkpoints. This measures each policy's whole trajectory, including congestion it created.

Exact continuation requires the same policy definition, physical model, input realization, and compatible engine. Branching a checkpoint into another policy is a separate intervention: old reservations and controller memory may not have a valid meaning. Require an explicit conversion/reset procedure, preserve the original checkpoint, record the intervention time and changed state, and evaluate transition effects. The current resume request supports exact continuation only; cross-policy branching remains a scientific decision for OMFA, not an automatic loader feature.

Named stochastic streams cover demand, departure times, ownership/population assignments, fault selection, communications, and policy tie-breaking. Algorithm/version and seed derivation are unresolved and block execution. Adding a policy-side random draw must not change the exogenous trips. Matching seeds alone is insufficient if draw consumption differs: materialize exogenous inputs or key draws by stable entity/event IDs. Selection from vehicles present at onset can yield different candidate sets across policies; report candidate counts, selected IDs, and realized fractions. Such runs match the selection rule, not necessarily the affected vehicles. Use independently fixed cohorts only in a separately declared scenario.

## Validation and remaining decisions

JSON Schema checks required fields, basic types, explicit units, and the disjoint fresh/resume forms. It does not prove compatible topology, physically possible occupancy, complete policy definitions, time ordering, artifact availability, checksum correctness, or resumability. Those are semantic checks in verification-plan.md. Draft requests must be rejected by any future execution entry point until fully resolved and validated.

Open: actual asset formats and values; complete policy definitions; numerical time resolution; RNG algorithm and seed derivation; engine checkpoint serialization; boundary topology; physical/sensing detail sufficient for each claimed outcome. The latest accepted starting point is quiescent 03:00, occupancy-based individual actors, configurable AOI, and checkpoint continuation. This supersedes the earlier empty-start default. Checkpoint capture times and tick-boundary conventions are implementation proposals, not measured Phoenix facts. The scientific refinement is recorded in ../initial-conditions.md and updated OMFA artifacts. This parameter encoding follows those sources without choosing unresolved numerical profiles, road measurement, or geography.

## Occupancy and geographic scope

The user selected three separate profiles: `initialization.occupancy_profiles.road`, `.vehicle`, and `.household`. Road loading constrains initial vehicles; persons per vehicle supports person accounting; people per household or equivalent aggregates constrains the resident population. Each profile needs spatial/time support, a distribution or explicitly justified aggregate, and evidence class. Numerical profile assets remain null. A percentage without a denominator is invalid. Schema version 0.2 replaces the v0.1 single occupancy selector; run-request schema remains v0.1 because its shape is unchanged.

For road occupancy, leave `measure` unresolved until the data/model definition is chosen: spatial occupied fraction, vehicles per lane-kilometer, and temporal detector occupancy are distinct measurements. A conversion to feasible individual vehicle states needs an explicit materialization profile; do not silently equate these units. For vehicle occupancy, the profile unit is `persons_per_vehicle`; actual vehicle counts must respect seat capacity and may include zero-person autonomous movements when modeled. For households, the profile unit is `persons_per_household`; its representation can be explicit households, weighted households, or zone aggregates, and is still unresolved. The profile must retain resident totals and explain how size distributions or aggregates map to individual actors.

Proposed realization order: resolve AOI/context and population totals; construct resident population from household inputs; construct or load a time-varying exogenous trip realization using declared departure/destination/mode/sharing rules; reconcile initial on-road vehicles and their carried people against the road and vehicle profiles; preserve existing trip histories and exclude those ongoing trips from newly introduced demand. This is an implementation dependency order, not acceptance of a particular population-synthesis or trip-generation algorithm. It preserves the assumption of exogenous within-run demand. Resident household totals do not constrain visitors or through travelers to be resident household members. Avoid forcing noisy independent input marginals to exact agreement through undocumented tuning; record discrepancies and the chosen reconciliation method.

Checkpoint state must include any materialized resident/traveler identities, household or aggregate membership/weights, current locations, travel-party assignments, and remaining trip commitments needed for consistent continuation. No person may be copied into simultaneous unrelated trips. Keep empty fleet repositioning and freight movements distinct from resident person travel. Aggregate counts and individual realizations must be labeled and reconciled, not added together as separate populations.

`spatial_scope.aoi` accepts an explicit WGS84 bounding box `[west, south, east, north]` or a referenced polygon. A bbox may be null in a draft. `context_buffer_m` is a distance in meters computed using a suitable metric/geodesic method, not a number of longitude degrees. Keep boundary-crossing routes, entry queues, arrivals, departures, and external pressure; a small map cannot become an isolated closed road system by accident. Materialize inputs after selecting AOI and context, record the geographic extent, and preserve external-trip accounting. Scaling must retain densities/rates where applicable rather than silently keeping a fixed citywide actor count in a smaller region.

Record actual link/agent counts and computational cost. Resource limits may cause preflight rejection or an explicit configuration revision; they must not silently delete traffic or trim the selected region during a run. Compare expanded context buffers before interpreting coordination benefits. A small AOI run is a subarea experiment; citywide conclusions require suitable coverage and evidence.
