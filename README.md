# Autonomous Traffic Coordination

A computational modeling project exploring how autonomous vehicles could coordinate across a city when vehicles have different operators, incomplete information, equipment failures, and sometimes conflicting intentions.

The central question is: **which coordination rules improve travel across the network, and how do those improvements hold up when cooperation breaks down?** The first case study is Phoenix, Arizona. We want to compare the consequences of different rules for travelers, operators, and neighborhoods, keeping their tradeoffs visible.

## What we want to learn

“Optimal traffic” depends on whose experience we measure. A policy might move more vehicles through an intersection while increasing pedestrian waits, diverting traffic into a neighborhood, or leaving one operator's passengers waiting longer. We will examine travel time, reliability, throughput, fair access, and recovery from disruption separately. Safety outcomes will require enough physical detail to support their measurement.

The goal is to identify where coordination policies work well, what they cost, and the conditions under which they fail. Any claim of optimality will be tied to stated objectives, constraints, information, and scenarios.

## How the proposed model works

The model will represent individual vehicles and their driving policies within a connected road network. Each vehicle has a destination, route, operator, observations, and physical limits. Roads have finite space: a queue can fill a link and block traffic upstream. Vehicles can change routes as conditions change, allowing local decisions to produce congestion or relief elsewhere in the city.

We will compare conventional traffic signals, signals that respond to demand, systems that reserve intersection access, and coordination between intersections and vehicle operators. An ideal-information reference will help examine the cost of limited information, subject to the same physical constraints and disruptions.

The initial agents are explicit decision rules. Learning agents or language models could be considered later if they help answer a specific research question.

## Independence, faults, and bad faith

The model treats these as separate dimensions of behavior:

- **Independent operation:** vehicles or fleets pursue their own travel goals while following the rules.
- **Partial participation:** some vehicles cannot or choose not to use a coordination protocol.
- **Malfunction:** sensing, communications, actuation, or a shared fleet system fails.
- **Deliberate disruption:** actors send misleading intentions, reserve access they do not use, or obstruct traffic within declared physical limits.

For example, a missed intersection reservation could result from a communications outage or intentional noncompliance. A coordinator must respond using the observations and messages available to it. It cannot look up an actor's true intentions. Experiments will also examine failures affecting an entire fleet or a traffic coordinator, and measure how queues and service recover afterward.

## First case: Phoenix

The overall study targets citywide coordination in Phoenix. Each run will configure an area of interest, from a subarea to the whole city, plus surrounding roads and boundary traffic needed to represent connecting routes, arrivals, and queues. This allows us to manage computational cost while keeping each result tied to the area actually modeled. Burdens outside the reporting area will remain visible.

The initial state will be quiescent at 03:00, with individual actors generated from explicit occupancy-based inputs. Those inputs describe road occupancy, people per vehicle, and household population or equivalent aggregates. The accepted Coronado accounting benchmark supplies hypothetical household, passenger and departure profiles; physical/geographic realization and empirical support remain incomplete. Checkpoints will allow an established simulation to resume with its full state preserved. The first proposed experiments follow the buildup into a hypothetical weekday morning. Traffic demand, participation, operator behavior, and disruption severity will vary across scenarios. Transit and pedestrian crossings are part of the intended representation; broader welfare claims depend on representing their needs adequately. Chicago and New York are candidates for later comparisons, with Los Angeles an option for a stronger focus on freeway and surface-street coordination.

## Current status

This repository contains the scientific design, an accepted hypothetical Coronado benchmark, an installable Python package, a reproducible synthetic demand generator, a small SUMO checkpoint test, and a headless ensemble runner. **Coronado has not yet been simulated.** Official data-source metadata have been inspected, but road connectivity, trip demand, signal timing, and measurement coverage still need assessment. Initial numerical scenarios are hypothetical stress tests, not estimates of Phoenix traffic or malicious behavior.

A first OSM-derived road network has been acquired and audited under a proposed Coronado rectangle. The next stage is reviewing geometry and conversion assumptions, assigning routes to the generated requests, and completing traffic controls and physical initialization. Calibration and independent evaluation will be needed before drawing conclusions about Phoenix. Collision-avoidance claims will require suitable vehicle trajectories and physical modeling. The current work supports research design and early engineering tests; real-world control and deployment safety remain outside its demonstrated scope.

## Explore the scientific design

- [Scientific artifact guide](omf-artifacts/README.md)
- [Research questions](omf-artifacts/research-questions.md) and [conceptual model](omf-artifacts/conceptual-model.md)
- [Agent-based specification](omf-artifacts/abm-spec.md) and [initial conditions](omf-artifacts/initial-conditions.md)
- [Configuration and checkpoint contract](omf-artifacts/implementation/parameter-schema.md)
- [Phoenix case study](omf-artifacts/phoenix-case-study.md) and [data evidence assessment](omf-artifacts/data-evidence-assessment.md)
- [Disruption scenarios](omf-artifacts/scenario-register.md) and [experiment plan](omf-artifacts/experiment-plan.md)
- [Assumptions](omf-artifacts/assumptions.md), [uncertainty](omf-artifacts/uncertainty-register.md), and [evaluation status](omf-artifacts/evaluation-report.md)
- [Stakeholders](omf-artifacts/stakeholder-register.md), [ethical considerations](omf-artifacts/ethics-impact-statement.md), and [scientific decisions](omf-artifacts/decision-log.md)

These are living documents. This overview summarizes the proposed model; the linked scientific artifacts record its assumptions, open questions, and revisions.

## Command interface and containers

Use `just --list` to discover commands. Native development uses `just setup`, `just check`, and `just model <CLI arguments>`. Change the baseline clock with `just scenario 04:00:00 runs/scenario-0400.json`.

