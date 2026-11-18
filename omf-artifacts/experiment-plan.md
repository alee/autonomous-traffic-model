# Scientific experiment plan
Version: 0.2 | Date: 2026-11-17 | Status: draft, unreviewed | Authority: OMFA | Author: Codex with user-supplied intent

## Questions and scope
Answer RQ1–RQ5 conditionally for the Phoenix scope in phoenix-case-study.md. No experiment has run. Preserve open objectives; no weighted score or acceptable safety threshold is selected. Use scenario-register.md for hypothetical stress levels and data-evidence-assessment.md for evidence limits.

## Staged comparisons
1. Establish benign network behavior across the three demand scales, operator structures, participation levels, and candidate policies C0–C4. Examine queue and travel-time patterns before selecting informative stress conditions. Reserve saturated regimes rather than filtering them out as inconvenient.
2. Compare S1–S6 separately at matched demand and affected counts. Keep independent-compliant behavior as its own baseline; do not bundle it into disruption.
3. Test S7 and duration, boundary, routing-update, storage, and motion-resolution sensitivity where results warrant. Retain failed scenarios. Track whether selected scenarios were chosen through pilot exploration or held out for final comparison.

Initial pilot: ten matched random realizations per selected cell. Start with demand, departure-time, ownership, and fault-assignment random streams kept distinct. These ten runs provide variance estimates, not an assurance of precision. Freeze final scenario definitions before reporting rankings. Use a separate declared seed list for final comparisons. Pairwise replication and additional runs depend on predeclared precision targets after the pilot; disclose any budget truncation. Never stop solely because a preferred policy becomes significant.

## Candidate interventions and fair comparison
C0 fixed-time traffic service; C1 demand-responsive service; C2 reservation coordination; C3 the same reservation policy with timestamp expiry, observation checks, and fallback; C4 inter-intersection/federated coordination. These are intervention families, not fully specified algorithms. OMFB must flag scientifically consequential rule choices back to OMFA before their results are interpreted. The C2/C3 comparison isolates added safeguards at matched information, except for the explicitly evaluated sensing addition. Include an observation-matched C2 variant to avoid confusing information advantage with protocol benefit.

Reference O has ideal information but the same physical network, demand, and exogenous faults. No benchmark controller can force uncooperative vehicles to obey. Full citywide global optimality may be intractable; report a feasible reference or bound with its actual status. Small-instance exact optima only support local checks, not a claim of a citywide optimum.

## Outcome vector and analysis
Report completions in persons and vehicles; mean and upper-tail travel time including boundary waiting; unfinished requests and their accrued waiting; mode/operator/zone access distributions; queue spillback; and disruption recovery. Keep crash/conflict outcomes explicitly unavailable when motion fidelity cannot support them. Compute trip travel time from request to final destination, not merely network entry to municipal exit.

Define delay against the same trip's uncongested physically feasible path reference, and disclose if that reference is reconstructed rather than observed. Define recovery as affected-zone queue occupancy and completion rate both returning within 10% of their matched undisturbed policy trajectory for 15 consecutive minutes; use absolute floors when reference values approach zero, declared before analysis. Recovery thresholds are exploratory judgments: compare 5% and 20%. Unrecovered runs are censored at the end with residual queues reported. A policy with poor undisturbed throughput cannot earn a strong resilience conclusion from quick recovery alone; report absolute service alongside recovery.

Display scenario-conditional tradeoff fronts and paired differences with replication uncertainty. Noncompletion creates incomparable/censored trip distributions; show completed-trip quantiles alongside unfinished share and cohort waiting. Do not rank by completed-trip delay alone. Pareto dominance must account for direction and reported estimation uncertainty; label apparent dominance as uncertain if precision is inadequate. Keep deep scenario uncertainty separate from replication intervals. Report sensitivity of fronts to demand, occupancy, boundary, and behavioral alternatives. No universal optimum follows from being nondominated in a finite sample.

## Evidence and transition
Calibration and empirical validation remain future activities with separated observations and retained equifinal alternatives. Queue conservation, controller conformance, seed/rerun handling, and software tests belong to OMFB's engineering verification work. The scientific question here is whether represented outcomes and evidence can answer RQ1–RQ5. Review the conceptual model if an implementation cannot preserve the specified heterogeneity or spillback.
