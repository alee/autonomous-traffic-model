# Model card
Version: 0.7 | Date: 2026-11-17 | Status: draft, unreviewed | Authority: OMFA | Author: Codex with user-supplied intent

## Model Overview
Name: Autonomous Traffic Coordination under Heterogeneous Trust (working title). Software prototype: 0.1.0. Model status: conceptual with partial implementation; scientific review pending. Type: proposed agent-based network traffic model. Author: Codex; user supplied intent and scope. License, repository identifier, and DOI: undecided/unknown.

## Scientific Purpose
Explore citywide coordination tradeoffs when independent operators, faulty equipment, and deliberate disruption coexist. Intended users: researchers exploring coordination mechanisms. See research-questions.md.

## Conceptual Summary
Individual vehicle decisions, finite link storage, intersection access, route feedback, and delayed/uncertain communication generate network outcomes. Citywide scope and open multiobjective analysis are user-selected; the first hypothetical Coronado AOI and accounting benchmark are accepted. Exact geometry, physical/control realization and broader scenario evidence remain open. See conceptual-model.md, abm-spec.md, and assumptions.md.

## Evaluation Summary
A synthetic demand materializer and small SUMO checkpoint fixture now exist; no Coronado traffic run, calibration or scientific validation exists. Key uncertainties: demand reconstruction, physical and behavioral structure, participation, and adversary capabilities. See evaluation-report.md and uncertainty-register.md.

## Supported Claims and Intended Use
Current support: the documented conceptual model, accepted hypothetical accounting benchmark, reproducible demand materialization and scoped engineering checks. No scientific traffic outcome is established. Intended future use: conditional comparisons across declared scenarios. No predictive traffic improvement, global optimality, deployment safety, or policy recommendation is established.

## Known Limitations
Phoenix selected as the first case under the instruction to proceed. Official source metadata inspected; no feature records acquired, parameters estimated, stakeholder consultation performed, or transport-domain review completed. Multimodal and physical fidelity remain unresolved. See ethics-impact-statement.md and stakeholder-register.md.

## Implementation
A Python package and optional SUMO integration implement the initial accounting and engineering-check slice. Empirical readiness remains incomplete. Implementation artifacts, package source, synthetic demand and scoped fixture results now exist; the Phoenix model remains incomplete. Provenance: fair/provenance-manifest.json.

## Version Summary
Current documentation reconciles the accepted Coronado benchmark and Python/SUMO implementation with the existing evidence limits. Later cities remain proposals.

## Accepted first benchmark and engineering checks (0.6)
Coronado benchmark assumptions were accepted by the user. See first-scenario-proposal.md for scope and implementation/scenarios/coronado-benchmark.json for the active hypothetical recipe. implementation/feasibility-report.md reports engineering evidence only, not model validation.
