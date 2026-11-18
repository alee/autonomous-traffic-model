# Headless HTC exploration with HTCondor and OSPool

Version: 0.1 | Date: 2026-11-17 | Authority: OSPool / OMFB | Status: initial implementation; production inputs and pool preflight outstanding

## Execution model

One job is one prepared parameter case and one replicate. The planner expands a finite factorial design, requires exactly one prepared case per parameter cell, and schedules an explicit engine seed per replicate. Corresponding replicates use the same seed across cases. Seeds are independent of scheduler process numbers or execution order. Each task is content-identified by its prepared case, worker code, replicate and seed; task files, case archives and generated batch control files carry digests.

The initial backend runs native SUMO 1.28.0 on Linux x86_64 using one CPU, explicit simulation/physical-observation settings and prepared inputs. It supports native signal programs and behavior already encoded in those inputs. It does not implement the Python reservation/coordinator/communications layer, generate city geography, rebuild household demand, or apply ignored arbitrary parameter overrides. Every swept parameter binds to an attribute in declared prepared XML. A case builder must compile high-level household/load/participation/fault choices into a scientifically consistent realization before such choices can be studied here; not every high-level study parameter is expressible through the current native-attribute binding interface.

## Prepare data once

Follow prepared-sumo-inputs.md. Convert and audit GIS on a preparation machine, retain network/source/initialization identities, materialize explicit routes and the request ledger, and provide a fresh quiescent SUMO physical state for a traffic experiment. Empty starts are restricted to engineering fixtures. Preserve the configured reporting AOI, surrounding roads, boundary flows, lane/turn/time-dependent access, scope and data-source evidence. Do not download a street map or install packages per worker.

Each case is an immutable file set. Current direct input budget is 256 MiB uncompressed per bundle, an implementation limit rather than an OSPool policy claim. Larger/shared datasets need an explicit OSDF/cache staging design before scaling; this worker does not silently fetch URLs. Preserve case archives while a batch is queued/running. No local home-directory paths, credentials or shared writable outputs are required on workers.

## Local validation

The root README provides `htc-demo`, `htc-plan`, `htc-local` and `htc-collect` commands. The engineering demo creates four prepared speed/headway cells and two seeds, giving eight tasks. It is separate from Coronado and supplies no scientific parameter recommendation. `htc-local --jobs 1` and `--jobs 2` use the same isolated worker contract. Use fresh batch/collection directories; existing output attempts are not overwritten by local tooling.

`seed_scope` is explicitly `sumo_engine_only`. Initial population and route/departure inputs remain fixed within each prepared case. Different seeds do not imply different household demand, nor necessarily different trajectories for deterministic dynamics. Build separate input-realization designs when the scientific question requires variability in household/trip construction. Equal engine seeds are not proof of matched event sequences when model behavior changes draw consumption.

## Build the worker image

`deploy/htcondor/Dockerfile` pins the base image by digest, builds the project wheel in a separate stage, and installs hash-pinned SUMO/GIS runtime requirements. It includes the shared libraries required by the headless SUMO binary; no GUI/display service is started. The container runs as an unprivileged user, and all per-job writes go to scratch.

```sh
just image-build
```

The runtime requirement export is derived from uv.lock, not independently edited:

```sh
uv export --locked --extra sumo --extra geo --no-dev --no-emit-project --format requirements-txt --output-file deploy/htcondor/requirements.lock
```

Rebuild after source changes: the worker rejects a task if installed Python source fingerprints differ. Keep the resulting immutable image identity and native engine/runtime evidence with the batch. A local Docker image ID is not a remotely pullable registry manifest digest. Image publication/OSPool provisioning is a separate user-authorized action; no image is published by planning.

## Render and check an access-point batch

After provisioning an approved image, replace the following placeholder with its actual immutable registry reference:

```sh
uv run --locked --extra sumo autonomous-traffic htc-plan --sweep path/to/sweep.json --output runs/pool-batch --image docker://REGISTRY/WORKER@sha256:ACTUAL_MANIFEST_DIGEST
uv run --locked --extra sumo autonomous-traffic htc-preflight --batch runs/pool-batch
```

