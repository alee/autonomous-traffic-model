# Assumptions
Version: 0.6 | Date: 2026-11-17 | Status: draft, unreviewed | Authority: OMFA | Author: Codex with user-supplied intent

All entries except A1 are provisional modeling judgments, not empirical observations.

## Structural Assumptions
- A1 (user-selected): citywide road network; multiobjective tradeoff exploration.
- A2: finite link storage, queue spillback, boundary demand, and route feedback are essential. Omitting them invalidates citywide coordination claims.
- A3: evaluator truth is separate from information available to agents; no perfect intent detector.
- A4: multiple independent operators can be cooperative, compliant but selfish, faulty, or malicious in different combinations. Independence does not imply hostility.

## Behavioral Assumptions
- A5: physical bounds apply to every vehicle; protocol compliance does not. A reservation is a claim, not a guaranteed trajectory.
- A6: malicious capabilities and correlated faults are declared per scenario. Absolute safety against unrestricted physical attackers is outside the claim set.
- A7: fallback behavior may reduce throughput or fail; it is evaluated rather than automatically enforced as a protective oracle.

## Parameter Assumptions
- A8: no measured parameter values or defensible attack probabilities have been supplied. Demand, braking, latency, fault duration, fleet share, and adversary budgets remain unparameterized. Do not convert illustrative sweeps into prevalence estimates.
- A9: occupancy is needed for person-based outcomes; absent evidence, compare multiple occupancy scenarios and disclose assumptions.

## Simplifications and Abstractions
- A10: first study treats trip demand as exogenous within a day. No long-term demand, land-use, or adoption forecast follows.
- A11: collision or near-miss analysis requires trajectory detail; queue-only dynamics restrict conclusions to congestion and access.
- A12: city data describe contemporary traffic, not future AV behavior. Use for boundary conditions and baseline evaluation, not as proof of future performance.

## Data and evidence assessment
Official candidate sources are linked in city-use-cases.md. No raw datasets inspected or processed. Counts alone cannot identify origin-destination demand, routes, signal timing, or vehicle dynamics; multiple demand/behavior combinations can fit the same counts. Dataset selection, licensing, completeness, and independent evaluation splits remain unresolved.

## Phoenix evidence and defaults (0.2)
- A13: Phoenix is the first case under user authorization to proceed. Municipal study outcomes require regional routing context; exact extraction remains unperformed. Boundary sensitivity is required.
- A14: 03:00 is the user-selected starting time. The prior 10:00 demand stop, 11:00 end, and scenario stress levels remain hypothetical configurable study settings, not measured Phoenix conditions.
- A15: persistent vehicle identities bound the initial protocol threat model; spoofed identities and unbounded collusion are untested.
- A16: metadata availability is not dataset completeness. Official MAG planning-network attributes do not establish routability, signal plans, as-built status, or local-street coverage. See data-evidence-assessment.md. Raw records could not be retrieved in this environment.
- A17: ten pilot replications estimate variance only. Later precision decisions must be declared and reported.

Data-source update: P1–P6 are documented with access and quality limitations in data-evidence-assessment.md. No measured transport parameters added. Uncertainty register and prospective evaluation reviewed for consistency in this transaction; no calibration or validation report exists yet.

## User-directed initialization and scope (0.3)
- A18 (user-selected): start quiescent at 03:00, initialize individual actors using occupancy-based inputs, and support checkpoint continuation. This replaces the earlier empty-start default. Low activity does not establish zero traffic or any measured nighttime rate.
- A19 (user-selected): make AOI configurable for computational tractability. Subarea results do not establish citywide outcomes; retain explicit external-demand/context handling.
- A20 (partly resolved by user): represent road occupancy, persons per vehicle, and persons per household (or equivalent aggregates) separately. Detailed road measure/units, numerical values/distributions, temporal/spatial support, materialization mechanism, and initial route/control history remain unresolved. Preserve these as missing scientific inputs, not silent defaults.

See initial-conditions.md. Uncertainty and evaluation implications were reviewed in this revision; no empirical support is added.

## Acceptance and current benchmark (0.6)
The user accepted the reviewable Coronado first accounting benchmark on 2026-11-17, including its 1,000 m context, 1,000-household/2,300-resident synthetic population, 380 resident vehicle requests carrying 460 people, 510 external arrivals, 2 vehicles/lane-km initial external road target, prepositioned resident AV service, and deferred pedestrian/transit demand. These are accepted hypothetical experimental inputs, not measured Phoenix facts. The active machine-readable recipe is implementation/scenarios/coronado-benchmark.json. The proposal file remains historical. Geographic extraction, routing, initial physical on-road states, controller/dynamics and operator profiles still need completion. Demand materialization does not resolve those gaps.

A21: the accepted initial on-road population consists of external through travelers; residents start at home. Parked service supply is not included in road density. Households and three occupancy layers are materialized consistently; spatial assignments, initial road history and real demand remain unsupported.
