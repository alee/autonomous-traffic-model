# FAIR Management Plan

Version 0.3 · 2026-11-18 · FAIR authority · working plan, no release

This is the canonical stewardship plan for the project's software, prepared inputs, execution workflow and results. Scientific model definitions remain under OMFA in ../model-card.md and related specifications; this plan records their management and references them without replacing their contents.

## Project and responsibility

Project: Autonomous traffic coordination under heterogeneous trust. Working repository: this Git checkout. The modeler owns scientific decisions and repository stewardship; named PI, long-term steward, funding, retention commitment and archive destination are unassigned. Codex performed the documented implementation and author checks. No external submission, publication or image upload is authorized by this plan.

## Research object inventory

Inventory keys below are stable local references, not persistent identifiers.

| Key | Object | Location | Current status |
|---|---|---|---|
| model | Scientific model and accepted benchmark | ../model-card.md, ../implementation/scenarios/ | Specified in part; city model incomplete |
| software | Python package, tests, dependency/build declarations | src/, tests/, pyproject.toml, uv.lock | Local source; GIS/container extensions uncommitted at authoring |
| coronado-inputs | Accepted hypothetical household/person/request realization | ../implementation/generated/coronado-demand/ | Synthetic; spatial fields unresolved |
| prepared-fixture | Native SUMO engineering cases, network and request ledger | ../implementation/htc-verification/native/inputs/ | Synthetic; not Phoenix GIS or calibrated traffic |
| htc-workflow | Headless preparation, task/transfer/collection contract | ../implementation/htc-workflow.md, src/autonomous_traffic/htc/, deploy/htcondor/ | Locally verified; pool execution untested |
| runtime-image | Shared application environment, OCI and SIF formats | deploy/htcondor/; local dist/containers/; identities in container verification evidence | Locally built/tested Docker and non-setuid Apptainer; unpublished |
| htc-results | Native and container execution evidence | ../implementation/htc-verification/, ../implementation/container-verification/ | Engineering verification; no policy or city findings |
| gis-source | Public OSM road/restriction snapshot | runs/coronado-gis/source/; metadata in ../implementation/gis-verification/ | Acquired; local raw data, ODbL attribution retained |
| gis-network | Derived SUMO road network and full diagnostic audit | runs/coronado-gis/build/; compact reviewed evidence in ../implementation/gis-verification/ | Converted; geographic/control/attribute review outstanding |
| gis-workflow | Scenario parameterization and GIS preparation | ../implementation/gis-workflow.md, src/autonomous_traffic/scenario.py, src/autonomous_traffic/gis/ | Locally tested, proposed geometry only |

Paths starting src/, tests/ or deploy/ are relative to the repository root. Supporting management documents are not additional independent research objects.

## Findability and metadata

Git history, stable local inventory keys, SHA-256 file manifests, prepared-case/task JSON and provenance-manifest.json provide local discovery and identity. Task identity includes case bytes, package source fingerprint, replicate and engine seed. Case provenance declares GIS source, initial parameterization, scope and input-realization identity. No DOI, SWHID, ORCID, citation metadata or archive registration is claimed. Repository publication and search indexing require a later release decision.

## Accessibility and preservation

Keep source, accepted configurations and compact reviewed engineering evidence in Git; ignore transient runs, virtual environments, caches and build artifacts. Preserve batch plans, tasks, input bundles, result archives, collection completeness and runtime image digest with any shared ensemble. Keep failed/missing-task records alongside successful results. No external archival deposit or retention service has been arranged. Export/preserve the actual worker image before relying on future availability; the build recipe alone is insufficient.

## Interoperability

Use UTF-8 JSON/JSONL, CSV, SUMO XML, gzip/tar, POSIX wrappers and HTCondor submit descriptions. The prepared-case format is project-specific version 1 with an explicit executable validator and human input contract. GIS acquisition/CRS, clipping, topology and source licensing must be recorded when real inputs are prepared. The present native adapter does not claim compatibility with arbitrary SUMO configurations or the eventual external controller state.

## Reusability, provenance and quality

Use README.md, implementation/htc-workflow.md and prepared-sumo-inputs.md as entry points. Scientific documentation owns interpretation; the engineering fixture tests execution mechanics only. The append-only provenance manifest records actual skill contributors, authorization, changed file hashes, prior revisions, execution environment and limitations. A base Git revision is separate from uncommitted source fingerprints. Record frozen demand/placement realizations separately from engine seeds; paired seeds do not ensure identical random draw paths across cases. Report unfinished cohorts and completeness before comparing results. Independent review and empirical validation remain outstanding.

## Computational environment

