# Python package and environment capture

Version: 0.2 | Date: 2026-11-17 | Authority: FAIR | Scope: narrow implementation packaging/environment task

The managed object here is the local `autonomous-traffic-model` Python software, version 0.1.0. This note records the scoped packaging/environment work; it is not a project-wide FAIR assessment or management plan. Scientific input and generated evidence remain governed by the existing OMFA/OMFB artifacts. No release or external publication has been requested or performed.

## Authoritative files and observed environment

`pyproject.toml` is the package/build/dependency declaration. `uv.lock` records the resolved dependency distributions and hashes; `.python-version` selects Python 3.12. Code is under `src/autonomous_traffic`. Exact observed interpreter: CPython 3.12.3 on Linux x86_64. Tested uv: 0.12.7. Supported interpreter declaration is initially >=3.12,<3.13; other interpreter lines/platforms are unverified. Lockfile entries for other operating systems do not establish tested portability.

Core runtime dependencies: none. The `sumo` extra pins eclipse-sumo, traci, sumolib and sumo-data to 1.28.0. The development group pins hatchling 1.27.0 and Ruff 0.17.5; its resolved transitive build dependencies are captured in uv.lock. Use the locked development environment with `uv build --no-build-isolation` for the recorded build workflow. Interpreter patch version, operating system, native binary identity, floating-point behavior and full dynamic state remain relevant to exact simulation continuation. A package lockfile alone does not establish bitwise scientific reruns.

## Installation, execution and preservation

From the repository root, use `uv sync --locked --extra sumo`, then include `--locked --extra sumo` on uv engine/test commands. For core-only work use `uv sync --locked`; SUMO imports are lazy and the installed wheel was tested without the optional packages. Dependencies are sourced from the public PyPI registry; no credentials/private registry URLs are embedded in the lockfile. Virtual environments, caches, build distributions and new run directories are excluded by .gitignore. Reviewed evidence under omf-artifacts remains visible.

Preserve source, pyproject.toml, uv.lock, the Python/runtime identity, accepted configuration bytes, input/output digests and original scientific inputs with any shared run. The initial generated dataset remains unchanged by the package migration. Local compatibility launchers retain the earlier script invocation paths. Configuration remains an explicit external file; a wheel does not bundle the Phoenix network or all scientific artifacts. The source distribution includes the accepted benchmark configuration, tests and launchers; it is not a complete scientific archive.

## Unknowns and boundaries

The local project is initialized with Git on main for its first source snapshot. Repository remote, software license, creator/citation metadata, persistent identifiers and external archive remain unknown/unassigned. Exact commit IDs are recorded by Git; historical pre-Git provenance revisions correctly remain unknown. No license is inferred from SUMO or other dependencies, and no publishing/citation files are fabricated. These are follow-ups for a release or broader stewardship task. Full FAIR planning/assessment, cross-object metadata harmonization and release archival are outside this narrow packaging slice. Implementation and model validity limits are in ../implementation/python-stack-verification.md.

## Cleanup checks
Ruff formatting/import cleanup preserves the source function ASTs and the accepted configuration/generated data bytes. Ten tests, lint and formatter checks are required before the initial commit. The local .venv, caches, build products and new runs remain ignored; reviewed generated inputs and raw engineering evidence are retained.

## HTC environment extension

The canonical stewardship scope now includes cross-object execution lineage; see fair-management-plan.md. `deploy/htcondor/requirements.lock` is a hash-pinned runtime-only export of uv.lock, not an independent dependency authority. The Dockerfile consumes a built project wheel and a digest-pinned Python base, with explicit SUMO native libraries. Apt package resolution is not fully archived, so rebuilding the recipe alone does not guarantee identical image bytes. Preserve and use an immutable published image digest for remote runs. A local image was exercised without networking; details and observed environment are in ../implementation/htc-verification-report.md. No image was published, and OSPool execution remains untested. Base Git revision and actual worktree code fingerprint are recorded separately; the new HTC code has not yet been committed.

## Optional geographic preparation stack

`geo` pins pyproj 3.7.2; its certifi dependency and distribution hashes are in uv.lock. GIS commands disable PROJ network access and use explicit metre-based projected CRS definitions. `doctor` inventories pyproj availability. Neither core demand materialization nor HTC workers require geo. Runtime worker requirements remain the SUMO-only export; rebuild a worker after package source changes because the source fingerprint covers the whole package. Prior container evidence remains historical for its recorded source fingerprint, not evidence of this new source image.

## Shared application image (2026-11-18)

The current runtime export includes both sumo and geo; the earlier SUMO-only worker export is historical. A separate build-requirements.lock export captures the dev/build environment used inside the Docker build stage. The Dockerfile now builds its own wheel from source; host dist/ wheels are unnecessary. Source OCI identity, SIF file digests, conversion receipts and per-workspace runtime receipts preserve execution lineage. See implementation/container-workflow.md and the canonical FAIR plan. No image publication or OSPool execution is implied by a local image digest.
