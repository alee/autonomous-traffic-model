# One application image: just, Docker, Apptainer and HTCondor

2026-11-18 · OSPool / OMFB · no pool submission or image publication

The Python CLI remains the authority for parameters, validation, execution and metrics. `justfile` supplies short commands. `scripts/containers.py` handles runtime transport and workspace receipts, not scientific behavior. A single multi-stage Dockerfile builds the installed wheel and runtime; Apptainer converts that exact OCI image into SIF. The full runtime includes the locked SUMO and optional GIS stacks, so scenario generation, GIS preparation and headless execution share one application environment.

## Tools and build

Recipes target a POSIX shell, including WSL. Use just >=1.39 (tested 1.59.0), Docker with Linux/amd64 support, and Python >=3.11 for the standard-library host transport helper. Native recipes, including planning/preflight, additionally use uv; it is unnecessary for `just image-build` or container runs. SIF creation/local execution additionally needs an installed, working non-setuid Apptainer (tested 1.5.5). HTCondor is needed on the intended access point for parser preflight/submission, not inside the application image.

```sh
just --list
just image-build
just docker-demo runs/docker-demo
```

The Dockerfile is `deploy/htcondor/Dockerfile`. Its build stage installs hash-pinned build dependencies and builds the project wheel from source. Runtime dependencies are a hash-pinned `uv.lock` export including sumo and geo. Native system libraries are explicit; their apt versions are not fully frozen, so preserve the built image/SIF rather than equating a recipe rebuild with identical bytes. The base image is digest pinned. Both exports are derived files:

```sh
uv export --locked --extra sumo --extra geo --no-dev --no-emit-project --format requirements-txt --output-file deploy/htcondor/requirements.lock
uv export --locked --only-group dev --no-emit-project --format requirements-txt --output-file deploy/htcondor/build-requirements.lock
```

The runtime has no entrypoint/default command. HTCondor supplies its executable; local recipes explicitly invoke the installed CLI. The image defaults to uid 10001, and the Docker helper runs as the calling host's numeric uid/gid to preserve output ownership. `/work` supports arbitrary uids; public bundled examples are readable by non-root users. Code is installed in the image, never mounted from the source checkout. Rebuild after source changes: workers reject mismatched package fingerprints. Local mutable image tags are resolved to image IDs before execution/export; remote OCI references must include a manifest digest.

## Local workspaces

```sh
just docker - runs/start-2200 scenario-configure --base /opt/traffic/examples/coronado-benchmark.json --start-local 22:00:00 --output scenario.json
just docker runs/start-2200 runs/map-plan network-plan --config /opt/traffic/examples/gis/coronado-network.proposed.json --benchmark scenario.json --output geometry
```

`just docker INPUT OUTPUT <CLI arguments>` uses `-` for an empty input workspace. All model paths are relative to `/work`, apart from explicit image examples under `/opt/traffic/examples`. INPUT is preserved; OUTPUT must be fresh and outside INPUT. Output includes all copied input data and newly generated results, so a subsequent invocation can consume it. This is intentional workspace snapshotting, not an incremental file-build system. Use small explicit workspaces; copying a large city dataset for every exploratory command can be expensive.

Docker Desktop cannot always bind the agent's filesystem path. The helper uses an anonymous writable `/work` volume and Docker file transfer instead. The image filesystem is read-only, `/tmp` is scratch, and networking defaults to none. It removes only its own temporary container and volume. Application failures still export the workspace and record a nonzero exit; export failures cannot report success. Each output contains `.container-runs/` receipts with exact image identity, command, runtime and result status. User workspace paths containing spaces are supported; colons, commas and newlines are rejected as ambiguous transport syntax.

Use `just docker-online INPUT OUTPUT network-fetch ...` only for explicit GIS acquisition. The model and simulation workers never install packages/download maps at runtime. The demo checks bundled scenario parameterization, metric geometry planning and the complete four-cell/two-seed engineering workflow. Its grid and numerical settings remain fixtures, not city parameters.

