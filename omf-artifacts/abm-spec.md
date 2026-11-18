# ABM specification
Version: 0.5 | Date: 2026-11-17 | Status: draft, unreviewed | Authority: OMFA | Author: Codex with user-supplied intent

## Rationale for Agent-Based Modeling
See conceptual-model.md and research-questions.md. Individual commitments and heterogeneous behavior generate network outcomes; citywide emergence is the target.

## Agent Definitions
Vehicle states: physical pose or link progress, speed, dimensions, trip request and destination, route, occupancy, operator identity, local observations, received messages with timestamps, and access commitments. Health and intent are latent scenario states, observable only through modeled evidence. Drivers decide routing, movement requests, and bounded acceleration/braking. Parameter values are not yet evidence-backed.

Operator rules span independently optimizing compliant fleets, cooperative fleets, and noncommunicating participants. Faults alter sensing, messaging, or actuation independently. Deliberate disruption may involve false intentions, unfulfilled reservations, or physical obstruction under declared capability budgets. Correlated failures and collusion are separate scenarios. No actor receives unbounded control over physics or the evaluator.

## Environment Specification
Directed road graph with permitted turns, lane/storage constraints, intersection conflicts, access controls, crossings, transit interactions, and boundary demand. Include freeways and ramps if required by the chosen city boundary; omitting them limits claims to surface streets. Coronado is the accepted first reporting AOI with a 1,000 m context. Its exact extract, topology and geometry fidelity remain unresolved.

## Scheduling and Execution
Provisional synchronous decision rounds: introduce scheduled demand; deliver messages whose delay has elapsed; form observations from the current physical state; calculate driver/coordinator decisions from the same observation snapshot; apply commands and advance physical motion simultaneously; detect conflicts and record outcomes. Communications and coordination may have slower clocks than motion. Resolve simultaneous access ties by a declared reproducible rule, not container iteration order. Time increments and within-step collision detection must be justified by resolution sensitivity before safety-related comparisons. No implementation schedule is claimed finalized.

## Interaction Protocols
Candidates: C0 fixed-time signals and local route choice; C1 demand-responsive signals; C2 cooperative reservation-based access; C3 reservations with observation checks, expiry, and conservative fallback; C4 federated intersection coordination with network routing advice. Compare policies with matched information and actuation except where those differences are the explicit experimental factor. O is an ideal-information optimization reference, not a feasible controller. Its optimum is only claimed if solved and certified for the defined instance; otherwise report its bound/gap. It cannot command adversaries or ignore physical constraints.

## Output and Observation
Record trip requests, entries, exits, unfinished trips, movement trajectories at represented resolution, queue/storage state, safety events, communication and access failures, and disruption/recovery times. Controller observations are separated from evaluator ground truth. Outcome definitions are in evaluation-report.md.

## Assumptions and Limitations
See assumptions.md. Random demand, route ties, delay/loss, and fault onset require explicit distributions or scenario schedules, seed capture, and independent random streams. Use matched exogenous demand/scenario realizations across policies and multiple replications; numerical replication count awaits pilot variance. No learning agents or language models are presumed necessary. Mechanisms, bounds, and physical fidelity require review before OMFB handoff.

## Phoenix refinement (0.2)
Use phoenix-case-study.md for geography, 03:00 start and configurable study clock, entry/boundary accounting, multimodal constraints, and motion fidelity. Use scenario-register.md for bounded events and separate participation, ownership, health, and intent. Persistent identity is a declared initial assumption; no oracle supplies trust labels. Use experiment-plan.md for comparison and observation definitions. Finite queues and interference must not be bypassed by an implicit universal safety enforcer. Detailed numeric kinematic and fallback rules remain provisional scientific decisions for explicit handoff review, not undocumented implementation defaults.

## Initial conditions and continuation (0.3)
Initialize quiescent at 03:00 using occupancy-conditioned individual actors within a configurable AOI and context. Maintain separate road-loading, persons-per-vehicle, and household-population profiles (explicit households or equivalent aggregates). The accepted Coronado accounting benchmark supplies hypothetical household/party counts, departure windows, destination classes and a 2-vehicles-per-lane-kilometer initial target. Exact physical positions, mapped endpoints/routes, controls and empirical support remain unresolved; do not substitute zeros or passenger counts for missing physical inputs. Existing actors need destinations, route progress, original trip times, relevant physical state, and observation/control history. Do not generate those same trips again in future demand. Checkpoint continuation preserves complete physical, control, information, event, random-stream, and accounting state. See initial-conditions.md and implementation/parameter-schema.md. Area reduction limits scientific scope and must retain explicit external demand and boundary accounting.
