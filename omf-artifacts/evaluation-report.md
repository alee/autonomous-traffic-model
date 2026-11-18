# Evaluation report
Version: 0.7 | Date: 2026-11-17 | Status: draft, unreviewed | Authority: OMFA | Author: Codex with user-supplied intent

## Evaluation Context
Purpose: compare conditional citywide coordination tradeoffs (RQ1–RQ5). Status: initial demand/package checks and a synthetic SUMO checkpoint fixture exist; no Coronado traffic run, calibration, scientific validation or performance comparison exists. The following are scientific evaluation needs, not an engineering verification plan.

## Scope of Evaluation
Artifact consistency, synthetic household/person/request accounting, CLI/packaging and observed continuation on a simple SUMO fixture have been checked. No transport-domain review, actual Coronado behavior or empirical adequacy is established.

## Evaluation Evidence
Engineering checks: ten package/CLI tests and the recorded synthetic checkpoint probes passed; see implementation/python-stack-verification.md and implementation/feasibility-report.md. Calibration: none. Scientific validation: none. Scenario robustness: none. Candidate evidence sources are listed in city-use-cases.md. Contemporary observations can inform baseline plausibility, not future autonomous behavior directly.

## Outcome definitions for later review
- Safety: collision count and exposure, conflict/near-miss measures only if supported by trajectories, hard braking, and unsafe-entry events. Report scenario-level failures and severity proxies separately; no injury estimate without a justified model.
- Efficiency: completed persons and vehicles per interval; person and vehicle travel times including entry waiting; delay relative to a declared reference.
- Reliability: travel-time distribution and upper quantiles, by cohort; report unfinished trips as censored plus unmet demand, never simply drop them.
- Fair access: waits and noncompletion by operator, approach, mode, and zone; neighborhood traffic burden. No demographic claims without appropriate data.
- Resilience: degradation, time to a declared recovery condition, and unrecovered cases; a provisional recovery definition is recorded in experiment-plan.md; no recovery results exist.

## Credibility & Evidence Synthesis
No policy superiority or optimum is established. Compare C0–C4 on matched demand, physical constraints, information conditions, and scenario budgets; expose extra information privileges of reference O. Validate baseline flows, queues, travel times, and spillback with independent times/locations where available. Preserve calibrated alternatives to address equifinality. Any optimized reference must report computational gap or certified bound.

## How Uncertainty Informed the Evaluation
See uncertainty-register.md: vary parameter, structural, and deep scenario uncertainty; keep stochastic precision separate from scenario coverage. Finite zero-collision samples do not prove safety. Claims cannot extend beyond represented physical behavior and tested conditions.

## Fitness for Purpose
The artifacts support design discussion and the scoped accounting/engineering implementation. The hypothetical Coronado benchmark is accepted, while geometric extraction, empirical demand/control evidence, physical realization and final comparison criteria remain incomplete. Changed assumptions require renewed evaluation review.

## Historical Phoenix scope review (0.2)
Reviewed the conceptual/source changes against planned outcomes: citywide interpretation now requires municipal plus external burden accounting and topology coverage. Phoenix data metadata were inspected, but measurements, quality, calibration, and validation remain absent. See data-evidence-assessment.md. experiment-plan.md defines the conditional comparisons and recovery metric, including censoring and incomplete-trip disclosure. Reassessment: scientific inputs support exploratory OMFB planning; empirical city-model or safety validity remains unestablished. No simulation outcomes have been generated.

## Historical initialization and scope review (0.3)
Reviewed the user-directed shift to a quiescent 03:00 start, occupancy-conditioned actors, checkpoint continuation, and configurable AOI. Evaluate initial-state plausibility against the selected occupancy definition and evidence when available. Separate physical initialization, subsequent demand, buildup/analysis windows, and policy interventions. Compare geographic context sensitivity and account for boundary waits/diversion; a subarea simulation cannot establish whole-city benefit. Preserve initial actor history and unfinished trips across checkpoints. Occupancy input categories are resolved as road loading, persons per vehicle, and household population/aggregates. Detailed road measurements, values, materialization and physical/control profiles remain unresolved, so no execution-ready initialization or new empirical/safety claim is established.

## Initial engineering evidence (0.6)
The accepted synthetic demand now materializes 1,000 households, 2,300 residents, 380 resident requests carrying 460 people, and 510 external requests carrying 560 external people. Four generator tests passed for conservation, household/party consistency, stable realizations and rejection of inconsistent inputs. A SUMO 1.28.0 synthetic fixture produced exact observed trace/adapter matches for continuation at 30 and 60 seconds through 160 seconds (260 and 200 compared samples). Coverage includes a passenger, parked/future vehicles, signal state, active speed intervention, queued message and adapter reservation. These are engineering checks, not calibration or scientific validation. No Coronado network, trajectories, city outcomes, safety performance or scalability evidence exists. See implementation/feasibility-report.md and its raw inputs/results.