## The same image as SIF

```sh
just sif-build
just apptainer-demo runs/apptainer-demo
```

The helper exports the exact local image ID with `docker image save` and calls `apptainer build` on that archive. It detects whether the installed Apptainer supports `--ignore-proot` and uses it where available (older OSPool access-point guidance requires it). Build/cache temporary directories are explicit and honor APPTAINER_TMPDIR; on an access point follow its scratch/cache policy before building. The normal workflow builds locally and transfers the completed SIF to the access point, so Docker is not needed there.

The default output is `dist/containers/model.sif`, with `.sif.sha256` and `.sif.json` files recording its bytes and source OCI identity. Existing SIF names are never overwritten. Use a new filename when rebuilding, then set TRAFFIC_SIF accordingly:

```sh
just sif-build dist/containers/model-v2.sif
TRAFFIC_SIF=dist/containers/model-v2.sif just apptainer - runs/check-image doctor
```

Local Apptainer runs use clean environment/containment, an explicit workdir/bind, and fresh copied output workspaces. SIF bytes are checksummed in receipts. Apptainer networking uses the host by default; containment does not imply an isolated network namespace. Do not interpret the local `offline Docker` test as proof of network isolation under Apptainer. Worker code still needs no network. Linux user namespaces/runtime configuration must work on the execution host; no privileged/setuid helper is installed by this repository.

## HTCondor with Apptainer

Prepare scientifically reviewed case inputs as documented in prepared-sumo-inputs.md. Freeze them with the same package source used in the image:

```sh
just condor-plan path/to/sweep.json runs/pool-batch
just preflight runs/pool-batch
```

`--sif` stages a local image as `images/worker-<sha256>.sif` in the batch. The plan records its digest and preflight rejects mutation. The container_image setting makes HTCondor transfer the local SIF automatically; it is intentionally absent from transfer_input_files. Generated jobs use container universe, `/work` as the target scratch directory, Linux amd64 and HasSingularity requirements. The worker script runs the installed model directly; it must not launch Apptainer or Docker inside an already managed container. Local SIF staging is for pilots, not repeated multi-gigabyte transfer at ensemble scale.

For larger ensembles, place the SIF in the access point's supported OSDF data location under its content-derived name and prepare a new batch:

```sh
just condor-plan-image path/to/sweep.json runs/osdf-batch osdf:///ospool/AP/data/USERNAME/worker-ACTUAL_64_CHARACTER_SHA256.sif
```

Replace placeholders with real values; the parser requires an actual 64-digit lowercase digest in the filename. OSDF caches by name, so changing image bytes requires a new name. The URI is recorded as content-named but its remote bytes are not downloaded/verified by local planning. Verify the staged remote object yourself before a pool pilot. Actual worker source fingerprints and native version checks still apply. An immutable `docker://REGISTRY/IMAGE@sha256:DIGEST` reference is also supported.

Preflight validates task, input, control and local-image hashes and invokes only `condor_submit -dry-run` when available. It explicitly reports missing parser validation. No recipe auto-submits, uploads a SIF, or publishes a registry image. On the access point, inspect the submit file, run the actual parser, then use a small authorized pilot before scaling. Job eviction still restarts from immutable inputs; complete distributed checkpoint continuation remains future work.

## Evidence and claim scope

See container-verification-report.md for executed Docker/Apptainer checks, native comparisons, failures and outstanding access-point validation. These are engineering fixtures, not new traffic-policy findings. Existing GIS/scenario work and accepted benchmark remain preserved.

Primary references: [just positional arguments](https://just.systems/man/en/positional-arguments.html), [Apptainer OCI/SIF conversion](https://apptainer.org/docs/user/main/docker_and_oci.html), and [OSPool container execution and image transfer](https://portal.osg-htc.org/documentation/htc_workloads/using_software/containers/).