Python 3.12 and pinned SUMO 1.28.0, declared in pyproject.toml/uv.lock. The runtime requirements export is derived from that lock. Docker base is digest pinned; apt library versions are resolved at build time. Use a published immutable image digest for OSPool. Native and offline-container evidence records observed identities; it does not establish bitwise portability across platforms. HTCondor parser/access-point and distributed execution checks remain pending. See python-environment.md and ../implementation/htc-verification-report.md.

## Licensing and citation

Project license, ownership and citation metadata remain unresolved; no license is inferred from dependency licenses. SUMO/dependency distributions and any future GIS data retain their own terms. Before redistribution, record a license inventory, verify GIS attribution/derivative-data obligations, select project licensing with the owner, and add verified citation metadata. No license inventory or release metadata is fabricated in this task.

## Resources, security and ethics

Initial jobs request one CPU, 2 GiB memory and 4 GiB disk as unprofiled pilot values. The application's 256 MiB prepared-input and 10,000-task guards are implementation limits, not OSPool quotas. Profile actual AOI cases before allocating an ensemble; use supported cached/OSDF delivery for larger shared GIS assets in a later extension. No OSDF adapter exists yet. Current fixtures contain synthetic households and engineering traces. Future household/travel data may need aggregation, access control and output disclosure review; do not publish real household routes by default. Successful worker results omit per-trip XML; failures retain diagnostics, requiring review for sensitive future inputs. Keep credentials outside inputs/images/logs. Backups currently depend on the user's local repository arrangements; no managed backup is claimed.

## FAIR assessment and follow-up

| Principle | Present support | Remaining work |
|---|---|---|
| Findable | Local inventory, hashes, Git, traceable task IDs | Verified metadata, persistent identifiers and archive |
| Accessible | Local reproducible inputs and compact evidence | Published/licensed objects; image and data availability |
| Interoperable | Open serialization and explicit versioned adapters | Real GIS provenance, broader model adapters |
| Reusable | Locked dependencies, tested execution, stated scope | Licensing, calibrated inputs, independent review, pool pilot |

This is a scoped stewardship self-assessment, not a full FAIR score or a publication-readiness judgment. A separate detailed FAIR assessment is deferred to release preparation. No derived DMP/SMP is maintained; any future extract must follow this plan.

## Review history

0.1 (2026-11-17): introduced the cross-object HTC inventory, execution lineage, preservation strategy and explicit release gaps. Revisit when actual GIS data, new policy adapters, remote execution or a release is introduced.

## Geographic data stewardship update (0.2)

The OSM acquisition is now an inspected dataset, distinct from the earlier official-source metadata inventory. Retain raw source, full converted network and full audit locally under ignored runs/coronado-gis, with SHA-256 identities, snapshot time, requested coverage, query, URL, attribution/license, converter command/version and warnings in compact tracked evidence. Changing an online query cannot reproduce an old snapshot; archive exact raw/derived bytes before distributing a study. Raw OSM was requested without contributor user metadata. No external archive or dataset publication has occurred. The proposed geometry and conditional vehicle count are not scientific approvals. Parameterized scenario variants retain base/override digests and configured/unreviewed status; accepting a base does not accept all variants. License details are in license-inventory.md. Preparation adds a pinned optional GIS environment and open JSON/GeoJSON/OSM XML/SUMO XML artifacts. Review this plan before a data release or new acquisition source.

## Shared container and command stewardship update (0.3, 2026-11-18)

The justfile remains a thin operator interface; CLI/configuration are authoritative. A single source-built OCI image contains pinned SUMO/GIS dependencies. The SIF is a derived format of that same runtime-image object, not a separate scholarly object. Preserve the OCI image identity, source fingerprint, SIF bytes/digest, conversion receipt, dependency/build exports and execution receipts with a study. Apt resolution is not a byte-reproducible environment specification; retain the actual images. Local mutable tags are resolved to exact IDs; remote OCI use requires a manifest digest. Local SIF batches stage content-derived filenames and verify bytes, while OSDF references record expected content identity without claiming a remote-byte check. Replacing bytes behind a cached name is unsupported; publish a new digest-derived name. No image publication, OSDF upload or pool submission has occurred.

Docker Desktop workspace transport uses temporary volumes and explicit copied snapshots; preserve input identity and complete exported failures. Apptainer uses a clean contained environment and host-network semantics; it is not claimed to enforce offline networking. The canonical execution workflow is ../implementation/container-workflow.md. Current verification and tool versions are in ../implementation/container-verification-report.md. just and a non-setuid Apptainer were installed under the user's local prefix for testing; neither is a model dependency in the application image. Preserve actual installed tool identities for reproducibility; no system/setuid package installation occurred. Review after runtime/HTCondor/OSDF changes and before publication.