Build and exercise the full application in Docker:

```sh
just image-build
just docker-demo runs/docker-demo
```

The image builds the package from source and includes SUMO, GIS dependencies and read-only example configurations. No host Python packages or prebuilt wheel are needed for the image build. Local Docker transport uses the host's Python 3.11+ standard library; the model runs in the image. Docker runs offline by default. Each invocation preserves an input workspace and exports to a fresh output workspace, with no Docker Desktop bind-mount dependency.

For Apptainer and HTCondor:

```sh
just sif-build
just apptainer-demo runs/apptainer-demo
just condor-plan path/to/sweep.json runs/pool-batch
just preflight runs/pool-batch
```

Apptainer must be installed for SIF build/local execution; HTCondor manages the runtime on pool workers. `TRAFFIC_IMAGE` and `TRAFFIC_SIF` select local images. Planning records image identities and emits submit descriptions; it does not submit jobs. See the [container workflow](omf-artifacts/implementation/container-workflow.md) for workspace examples, immutable OSDF/OCI deployment and validation limits.

## Install and run

The implementation uses **Python for model logic and experiments, with SUMO for traffic dynamics**. Python 3.12 is the initial supported interpreter line. The package's demand-generation core has no runtime dependencies; the optional `sumo` extra pins SUMO, TraCI, sumolib, and sumo-data to 1.28.0.

From the repository root, using [uv](https://docs.astral.sh/uv/):

```sh
uv sync --locked --extra sumo
uv run --locked --extra sumo autonomous-traffic doctor
uv run --locked --extra sumo python -m unittest discover -s tests -v
uv run --locked ruff check src scripts tests
uv run --locked ruff format --check src scripts tests
uv run --locked --extra sumo autonomous-traffic materialize --config omf-artifacts/implementation/scenarios/coronado-benchmark.json --output runs/coronado-demand --seed 20261117
```

The materialization command creates households, people, and trip requests with unresolved spatial fields. It does not run Phoenix traffic. Keep the accepted recipe separate from generated run outputs. Use a new output directory when changing the seed or configuration; conflicting outputs are rejected.

To run the separate synthetic checkpoint probe:

```sh
uv run --locked --extra sumo autonomous-traffic checkpoint-probe --output runs/checkpoint-probe
```

Use `uv sync --locked` for the core-only environment. Include `--extra sumo` on uv commands that need the engine. The `doctor` command reports environment availability; it does not establish model readiness. The original scripts in `scripts/` remain compatible entry points, and `python -m autonomous_traffic` exposes the same CLI after installation.

See the [implementation architecture](omf-artifacts/implementation/architecture.md), [package verification](omf-artifacts/implementation/python-stack-verification.md), and [environment notes](omf-artifacts/fair/python-environment.md). The earlier [feasibility report](omf-artifacts/implementation/feasibility-report.md) preserves the initial evidence and its limits.

## Headless parameter sweeps

The HTC runner executes independent prepared SUMO cases and engine-seed replicates. GIS conversion, physical initialization, demand construction and scientific review happen before workers run. Each job receives a checksummed input bundle and returns compact metrics and a run receipt. Native SUMO is headless; no display or worker-side package download is required.

Exercise the complete workflow locally with a synthetic engineering fixture:

```sh
uv run --locked --extra sumo autonomous-traffic htc-demo --output runs/htc-inputs
uv run --locked --extra sumo autonomous-traffic htc-plan --sweep runs/htc-inputs/sweep.json --output runs/htc-batch
uv run --locked --extra sumo autonomous-traffic htc-local --batch runs/htc-batch --jobs 2
uv run --locked --extra sumo autonomous-traffic htc-collect --batch runs/htc-batch --output runs/htc-collected
```

Without a worker image, planning emits `sweep.submit.in`, an explicitly non-submitting template. Supply an immutable worker image reference to render `sweep.submit`, and run the access-point preflight before any pilot submission. The demo varies native vehicle speed/headway settings on a synthetic grid; it does not replace the accepted Coronado initialization or implement reservation/coordinator policies.

See the [HTCondor/OSPool workflow](omf-artifacts/implementation/htc-workflow.md), [prepared-GIS input contract](omf-artifacts/implementation/prepared-sumo-inputs.md), [worker Dockerfile](deploy/htcondor/Dockerfile), and [verification evidence](omf-artifacts/implementation/htc-verification-report.md). Scientific ranges and acceptance criteria remain explicit study decisions.

## Parameterize the start and prepare street data

The 03:00 start is an editable scenario setting. Shift it together with every departure/horizon clock, and optionally override road density, vehicle occupancy, household histograms and demand profiles:

```sh
uv sync --locked --extra sumo --extra geo
uv run --locked --extra sumo --extra geo autonomous-traffic scenario-configure --base omf-artifacts/implementation/scenarios/coronado-benchmark.json --start-local 04:00:00 --overrides omf-artifacts/implementation/gis/scenario-overrides.example.json --output runs/scenario-0400.json
```

The generated variant records its inputs, recalculates accounting totals, and preserves the accepted baseline. Shifting clock labels alone preserves the elapsed demand profile; different time-of-day traffic requires explicit profile changes. Midnight rollover is supported through service-day hours such as 29:00 for 05:00 the following day.

The [GIS preparation workflow](omf-artifacts/implementation/gis-workflow.md) provides `network-plan`, `network-fetch`, `network-import` and `network-build`. A first OSM extract and SUMO conversion have been audited under a proposed Coronado rectangle; see [GIS verification](omf-artifacts/implementation/gis-verification-report.md). Boundary geometry, inferred lane/speed/access and synthesized signals require review before routing or physical initialization. The package's optional `geo` extra is for preparation; workers remain offline.
