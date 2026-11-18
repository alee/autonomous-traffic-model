# Initial scenario register
Version: 0.2 | Date: 2026-11-17 | Status: draft, unreviewed | Authority: OMFA | Author: Codex with user-supplied intent

All numbers are modeler-selected exploratory stress levels, not estimates of Phoenix conditions or attack probability. Keep scenario prevalence separate from its conditional outcome. No real system access or attack execution is part of this work.

## Common dimensions
- Demand: 0.75, 1.0, and 1.25 times a declared reference demand table. The reference is hypothetical until evidence-backed. Demand scale is not a guarantee of light/saturated traffic; classify achieved traffic states after pilot observation.
- Coordination participation: 0%, 50%, and 100% of vehicles are enabled for the evaluated protocol. Nonparticipants retain explicit ordinary right-of-way interactions; a reservation policy must explain how these are served.
- Operating policies: compare independent-compliant versus cooperative routing at matched enabled shares. Use three equal-share fleets plus private operators as an initial illustrative ownership structure and test one dominant fleet as an alternative. Fleet share alone is not maliciousness.
- Affect 0%, 1%, or 5% of physically present vehicles at event onset for vehicle faults/disruption; round nonzero fractions up to one vehicle and report realized fraction. Cap at the available population. In correlated cases choose a fleet-consistent subset rather than random independent draws.
- Event timing: onset 07:30, active for 15 minutes, physical/network aftermath observed through 11:00. Compare 5 and 30 minutes for duration sensitivity. Honest behavior resumes when an event ends, but queues and stopped vehicles clear through represented dynamics rather than disappearing.

## Families
| ID | Mechanism and capability | Matching control | Main question |
|---|---|---|---|
| S0 | No injected fault or adversary; vary operator independence and participation | Same trips and ownership | Cost/benefit of coordination under benign heterogeneity |
| S1 | Communications outage: affected vehicles receive/send no coordination messages during event; normal local sensing/actuation | Same affected identities, healthy communication | Graceful fallback and compatibility |
| S2 | Declared intentions remain stale until event ends; observations still arrive subject to the common sensing model | Same message budget and sensing | Can observed behavior correct misleading commitments? |
| S3 | Vehicle becomes stopped within bounded deceleration and remains obstructing its occupied road space until event end | Same location and onset without fault | Local failure and queue propagation; crash risk requires suitable dynamics |
| S4 | Affected participants request one feasible reservation at a time and intentionally fail to use it; one persistent identity each, no forged priority | Same request opportunities, honest use | Capacity wasted through bad-faith protocol use |
| S5 | Same-fleet correlated S1 or S2 at the matched total affected-vehicle count | Independently selected affected vehicles | Common cause versus isolated failure |
| S6 | One coordinator in a high-betweenness candidate zone unavailable for event; compare random-zone location | Healthy controller at same demand | Infrastructure failure, spillback, recovery |
| S7 | Bounded combination of one vehicle-event family and S6 | Both constituent events separately | Interacting vulnerabilities beyond one-factor tests |

All policies see the same event assignment and realized physical exposure where compatible, but not hidden intent labels. Protocol-specific disruptions apply only where protocol-enabled vehicles exist; record nonapplicable cells rather than pretending equivalent impact on a signal-only system. Match actor capabilities, not achieved damage. Adaptive targeting, spoofed identities, forged emergency priority, coordinated physical collision attempts, and network-wide compromise are outside this initial ensemble; they remain explicit untested threats. No robustness claim covers them.

Controller outage removes decision/communication service; it does not remove vehicles or queues. The fallback's service rule and information limits must be declared in the ABM specification before runs. Centrality-based targeting requires a defined road graph; never choose the worst target after seeing final policy performance without treating that selection as a separate adversarial search.
