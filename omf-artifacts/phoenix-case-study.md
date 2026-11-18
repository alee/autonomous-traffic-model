# Phoenix case study
Version: 0.4 | Date: 2026-11-17 | Status: draft, unreviewed | Authority: OMFA | Author: Codex with user-supplied intent

## Purpose and decision status
Phoenix is the first case, proceeding under the user's authorization to continue the proposed sequence. The user explicitly selected citywide scope and open tradeoffs earlier; detailed choices below are modeler defaults subject to revision, not additional user approvals. Chicago and NYC are later contrasts; LA is an alternative for freeway-focused expansion.

## Geographic boundary
The overall research question remains citywide, but each run has a configurable area of interest (AOI) to control computational cost. The AOI may be a Phoenix subarea or the whole city; its explicit geographic boundary and surrounding simulation context are part of the scenario. Include relevant local streets, arterials, freeway sections, and ramps within the declared extract. Report claims at the scope actually represented, without calling a subarea result citywide. Trips can cross the AOI/context boundary and re-enter; a boundary exit is not automatically trip completion.

Report outcomes for the AOI and surrounding context separately. Compare an expanded context network before attributing benefits to policy: faster AOI travel achieved by exporting queues or diversion is an outcome, not an unqualified benefit. Exact extract and context extent depend on obtainable topology and boundary data; no geometric boundary extract has been produced. A disconnected or arterial-only extract must be labeled as such and cannot establish full citywide performance. Preserve intersections, grade separation, one-way access, and turn permissions; apparent polyline crossings are not automatically junctions.

## Time and demand
Start at 03:00 America/Phoenix in a quiescent state, as directed by the user. Quiescent means low activity, not necessarily no vehicles or demand. Initialize individual actors from explicit occupancy-based profiles; the user selected road occupancy, people per vehicle, and household population (or equivalent aggregates). Their numerical values, detailed measurement definitions, and materialization remain unresolved. Do not assume that passenger occupancy, road density, and occupancy/activity at origins are interchangeable. Preserve the chosen realization for matched comparisons and checkpoint continuation.

The previous 06:00 empty-network default is superseded. The previously proposed 10:00 demand stop and 11:00 run end remain configurable, hypothetical study bounds, not measured Phoenix peak times. With those bounds, elapsed demand stop is 25,200 s and run end is 28,800 s after 03:00. The analysis/buildup cutoff is unresolved; record the full trajectory and retain original trip times and initial-state history needed for waiting and recovery measures. Checkpoints resume established state without rebuilding the actor population. See initial-conditions.md for scientific commitments and implementation/parameter-schema.md for their encoding.

Begin with explicit hypothetical origin-destination demand ensembles if no defensible trip table is available. Preserve the distinction between internal, inbound, outbound, and through trips and sensitivity to each. Network geometry alone does not make hypothetical demand representative of Phoenix. An empirical track needs compatible network/demand dates, time profiles, and independent evaluation observations.

## Actors and coordination
Model vehicles controlled by explicit decision policies, with multiple fleet affiliations and private operators. Cooperative and independent-compliant behavior, communications participation, health, and intent vary separately. Rule-based agents are sufficient for an initial mechanistic study; learning or language-model drivers require a separate scientific rationale and evaluation before introduction.

Control policies have only modeled observations and messages. The evaluator may inspect true faults and intentions for scoring; policies cannot. A first reservation study uses persistent vehicle identity as an explicit simplification, preventing unlimited fake identities; identity spoofing requires a separate scenario and capability budget.

## Physical representation and claim boundary
The target model represents individual vehicles, finite queues, spillback, route choices, conflict movements, and bounded driving dynamics. Citywide congestion experiments may use coarser motion, but no collision-avoidance conclusion follows without geometric vehicle trajectories, bounded perception/actuation, and resolution evaluation. An automatic conflict blocker is part of a tested policy or an explicit simulator idealization; it cannot silently make malicious/faulty actions harmless. Record denied or infeasible actions rather than claim the proposed controller avoided every collision.

Pedestrian crossings consume access time; transit vehicles share road space with occupancy and stop delays. Start with hypothetical demand and occupancy where necessary, then vary them. Without observed demand and explicit representation, results address conditional vehicle-network tradeoffs and cannot establish whole-city social welfare. Freight, emergency priority, cycling interactions, and curb activity remain distinct extension scenarios, with omissions disclosed.

## Readiness
Scientific scope, scenario families, objectives, and provisional clocks are now concrete enough to request OMFB planning for an exploratory realization. Empirical city-model readiness remains incomplete: no routable extract, origin-destination table, signal plans, parameter evidence, or independently assessed observations. OMFB must preserve these distinctions and the implementation/review triggers in README.md. This is a scientific handoff assessment, not an implementation architecture or engineering verification plan.
