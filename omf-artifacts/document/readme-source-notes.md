# Root README: source and framework notes

Version: 0.6 | Date: 2026-11-17 | Status: draft, unreviewed | Authority: document

## Classification and framework selection

Model type is the proposed agent-based network traffic model established by OMFA. The requested output is a human-readable repository introduction. Use a structured project overview, with links to scientific specifications, instead of a full ODD+2 protocol: no simulator is implemented and the user requested an initial root README. This is not a formal ODD narrative or a substitute for a future implementation description.

## Source inventory and extraction

| README subject | Authoritative source | Extraction and status |
|---|---|---|
| Purpose and open tradeoffs | research-questions.md, model-card.md | Proposed conditional comparisons; no universal objective selected |
| Vehicles, operators, road queues, routing feedback | conceptual-model.md, abm-spec.md | Proposed entities/states and processes; no code exists |
| Agent logic and information | abm-spec.md, phoenix-case-study.md | Explicit driver rules; intent hidden from controllers; learning/LLMs optional future work |
| Independence, faults, deliberate disruption | scenario-register.md, abm-spec.md | Separate dimensions with bounded scenarios; shared failures and recovery included |
| Phoenix boundary and morning scale | phoenix-case-study.md | Target municipal network plus regional context; hypothetical time window |
| Outputs and claims | evaluation-report.md | Travel time, reliability, throughput, access, recovery; safety depends on physical detail |
| Data and maturity | model-card.md, phoenix-case-study.md | Metadata only; no runnable code, calibrated parameters, or evaluation results |

Parameters and stochastic settings remain in the linked specifications. The overview does not invent values, algorithms, distributions, execution commands, or implementation names. Intended processes are described in future tense.

## Unknowns and source qualifications

No source-code inventory is possible because there is no implementation. Actual topology coverage, trip demand, signal timing, physical parameters, software environment, and empirical validity remain unresolved. Earlier paragraphs in the conceptual model and evaluation report retain pre-refinement uncertainty about geography and readiness; their explicit Phoenix/0.2 refinement sections and phoenix-case-study.md establish the latest conditional scope. This README follows those recorded refinements without editing or resolving OMFA scientific commitments. No new scientific finding is asserted.

## Observed versus inferred

Observed: the inspected artifacts specify the proposed entities, scope, comparisons, limitations, and lack of results. Narrative choices: paragraph order and plain-language examples summarize those commitments. The missed-reservation example illustrates mechanisms already represented, not an observed incident.

## Review

Checked that proposed behavior stays distinct from implemented behavior and that local README links resolve. Scientific approval, independent domain review, and empirical evaluation remain outstanding. Provenance is appended to ../fair/provenance-manifest.json with source hashes and actual contributing skills.

## Initialization refinement
The user-directed quiescent 03:00 start, occupancy-conditioned individual actors, checkpoint continuation, and configurable AOI are now described in the root README. Source authority is the revised initial-conditions.md, Phoenix case, ABM specification, and decision log. The user clarified road occupancy, persons per vehicle, and household population/aggregates as separate inputs. Detailed road measurement, numerical profiles, exact geography, and engine realization remain unresolved. This meaning-preserving narrative reconciliation does not adopt a numeric rate or initial actor-generation mechanism.

## Three-profile clarification
The README follows user-approved occupancy categories in initial-conditions.md version 0.4 and the updated decision log. It makes no claim about measured rates or a selected synthesis/departure algorithm.

## Acceptance and engineering implementation
The user accepted the Coronado accounting benchmark. README wording now distinguishes the working standard-library demand generator and synthetic SUMO checkpoint probe from the still-incomplete Phoenix model. Sources are the accepted scenario recipe, scripts/tests, generated summary and implementation/feasibility-report.md. No city validation or universal state-restoration claim is introduced.

## Python package and locked environment
The user selected Python + SUMO. README installation and CLI commands now reflect the implemented package, optional pinned SUMO extra, uv lockfile and verified core-only path. Sources are pyproject.toml, src/autonomous_traffic, implementation/architecture.md, implementation/python-stack-verification.md and fair/python-environment.md. Scientific benchmark inputs and the incomplete Phoenix model status are preserved.

## Pre-commit cleanup
Current summaries were reconciled with the already-accepted benchmark and recorded engineering evidence; historical review sections are labeled. Python sources were formatted without changing function ASTs, accepted parameters or generated input bytes. README quality-check commands match the pinned Ruff development dependency. No scientific conclusion, model mechanism or benchmark scope was changed.
