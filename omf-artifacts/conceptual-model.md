# Conceptual model
Version: 0.5 | Date: 2026-11-17 | Status: draft, unreviewed | Authority: OMFA | Author: Codex with user-supplied intent

## Model Purpose and Scope
Explore citywide coordination tradeoffs under heterogeneous autonomy and unreliable cooperation. The unit of study is a connected urban road network, including boundary inflows/outflows and freeway interfaces where relevant. Each scenario configures its reporting AOI and surrounding simulation context; citywide remains the overall research scope, while individual subarea runs support correspondingly limited claims. Represent low-activity buildup from 03:00, congestion, disruption, and recovery; exact subsequent study bounds remain configurable and evidence-limited.

## Entities and State
Vehicles carry position, speed, destination, route, occupancy, operator affiliation, observations, and commitments. Operators have distinct local objectives and policy rules. Intersections and road links have permitted movements, signal/service states, storage, capacity, queues, and occupancy. Communications have delay, loss, and availability. Pedestrian crossings and transit service demands constrain access; these groups cannot disappear from citywide welfare assessment.

Behavioral dimensions are separate: operator independence, cooperation, sensing quality, actuation health, communications participation, and malicious intent. The evaluator knows scenario assignments; controllers do not receive hidden actor labels.

## Relationships and Interactions
Drivers choose routes and movements using their available information. Coordination policies advise routes or allocate intersection access. Vehicle motion obeys physical limits even when actors violate rules. Queues occupy finite space and can block upstream links. Reported intentions can disagree with observed behavior. Controller failure and shared operator/software faults are explicit alternatives to isolated vehicle faults.

## Dynamic Logic
Demand creates trip requests; entry queues preserve requests when links are full. Vehicles observe locally, receive delayed messages, choose actions, and advance subject to dynamics. Coordination can be centralized, local, or federated. Local fallback is a candidate mechanism, with success measured rather than assumed. Congestion changes route costs and induces rerouting; synchronized choices may create oscillations. Recovery and noncompletion are outcomes.

## Mapping to Objectives
RQ1 compares policy outcome vectors; RQ2 varies behavior and information; RQ3 uses finite storage and route interaction; RQ4 examines degradation and recovery; RQ5 uses an ideal-information reference.

## Abstraction rationale and evidence
Agent representation is needed for heterogeneous intent, information, commitments, and operator-level correlations. Aggregate flow alone hides these distinctions; optimization alone does not represent departures from prescribed behavior. Use a network traffic representation with individual vehicles; collision claims require sufficiently detailed trajectories and geometry. A queue-only realization can support congestion comparisons but cannot substantiate collision avoidance.

Reservation coordination has a prior research basis in Dresner and Stone (2008), listed in city-use-cases.md. No empirical support for the proposed fault prevalence, adversary behavior, or city-specific benefit is claimed. Detailed perception, vehicle hardware, long-term land use, and induced demand are outside the initial conceptual scope; this limits transfer to deployment and long-term policy.

## Historical Phoenix realization scope (0.2)
Phoenix is the first city. phoenix-case-study.md specifies municipal outcomes with regional context, the hypothetical time window, and explicit geometric/safety limits. scenario-register.md bounds the initial fault/adversary families. data-evidence-assessment.md records inspected metadata and unavailable measurements. These refine the conceptual scope without claiming empirical parameter support. The original full-day ambition is deferred; the first experiment uses the explicitly limited morning window.

## Initial-state refinement and current benchmark
The user selected a quiescent 03:00 start with occupancy-based individual actors, saved-state continuation, and configurable AOI. This supersedes the empty-start/06:00 draft defaults. See initial-conditions.md; the occupancy inputs are now road loading, people per vehicle, and household population or equivalent aggregates. The accepted Coronado benchmark supplies scoped hypothetical rates, household/party rules, named AOI boundaries and an initial vehicles-per-lane-kilometer measure; physical/spatial realization and empirical support remain unresolved. See first-scenario-proposal.md and implementation/scenarios/coronado-benchmark.json.
