# Scientific-to-implementation mapping

Version: 0.1 | Date: 2026-11-17 | Authority: OMFB | Status: initial package slice

| Scientific commitment / input | Implementation | Current evidence / limit |
|---|---|---|
| Accepted hypothetical Coronado household, passenger and request totals | scenarios/coronado-benchmark.json; autonomous_traffic.demand | Original generator tests pass; no geography or actual road traffic materialized |
| Separate household residents, resident parties and external travelers | demand.materialize | Unique IDs, distinct parties, seat bounds and totals checked; no household/person duplicated across simultaneous requests |
| Stable exogenous realizations and independent random sources | randomness.random_stream; demand allocation | Fixed-seed output agrees with prior recorded data; runtime version remains explicit |
| Explicit output provenance and preserved unrealized spatial fields | outputs.write_outputs | JSON/JSONL and byte digests; routes and geometry stay null rather than being invented |
| Complete checkpoint requirements | sumo.probe plus external adapter state | Observed equivalence on a simple synthetic fixture only; not proof for the eventual scientific model |
| Explicit scenario/run inputs and optional engine | cli.main; pyproject.toml | Core-only wheel works; engine command requires optional dependencies and binaries |
| Physical vehicles, finite road storage, geographic AOI, route choice and real coordination | Future network/engine adapter and policy modules | Not implemented; do not infer from the engineering fixture |
| Experiments, robustness ensembles and scientific comparisons | Future experiment runner | No scientific policy comparison has run |

Scientific authority remains ../abm-spec.md, ../initial-conditions.md, ../assumptions.md and the accepted Coronado benchmark. The package refactor changes execution structure, not those commitments.

## Headless ensemble implementation

Prepared network, explicit routes, optional fresh initial state and passenger ledger enter through `htc.inputs.validate_case`. `htc.plan.prepare` enumerates finite cases × replicates with immutable identities; `htc.worker.run_task` executes SUMO; `htc.collect.collect` reports every expected task. See htc-workflow.md and prepared-sumo-inputs.md. The earlier “future experiment runner” row now applies to scientific policy comparisons: generic native batch mechanics are implemented, while controller, fault and malicious-actor model adapters remain future work. The engine seed changes native runtime randomness only; demand and initial placement are frozen inputs.
