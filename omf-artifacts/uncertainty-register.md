# Uncertainty register
Version: 0.6 | Date: 2026-11-17 | Status: draft, unreviewed | Authority: OMFA | Author: Codex with user-supplied intent

## Parameter Uncertainty
U1: demand profiles, occupancies, reaction/control lag, braking, loss and latency. No measured ranges selected. Separate natural variation from missing knowledge; use evidence-supported distributions only after data review. Until then, clearly labeled bounded sweeps are illustrative.

## Structural Uncertainty
U2: queue-based versus trajectory traffic representation; route-choice adaptation; fallback rules; centralized versus federated authority. Compare alternative structures where conclusions change. Safety ranking is unsupported without physical conflict representation. Test time resolution and boundary placement.

## Scenario Uncertainty
U3: malicious share, capabilities, collusion, shared software faults, controller compromise, participation and operator incentives are deep uncertainties. Compare bounded scenario families without assigning unsupported probabilities. Cross isolated/correlated failures, benign/adaptive disruption, and light/congested demand. Report vulnerabilities and regret relative to scenario-specific references rather than one expected optimum. Robustness statements apply only to enumerated scenarios and declared ranges.

## Data Limitations
U4: public counts and probe speeds may be asynchronous, sparse, biased, or historical. Network geometry and control data may be incomplete. Demand reconstruction uncertainty can reverse policy rankings. No dataset has been evaluated yet.

## Calibration Ambiguity & Equifinality
U5: demand, routing, and capacity may compensate for each other. Preserve multiple plausible parameter sets; evaluate against independent patterns and held-out locations/times. Calibration is not validation.

## Sensitivity and disclosure
Screen demand, participation, storage, braking/observation limits, communication loss, fault duration, and disruption budget; examine interactions and alternate structures. Pilot replications establish Monte Carlo precision targets before comparative claims. Separate replication intervals within a scenario from uncertainty across scenarios. Report worst observed scenario, tail delays, failed runs, and incomplete trips. Do not average away catastrophic outcomes. Sensitivity analysis has not been run.

## Phoenix refinement review (0.2)
The source-assessment change is incorporated: feature records, temporal coverage, network codes/connectivity, and reuse terms remain unverified. No raw count acquisition succeeded. The planning year is not an observation year. Border routing, preload/buildup, hypothetical OD patterns, fleet concentration, and persistent identity are added sensitivity dimensions. Scenario-register.md bounds the initial exploratory ensemble; experiment-plan.md separates pilot precision from final inference. No uncertainty has been converted into an evidence-backed probability by this revision. Future calibration and sensitivity artifacts must use this evidence assessment; none exist yet.

## Initial-state and AOI review (0.3)
Quiescent 03:00 is a user-selected modeling starting point, not evidence of measured low traffic. The user selected road occupancy, persons per vehicle, and household population as separate input layers. Detailed road measurement, values/distributions, and conversion into consistent individual actors remain unresolved. Household population does not determine travel without departure, destination, mode, and sharing assumptions; multiple such combinations can fit initial road loading. Initial speeds/routes, prior trip ages, queue/control state, and future-demand reconciliation can change outcomes. Configurable AOI introduces boundary truncation and context/flow uncertainty; compare expanded context and preserve geographic scope in interpretation. Checkpoint continuation requires complete realized state and compatible policy/engine to avoid introducing a hidden second initialization. No numerical profile or probability is inferred by this change.

## Accepted benchmark inputs versus uncertainty (0.6)
User acceptance fixes hypothetical values for the first Coronado accounting experiment; it does not reduce uncertainty about actual household sizes, departure patterns, road loading, destinations, control, or vehicle behavior. Prepositioned vehicles, one departure per selected household, initial external-only road users and deferred pedestrian/transit demand restrict interpretation. A successful simple engine continuation probe does not remove state-restoration risk for untested dynamics or adapter extensions. See implementation/feasibility-report.md.
