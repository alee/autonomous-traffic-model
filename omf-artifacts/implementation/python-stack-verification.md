# Python package and stack verification

Version: 0.1 | Date: 2026-11-17 | Authority: OMFB | Status: observed implementation evidence

## Implemented scope

The user selected Python for model logic/experiments and SUMO for traffic dynamics. The working source is now an installable src-layout package with a console CLI. Demand algorithms, stream names, input bytes and accepted numerical assumptions were preserved. Legacy script commands delegate to the same implementation. Core runtime dependencies are empty; SUMO is an optional pinned extra. Architecture and module mapping are documented alongside this report. See ../fair/python-environment.md for the scoped packaging/environment record.

## Checks and observed results

- Ten tests passed: the four original household/person/request/seed tests plus six CLI checks covering recorded-output equivalence, invalid JSON, output-conflict preservation, negative seeds, inventory reporting and the legacy launcher.
- Fixed-seed materialization on CPython 3.12.3 retained every recorded data/summary/output hash. CLI tests compare scientific records and summary fields while allowing only the recorded Python patch-version metadata to differ on another supported interpreter patch.
- `uv lock --check --offline` passed. `uv sync --extra sumo` resolved the pinned engine and build environment from the public PyPI registry. No private registry credentials were embedded.
- Source distribution and wheel built with `uv build --no-build-isolation` using the locked development build tools.
- The installed wheel in a separate clean core-only environment imported and materialized the benchmark without SUMO/TraCI. Its output hashes matched the reviewed realization. Its engine command failed clearly before creating output when optional dependencies/binaries were absent.
- The packaged CLI executed the synthetic SUMO checkpoint probe in the locked full environment. Native engine plus adapter state restored at 30 s and 60 s and exactly matched 260 and 200 observed samples respectively through 160 s. All seven fixture coverage checks passed, including actual carriage of a passenger, parked/future vehicles, a light controller, active fault, queued message and adapter reservation.

The exact observed environment was CPython 3.12.3, uv 0.12.7, Linux x86_64; SUMO, TraCI, sumolib and sumo-data were 1.28.0. Raw packaged-command inputs, snapshots, adapter states and traces are preserved under spike-results/python-package-0.1.0/. The earlier script-only probe remains separate historical evidence. The script used a localhost TraCI connection requiring an execution-sandbox socket override; it did not access real road infrastructure.

## Reproduction from the repository

```sh
uv sync --locked --extra sumo
uv run --locked --extra sumo python -m unittest discover -s tests -v
uv run --locked --extra sumo autonomous-traffic doctor
uv run --locked --extra sumo autonomous-traffic materialize --config omf-artifacts/implementation/scenarios/coronado-benchmark.json --output /tmp/coronado-demand --seed 20261117
uv run --locked --extra sumo autonomous-traffic checkpoint-probe --output /tmp/traffic-checkpoint-probe
uv build --no-build-isolation
```

Use a fresh or identical output directory for materialization. Core-only use omits the sumo extra. Original script paths remain usable from a checkout; installed CLI inputs remain explicit. Test outputs/builds/environments are local artifacts, not a published release.

## Limits

No Coronado network or initial on-road vehicle realization has been built, and no Phoenix policy comparison has run. The native checkpoint test proves equality only for observed traces and adapter state in its simple synthetic fixture on the tested environment; it does not establish restoration of every hidden engine state or portability to other models, platforms, releases or thread counts. Physical fault realism, citywide scaling, safety, empirical calibration and validity remain unestablished. Language/packaging selection changes none of these scientific limits.