The image argument rejects mutable tags. Without an image URI or --sif input, only a `.submit.in` template is written. The plan does not call condor_submit. `htc-preflight` checks batch digests and invokes only `condor_submit -dry-run` if the client exists and an image was configured; it reports absent/unrun syntax validation explicitly. On the intended access point, inspect the generated file and run:

```sh
cd runs/pool-batch
condor_submit -dry-run classads.txt sweep.submit
```

The generated submit file uses modern HTCondor container universe, explicit file transfer, an immutable image, isolated result remapping, one CPU, requested memory/disk, and Medium duration category. It targets access points supporting container universe; it is not a compatibility claim for older HTCondor releases. A single queue is sufficient for independent jobs; no DAG is required for the manual collect-after-completion workflow. Submit externally only after user authorization, image verification and a small access-point pilot.

## Results, failures and restarts

Each worker writes a run receipt with input/code identities, explicit settings, engine version and wall time. Success adds counts, completed-trip request-to-arrival times, a precisely labeled nearest-rank completed p95, ledger-weighted person metrics, unfinished counts/fraction and accumulated unfinished request time. Unfinished/undeparted requests remain in the cohort. Person counts are ledger weights, not independently verified passenger-carriage observations. Registered engine collision events are not a safety guarantee. No automatic policy winner or Pareto ranking is inferred.

The initial compact return contains aggregate metrics and diagnostic logs. Successful per-trip XML is not retained; choose a separate reviewed output policy before studies that require individual-trip reanalysis. Failure receipts and available diagnostics are archived too. Nonzero exits are held for inspection rather than silently retried indefinitely. `htc-collect` validates returned identities/digests, writes metrics.csv plus a completeness report, and returns a nonzero status for missing, failed or invalid tasks.

OSPool eviction can restart a job from its original immutable inputs. This native worker does not claim distributed checkpoint/restart or use `checkpoint_exit_code`; the earlier project checkpoint fixture does not establish full HTC continuation. Keep tasks short enough for the selected category. This initial worker bounds the engine subprocess at at most 32,400 seconds; default demo requests one hour, 2 GiB memory and 4 GiB disk as unmeasured pilot allocations. Profile memory, disk and wall time on the pool before larger submissions. Do not release/resubmit a completed batch into existing returned results; create a new batch/attempt directory to preserve earlier evidence.

## Before real exploration

Required: scientifically reviewed GIS/network and physical initialization, complete native parameter cases, explicit stochastic/input-realization design, final study ranges/metrics, working immutable worker image, account/access point/storage allocation, actual HTCondor syntax preflight and a small pool pilot. These are visible readiness items rather than invented defaults. Container/local fixture verification does not validate Coronado traffic or establish OSPool throughput.

## Inspected primary execution references

- [OSPool Python jobs and containers](https://portal.osg-htc.org/documentation/software_examples/python/manage-python-packages/)
- [OSPool file transfers](https://portal.osg-htc.org/documentation/htc_workloads/managing_data/file-transfer-via-htcondor/)
- [OSDF large-data/container staging](https://portal.osg-htc.org/documentation/htc_workloads/managing_data/osdf/)
- [OSPool duration categories](https://portal.osg-htc.org/documentation/htc_workloads/workload_planning/jobdurationcategory/)
- [OSPool checkpointing](https://portal.osg-htc.org/documentation/htc_workloads/submitting_workloads/checkpointing-on-OSPool/)
- [HTCondor container universe](https://htcondor.readthedocs.io/en/23.0/users-manual/container-universe-jobs.html)

Pool policy and access-point support must be checked at deployment; no live submission was made during setup.

## Current Docker / Apptainer / just interface

See container-workflow.md for the current source-built full application image, Docker Desktop workspace transport, SIF conversion, local and OSDF-backed HTCondor plans. In addition to immutable OCI references, --sif stages and checksums a local image; remote OSDF SIF references require a content-derived filename. No nested runtime launch occurs in the job wrapper. Earlier OCI-only instructions above describe the initial interface.
