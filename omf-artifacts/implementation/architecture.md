# Python and SUMO implementation architecture

Version: 0.1 | Date: 2026-11-17 | Authority: OMFB | Status: initial package implemented

## Accepted stack and boundaries

The user selected Python for scenario/model logic, coordination policies, disruptions, experiments and metrics, with SUMO as the traffic engine. Python 3.12 is the initial interpreter line; the optional engine extra pins the four tested SUMO packages to 1.28.0. This is an implementation choice, not a scientific fitness claim. Julia/Agents.jl is not required by this realization. No additional general ABM framework is introduced.

The currently implemented slice is synthetic demand generation and an engineering checkpoint fixture. The actual Phoenix network backend, policy algorithms and coupled model are not implemented. Numerical assumptions remain external in the accepted JSON benchmark; the package does not discover or overwrite them implicitly.

## Components

- `src/autonomous_traffic/demand.py`: accepted household/person/request materialization, allocation checks and unresolved spatial fields. Scientific input is passed as a configuration dictionary following the benchmark contract; no engine calls occur here.
- `randomness.py`: independent named SHA-256-derived random streams. Preserve the existing stream names and draw order so the refactor does not change accepted realizations.
- `outputs.py`: deterministic JSON/JSONL serialization, content manifest and conflicting-output rejection.
- `cli.py` and `__main__.py`: explicit input/output/seed arguments, environment inventory, error reporting and optional engine dispatch. Console entry point is `autonomous-traffic`.
- `sumo/probe.py`: explicit synthetic network/vehicle/control fixture, native plus external-adapter state save/restore and observed trace comparison. SUMO imports remain inside the invoked probe. This fixture does not provide a Phoenix traffic backend or implement coordination policies.
- `scripts/`: compatibility launchers for the original commands, delegating to the same package code.
- `tests/`: population/conservation/seed checks and CLI/output/error/compatibility checks. Actual engine continuation is an explicit integration probe, not a hidden unit-test dependency.

## Interfaces and next work

Configuration, input assets and output paths are supplied by the caller. CLI inventory does not imply scientific readiness. SUMO remains optional for core materialization; packaging and runtime dependency rules are in pyproject.toml and uv.lock. Source/wheel installation does not embed geographic datasets or scientific defaults in code.

The eventual traffic adapter must preserve constrained policy observations, explicit exogenous inputs, bounded driving physics, finite link storage, boundary accounting and complete checkpoint state. It will require audited geometry/turn/lane rules, actual trip endpoints/routes, physical initialization and control/operator profiles. Return any scientifically consequential change to OMFA. Profile actual coupled runs before selecting libsumo, threading, or a new numerical clock.
