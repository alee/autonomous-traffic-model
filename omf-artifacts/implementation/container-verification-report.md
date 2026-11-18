# Shared container and command verification

2026-11-18 · OSPool / OMFB / FAIR · engineering checks only

**39 tests passed**, including scenario/GIS/HTC regressions and new transport/image checks. Ruff lint/format and justfile formatting passed. The full OCI image built from source without a host wheel. Docker and non-setuid Apptainer both executed the bundled scenario shift, metric GIS planning and complete eight-task engineering workflow.

A separate shared-input comparison used identical frozen cases/tasks under native Python, Docker and Apptainer. All three collected metrics CSVs match **byte for byte** across eight tasks. The generated HTCondor worker script was also executed inside Apptainer with exactly its transferred task/bundle basenames; its task metrics match the corresponding Docker result. No driving mechanism or parameter was changed for this execution comparison.

## Exercised behavior

- Docker runs as the calling non-root numeric uid/gid, with a read-only image filesystem, writable scratch/work volume, and networking disabled. No host source/venv is mounted. Explicit copy-in/export works with Docker Desktop; normal host bind mounts are unavailable in this environment.
- Public bundled examples work for non-root users. An early permissions failure was corrected before the final image/SIF; these examples are now readable and their directories traversable.
- The Docker input workspace remains intact, application failures export diagnostics, output overwrites/nesting are rejected, and transport failures cannot report success. Unit checks cover failure cleanup of only the created container/volume.
- SIF conversion exports the resolved OCI image ID and records both source identity and SIF bytes. Apptainer uses clean environment/containment and the explicit work directory. Host networking remains available; network isolation is not claimed for Apptainer.
- Local SIF staging uses a content-derived filename, preflight rejects modified bytes, and HTCondor's generated wrapper invokes only the model CLI. Remote OSDF image references require content-derived names; their remote bytes are explicitly unverified by local planning.

## Environments and retained evidence

Native Python: 3.12.3. Image Python: 3.12.16. SUMO: 1.28.0. pyproj: 3.7.2. just: 1.59.0. Apptainer: 1.5.5. The official tool release downloads were checksum checked. just and non-setuid Apptainer were installed under the user's local prefix; the isolated Apptainer installation uses local dependency libraries and adjusted loader paths, recorded separately. No system packages or setuid helpers were installed.

[Summary](container-verification/summary.json), [image configuration](container-verification/image.json), [SIF conversion lineage](container-verification/sif-conversion.json), [test log](container-verification/tests.log) and [file digests](container-verification/files-manifest.json) identify the verification epoch. `shared-inputs/` retains the portable fixture and planned task/control files; re-plan from its sweep into a fresh directory to execute it. The native/docker/apptainer subtrees retain matched results and completeness reports. `job-transfer/` preserves the generated worker, transferred inputs and actual single-job outputs. Container workspace receipts identify runtime, exact image/SIF, commands and status.

The application SIF is retained locally at ignored `dist/containers/model.sif`, with sidecar identities. Larger raw runtime workspaces and the staged SIF batch are retained under ignored `runs/container-verification/`. Compact reviewed evidence remains tracked. Preserve exact images and raw inputs before sharing/archiving a study; a future recipe rebuild is not a guaranteed identical image.

Base Git revision: 161868c6f688ceef5f9b5c05610bea673198e921. This work includes the previously uncommitted GIS/scenario slice plus an uncommitted container extension; the recorded package source fingerprint identifies the actual executed Python source. Do not attribute it to the base commit alone.

## Remaining deployment checks

No HTCondor client exists here, so `condor_submit -dry-run` and a scheduler-managed pilot remain outstanding on the intended access point. The recorded preflight verifies local image/task/input/control digests and reports parser absence. The worker-in-Apptainer check verifies the executable/transfer contract; it is not a Condor submission. No registry image was published, no OSDF object uploaded, and no pool job submitted. Access-point capability, transfer/storage allocation, remote image bytes and resource requests need an actual pilot.

These fixtures do not simulate Coronado, evaluate coordination/fault/malicious-actor policies, establish traffic or safety validity, or implement full distributed checkpoint continuation. Existing accepted benchmark and raw GIS evidence are preserved.
