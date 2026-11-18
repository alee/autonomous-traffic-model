# Python and SUMO implementation architecture

Version: 0.1 | Date: 2026-11-17 | Authority: OMFB | Status: initial package implemented

## Accepted stack and boundaries

The user selected Python for scenario/model logic, coordination policies, disruptions, experiments and metrics, with SUMO as the traffic engine. Python 3.12 is the initial interpreter line; the optional engine extra pins the four tested SUMO packages to 1.28.0. This is an implementation choice, not a scientific fitness claim. Julia/Agents.jl is not required by this realization. No additional general ABM framework is introduced.

The implemented slices are synthetic demand generation, an engineering checkpoint fixture, and a native-SUMO headless ensemble runner for explicitly prepared cases. The actual Phoenix network backend, policy algorithms and coupled model are not implemented. Numerical assumptions remain external in the accepted JSON benchmark; the package does not discover or overwrite them implicitly.

## Components

- `src/autonomous_traffic/demand.py`: accepted household/person/request materialization, allocation checks and unresolved spatial fields. Scientific input is passed as a configuration dictionary following the benchmark contract; no engine calls occur here.
- `randomness.py`: independent named SHA-256-derived random streams. Preserve the existing stream names and draw order so the refactor does not change accepted realizations.
- `outputs.py`: deterministic JSON/JSONL serialization, content manifest and conflicting-output rejection.
- `cli.py` and `__main__.py`: explicit input/output/seed arguments, environment inventory, error reporting and optional engine dispatch. Console entry point is `autonomous-traffic`.
- `sumo/probe.py`: explicit synthetic network/vehicle/control fixture, native plus external-adapter state save/restore and observed trace comparison. SUMO imports remain inside the invoked probe. This fixture does not provide a Phoenix traffic backend or implement coordination policies.
- `htc/inputs.py` and `plan.py`: validate checksummed prepared cases, freeze factorial tasks and paired engine seeds, and render portable HTCondor transfers.
- `htc/worker.py`, `local.py` and `collect.py`: isolated native engine execution, bounded local concurrency, compact result receipts and complete-cohort collection. No controller/TraCI policy adapter is implemented by this runner.
- `htc/demo.py`: synthetic engineering inputs; never a source of city defaults. `deploy/htcondor/` captures the container build.
- `scripts/`: compatibility launchers for the original commands, delegating to the same package code.
- `tests/`: population/conservation/seed checks and CLI/output/error/compatibility checks. Actual engine continuation is an explicit integration probe, not a hidden unit-test dependency.

## Interfaces and next work

Configuration, input assets and output paths are supplied by the caller. CLI inventory does not imply scientific readiness. SUMO remains optional for core materialization; packaging and runtime dependency rules are in pyproject.toml and uv.lock. Source/wheel installation does not embed geographic datasets or scientific defaults in code.

The eventual traffic adapter must preserve constrained policy observations, explicit exogenous inputs, bounded driving physics, finite link storage, boundary accounting and complete checkpoint state. It will require audited geometry/turn/lane rules, actual trip endpoints/routes, physical initialization and control/operator profiles. Return any scientifically consequential change to OMFA. Profile actual coupled runs before selecting libsumo, threading, or a new numerical clock.

## Scenario and GIS preparation extension

`scenario.py` creates explicit hypothetical variants with a shifted service-day clock and nested overrides, recalculating derived accounting totals and validating demand before writing. It preserves the accepted baseline and does not inherit its approval for variants. `gis.prepare` plans projected rectangular AOI/context geometry, acquires or imports OSM, and invokes pinned netconvert offline. `gis.audit` measures clipped external passenger-lane lengths and topology diagnostics without automatic pruning. `gis.api` is separate from the worker API. Optional pyproj 3.7.2 belongs to the `geo` preparation extra, not the worker runtime requirements. See gis-workflow.md and gis-verification-report.md. Geographic geometry is proposed; no actual traffic initialization has been implemented.

## Shared container and command interface

`justfile` is the developer/operator entry point; scientific values and execution remain in Python. `scripts/containers.py` handles Docker Desktop-compatible workspace transport, Apptainer execution and OCI-to-SIF lineage. The multi-stage image builds from package source and includes locked SUMO/GIS dependencies and public example configurations. `htc.plan` accepts content-staged local SIFs or content-named OSDF SIF URLs, requires Apptainer capability for those images and uses HTCondor-managed containers without nested runtime launches. See container-workflow.md for boundaries and container-verification-report.md for actual checks.
