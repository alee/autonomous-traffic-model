# Autonomous traffic coordination: scientific artifacts

Version: 0.7 | Date: 2026-11-17 | Authority: OMFA | Status: living scientific drafts with accepted benchmark choices

These are living documents, created early and revised throughout the project lifecycle. The current stage combines conceptual modeling, evidence assessment and initial engineering implementation. The Python package materializes synthetic demand and tests checkpoint continuation on a separate SUMO fixture. No Coronado traffic simulation, calibration or scientific validation has run.

## Current accepted scope

The overall question concerns citywide coordination under independent operation, partial participation, faults and deliberate disruption. Outcomes remain separate tradeoffs. The first accepted accounting benchmark uses Coronado, a 03:00 quiescent start, a configurable AOI/context and three distinct occupancy layers: road loading, persons per vehicle and household population.

The accepted hypothetical recipe contains 1,000 households, 2,300 residents, 380 resident vehicle requests carrying 460 people, 510 external future requests and a target initial loading of 2 vehicles per eligible lane-kilometer. Resident service vehicles are prepositioned; pedestrian/transit demand is deferred in this first accounting benchmark. These choices do not establish measured Phoenix conditions or broader welfare/safety claims. Exact geometry, initial physical road states, routes, controls and operator profiles remain unresolved.

## Read the current design

- [Research questions](research-questions.md), [conceptual model](conceptual-model.md) and [ABM specification](abm-spec.md).
- [Initial conditions](initial-conditions.md), [Phoenix case](phoenix-case-study.md) and [accepted Coronado benchmark](first-scenario-proposal.md).
- [Active benchmark recipe](implementation/scenarios/coronado-benchmark.json), [configuration contract](implementation/parameter-schema.md), [scenarios](scenario-register.md) and [experiment plan](experiment-plan.md).
- [Assumptions](assumptions.md), [uncertainty](uncertainty-register.md), [data evidence](data-evidence-assessment.md) and [evaluation status](evaluation-report.md).
- [Model card](model-card.md), [stakeholders](stakeholder-register.md), [ethics](ethics-impact-statement.md) and [decision history](decision-log.md).
- [Implementation architecture](implementation/architecture.md), [package verification](implementation/python-stack-verification.md) and [environment notes](fair/python-environment.md).

The proposal JSON under implementation/proposals/ and generic examples under implementation/examples/ preserve their stated historical/draft roles. The accepted recipe above is the materializer's input. Previous revisions and their inspected evidence are retained in [provenance](fair/provenance-manifest.json); version-labeled review sections in other artifacts describe their historical stage unless explicitly current.

## Review triggers and handoffs

Downstream use is gated by explicit status and review triggers. Accepted benchmark choices support their scoped hypothetical implementation; unresolved fields cannot become hidden defaults. Scientific changes route to OMFA, implementation to OMFB, narrative work to document, and packaging/stewardship to FAIR. Changing scientific assumptions requires targeted uncertainty/evaluation review; changing physical or control structure requires renewed implementation/evaluation review. Transport-domain review and suitable empirical evidence are required before credible Phoenix interpretations. Publication-facing ODD documentation remains a document handoff when requested.

Git records the local project. The locked Python environment, commands and scoped deterministic checks are documented; the ignored local .venv is not source. License, repository remote, citation identifiers and external archival remain unresolved. Public source metadata have been inspected, but no real road-feature/traffic dataset has been acquired and audited. The initial synthetic inputs and raw fixture evidence remain preserved.
