# Initialization and checkpoint verification

Version: 0.2 | Date: 2026-11-17 | Authority: OMFB | Status: design checks only

## Checks performed for this draft

Validate all three draft examples against their JSON schemas. Confirm malformed fresh/resume requests, negative checkpoint times, and unknown initialization modes and invalid AOI forms are rejected. Check relative schema references and local documentation links. These checks concern representation, not simulation correctness. Results from the authoring transaction are recorded in provenance.

## Required execution gates

1. Reject null assets, draft readiness, undefined physical/control profiles, unknown units/versions, missing files, or incorrect digests. Never substitute a default based on filename. Resolve references relative to each containing file and prevent path ambiguity when packaging.
2. Require 0 <= analysis_start_s <= demand_stop_s <= end_s when analysis_start_s is supplied; otherwise preserve the unresolved analysis cutoff and strictly increasing checkpoint requests inside the supported horizon. Check event and scheduler boundary alignment against chosen numerical clocks. Input requests at demand_stop_s are outside the demand-introduction interval.
3. Check graph IDs, directed connectivity, turn/grade separation, boundary trip continuity, vehicle dimensions and physical bounds, profile referential integrity, complete operator/participation assignments, occupancy, and crossing/transit representation. A routable graph is not evidence of a calibrated Phoenix model.
4. At a quiescent start, verify that individual actors and any queues/commitments match the resolved occupancy/population/control profiles. Verify original request times, route feasibility, and no duplicates in future demand. Do not assume no nighttime traffic or erase waiting requests. For checkpoints with existing vehicles, check occupancy, finite storage, queue order, and applicable dynamics; do not impose an assumed safe state that erases modeled failures.
5. Confirm that policy-visible input contains only modeled observations/messages, including after restore; latent intent, true fault labels, and undelivered future messages remain hidden. Validate actual input file digests before accepting checkpoint compatibility.
6. From a deterministic fixture, run uninterrupted to an end time and compare with save/restore at several boundaries: physical trajectories, observation/control state, message order, event activation, RNG state, queues, trip IDs, and cumulative outcomes must agree within a declared precision contract. Start with exact equality when the engine supports it; otherwise document a justified numerical tolerance and its limits, never assert bitwise portability without evidence.
7. Repeat continuation with an in-flight message, a blocked entry queue, an active reservation, an active fault crossing the save boundary, and requests at t=0 and demand_stop_s. A fault due at checkpoint time must activate exactly once after restore.
8. Changing policy code, input bytes, dynamics, engine/schema version, or required state shape must reject exact continuation unless an explicit compatible migration is implemented and verified. A policy switch is a separately declared experiment, never an implicit resume.
9. Compare matched policies using frozen demand/population realizations; show that extra policy-side random draws do not change those inputs. Report when present-at-onset selection yields different affected cohorts. Preserve unfinished demand and original waiting times across resume.

No future checks above have run: no loader, scheduler, driving model, checkpoint payload, or simulator exists. Numeric profiles, graph coverage, and independent scientific evaluation remain unresolved.

10. Reject reversed/out-of-range bbox bounds and missing polygon inputs; check extracted AOI/context topology, rate units and spatial support, boundary inflow/outflow, and conservation across AOI changes. Check expanded context and resource estimates; never silently truncate actors or topology to fit a compute budget.

## Occupancy/population consistency requirements

Require all three occupancy-profile declarations. Reject unknown road measures and unit swaps between persons per vehicle and persons per household. Check the numeric contents and units of resolved profile assets separately from their references. The schema does not inspect those future files.

For a realized initial state, check road-loading consistency using the selected measurement/conversion, individual vehicle capacity, unique person/trip assignment, resident totals versus household/aggregate totals, preserved aggregate weights, and removal of already-active trips from future arrivals. A zero-person AV may be a valid repositioning trip; household population does not imply all residents are traveling. Visitors and through travelers remain explicit nonresident populations. Report incompatible marginals and any reconciliation rather than silently modifying demand. Restore population/household membership and travel-party commitments at checkpoints. These semantic checks remain planned; no loader or actor generator exists.

## Headless runner checks now performed

The generic runner has a separate tested contract: input/binding digests, task identity, safe archives, complete factorial coverage, fresh-state/RNG rules, isolation, serial/concurrent agreement, missing/failed-result reporting, and unfinished-cohort accounting. htc-verification-report.md records native and offline-container results. These checks do not satisfy the future city adapter, fault, coordination or complete coupled checkpoint gates above. Native worker eviction currently restarts the task from its original prepared input; there is no distributed continuation protocol.
