# Initial engine assessment

Version: 0.3 | Date: 2026-11-17 | Authority: OMFB | Status: documented capability assessment, not a runtime benchmark

## Selected implementation stack

Recommend a SUMO feasibility spike for the initial traffic engine, with an external adapter for coordination, household/traveler accounting, observations, communications and scenario events. The user subsequently selected Python + SUMO; the implemented package pins its optional SUMO/TraCI stack to 1.28.0. The initial pre-install inventory below was followed by the documented feasibility probes. Model-specific fitness remains conditional; the Coronado traffic model is incomplete.

| Candidate | Inspected support | Fit and unresolved work |
|---|---|---|
| SUMO | TraCI can inspect/change vehicle, person and signal state; state save/load documented | Strong candidate for the represented network and control problem. Custom reservation/communication/household state remains external; performance and exact continuation must be measured |
| CityFlow | Documentation targets large-scale microscopic multi-agent RL traffic with configurable networks/flows and Python control | Plausible alternative for traffic-signal optimization; full project checkpoint/person/physical-fault requirements not established by the inspected pages. Do not infer unsupported absence or use published speed comparisons as this project's benchmark |
| CARLA | Recorder documents recording and reenactment of actors/traffic lights | Candidate if sensor/perception/3D vehicle interaction becomes central. Recorder replay alone does not establish complete project checkpoint continuation; map/population/scale fit not evaluated here |

Sources: [SUMO TraCI](https://sumo.dlr.de/docs/TraCI/), [SUMO state saving](https://sumo.dlr.de/docs/Simulation/SaveAndLoad.html), [SUMO safety behavior](https://sumo.dlr.de/docs/Simulation/Safety.html), [CityFlow introduction](https://cityflow.readthedocs.io/en/latest/introduction.html), [CityFlow quick start](https://cityflow.readthedocs.io/en/latest/start.html), [CARLA recorder](https://carla.readthedocs.io/en/latest/adv_recorder/). Inspected 2026-11-17; stable documentation pages, not a selected installed release.

## Checkpoint feasibility requirements

SUMO documents explicit options for saving RNG and person state; these cannot be presumed enabled. Future departures still depend on original inputs. Its state page lists internal lane-change/car-following state and parking-position limitations, and RNG state has platform restrictions. Thus a native state file is not proof of exact project continuation. Pair native state with external adapter state, immutable future inputs and cumulative accounting; test the chosen release, dynamics and precision before making a checkpoint equivalence claim. If relevant internal state cannot be restored, document the limitation and revisit model/platform choice; do not weaken the accepted complete-continuation requirement silently.

## Physical-fault fidelity

SUMO safety documentation makes collision interpretation and intervention settings consequential: minimum-gap events differ from physical overlap; junction checks and collision response need explicit configuration. Default protective behavior can mask the intended physical consequences of a fault, while forced control can create unrealistic physics. Record and verify the chosen configuration against bounded dynamics, including whether vehicles are teleported, removed, stopped or continue after an event. A configurable collision mechanism is not evidence of realistic injury or deployment safety.

## Feasibility spike before model implementation

1. Use a small synthetic engine fixture solely to test capabilities, clearly separate from the Phoenix scientific AOI. Pin/record the exact candidate engine and Python adapter versions.
2. Exercise one vehicle, a carried person, a parked future service vehicle, a pending departure, traffic-light state, one queued message and an adapter-held reservation. Add a bounded stop/outage rather than assuming engine defaults realize the threat model.
3. Compare uninterrupted and resumed execution through the same end time. Check trajectories, route/control/observation memory, all relevant RNG streams, pending inputs, person/household membership, reservations, event counters and cumulative trip metrics. Test multiple save boundaries, including active events and boundary queues.
4. Reject a checkpoint continuation that changes hidden state or loses accounting. Confirm whether omitted engine state affects the selected models, rather than claiming universal support or universal incompatibility.
5. Inspect actor/link counts and runtime for increasing fixture sizes. Only measured behavior should determine threading, TraCI/libsumo choice, timestep and AOI budget. No runtime estimate or scalable-city claim has been established.

The spike is independent of accepting the hypothetical Coronado demand values. Scientific contradictions return to OMFA; release packaging and archival route to FAIR when the platform is selected.

## Feasibility probe result
After the earlier inventory, SUMO/TraCI/sumolib/sumo-data 1.28.0 were installed in an isolated temporary environment and the checkpoint fixture ran on Linux. Observed trace and adapter equality passed at both save times. This is evidence for proceeding with SUMO investigation, not proof for all models/releases or an accepted final platform for scientific claims. See feasibility-report.md and spike-results/sumo-1.28.0/summary.json.
