# Decision log
Version: 0.6 | Date: 2026-11-17 | Status: draft, unreviewed | Authority: OMFA | Author: Codex with user-supplied intent

| ID | Decision and source | Rationale and alternative | Status / approval |
|---|---|---|---|
| D1 | Citywide road network; user | Capture network coordination; replaces Codex's provisional intersection-first scope before any artifacts were written | Accepted by user selection |
| D2 | Explore tradeoffs without a single priority; user | Avoid prematurely selecting a welfare function; alternative safety-first ranking | Accepted by user selection |
| D3 | Separate independence, compliance, health, connectivity, and intent; Codex | Avoid conflating independent operation with bad faith; alternative single actor-type label | Provisional |
| D4 | ABM with finite road storage and route feedback; Codex | Agent heterogeneity and spillback address RQ2–RQ3; alternative aggregate-only model | Provisional |
| D5 | Bounded adversarial scenario ensemble without attack probabilities; Codex | No prevalence evidence; alternative expected-value optimization | Provisional |
| D6 | Compare feasible C0–C4 policies and ideal-information O; Codex | Separate attainable coordination from information advantage; alternative claim one universal optimum | Provisional |
| D7 | Recommend Phoenix first and contrasting Chicago/NYC later; Codex | Scientific contrast and candidate official data; alternative LA-first or all cities simultaneously | Phoenix-first sequence accepted through user instruction to proceed; later cities remain proposed |
| D8 | Phoenix municipal outcomes with regional route context; Codex | Preserve citywide scope while disclosing external queues; alternative arbitrary small district | Provisional default |
| D9 | Hypothetical 06:00–11:00 study, demand until 10:00; Codex | Observe buildup and recovery; no measured peak claim | 06:00 start superseded by D13; stop/end remain provisional configurable bounds |
| D10 | Bounded S0–S7 scenarios and open outcome vector; Codex | Explicit capability and exposure; alternative unrestricted threat assumption | Provisional default |
| D11 | Separate exploratory realization from empirical Phoenix validity; Codex | Metadata do not establish row quality, OD, or controls; no calibrated-city claim | Provisional methodological commitment |
| D12 | Initially select empty buildup and checkpoint continuation; user | Two supported initialization workflows | Empty-start component superseded by D13; continuation retained |
| D13 | Start quiescent at 03:00 and initialize individual actors from occupancy rates; user | Develop traffic from low activity instead of assuming a 06:00 empty network | Accepted; three occupancy input categories clarified in D16; detailed measures/values unresolved |
| D14 | Configurable geographic AOI; user | Bound computational cost; alternative requiring the whole city in every run | Accepted; extent/context values unresolved; claims limited to represented scope |
| D15 | Clarify occupancy quantity before choosing actor-generation mechanism; OMFA | Road loading, origin activity, and passenger occupancy have different meanings | Resolved by D16 for input categories; detailed measures, values, and mechanisms remain unresolved |
| D16 | Represent road occupancy, people per vehicle, and household population or equivalent aggregates separately; user | Separate initial road loading, carried travelers, and resident population; avoid treating household population as a departure schedule | Accepted input categories; no numerical rates or synthesis mechanism supplied |
| D17 | Coronado reporting AOI with proposed 1,000 m context; Codex | Named City boundaries give a bounded candidate; alternate larger central-Phoenix extract | Accepted by user for first hypothetical benchmark; geometric extraction still pending |
| D18 | 1,000 hypothetical households, 2,300 residents, 380 resident vehicle requests and separate initial/external traffic; Codex | Make three occupancy layers, timing and service availability reviewable | Accepted by user for first hypothetical accounting benchmark; not empirical values |
| D19 | Recommend SUMO feasibility spike; OMFB | External control and native state interfaces fit part of the design; exact continuation and physical-fault behavior remain unproved | Feasibility probe authorized and completed with temporary SUMO 1.28.0; final model/platform fitness still conditional |
| D20 | Record scoped acceptance and implement demand materialization; user / OMFB | Apply accepted inputs without rerouting or creating unresolved physical states | Accepted benchmark; materialized data remain unrouted and not execution-ready |
| D21 | Continue SUMO feasibility work after exact observed fixture continuation at 30 s and 60 s; OMFB | Compare 260 and 200 post-save samples through 160 s, including adapter state | Observed engineering evidence only; no universal continuation or Phoenix validity claim |

No exceptions authorized. Remaining evidence gaps: geometric extract/context extent, physical/behavioral values, raw demand/control data, multimodal measurements, and independent evaluation. These limit empirical interpretation. Scientific defaults are sufficient for exploratory OMFB planning; changes to these commitments route back to OMFA.
