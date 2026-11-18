# Headless ensemble verification

2026-11-17 · OSPool / OMFB · engineering evidence, not a city experiment

The final source passed **22 tests**. A synthetic 3×3 street grid with a signal, four speed/headway cells and two paired engine seeds produced eight tasks. Sixteen native runs (serial and two concurrent workers) and eight container runs completed. All three collected metrics CSVs agree byte for byte in this fixture. Each case deliberately includes a late vehicle that remains unfinished at the horizon; the complete requested cohort stays in metrics.

The container ran as uid 10001 with Docker networking disabled and no display. It used Python 3.12.16 and SUMO 1.28.0; native verification used Python 3.12.3. Its local image identity is `sha256:c18e92d19b64d36415a5fde7af1935691a460e80cf64b3dc24565d4e89054d0d`. This observation is scoped to these runs, not a cross-platform equivalence guarantee. The first image test exposed missing libXrender/libatomic libraries; adding them resolved native binary startup. The final evidence reflects the repaired image.

The tests also cover mismatched inputs/bindings, changed batch files, unsafe archives, incomplete/oversized factorial designs (rejected before expansion), missing/failed results, inconsistent vehicle ledgers, and fresh-state RNG rejection. Ruff lint and formatting passed; the wheel and source distribution built from the locked build environment. The source fingerprint is `8391b0e99f86c9fa8a830ae71c52b08e0742b0e63cbf32b645b99c32742858ee`. Base Git revision is `a59b4692072f3feca040daf8faafc15c1fa26732`; the new implementation was uncommitted during execution and must not be attributed to that base revision alone.

## Retained evidence

- [Summary and environment identities](htc-verification/summary.json) and [file digests](htc-verification/files-manifest.json).
- [Test log](htc-verification/tests.log), [native verification](htc-verification/native/verification.json), [native metrics](htc-verification/native/collection/metrics.csv), and [collection completeness](htc-verification/native/collection/collection.json).
- The native subtree retains prepared inputs, tasks, reproducible transfer bundles, a non-submitting HTCondor template and eight result archives; serial metrics are retained separately.
- [Offline-container invocation](htc-verification/container/verification.json), [environment](htc-verification/container/doctor.json), [image identity](htc-verification/container/image-identity.json), [metrics](htc-verification/container/collected/metrics.csv) and eight returned result archives.

`htc-local` labels orchestration `local_native_not_container_or_pool`; the container verification command invoked that orchestration *inside* Docker. This is container evidence, never pool evidence. The retained wheel hash identifies the local build; ignored build products and the local Docker image are not a durable archive.

## Scope and next validation

No HTCondor client is installed here, so access-point syntax parsing and a real pool pilot remain unperformed. No image was published and no OSPool jobs were submitted. A configured remote image digest and actual access-point checks are required before submission.

No Phoenix GIS, physical 03:00 population/road realization, reservation policy, communications or faulty/malicious actor adapter was exercised. The native backend seeds only the engine and holds prepared demand/placement fixed. Engine events and ledger-weighted passenger times are explicitly limited metrics; neither safety nor empirical traffic validity follows. Worker eviction restarts from original inputs; distributed complete-state checkpoint continuation remains future work.

Reproduce locally with the README HTC quickstart and the optional SUMO dependencies. To repeat serial/concurrent verification and preserve new evidence, set `HTC_TEST_EVIDENCE` to a fresh directory when running the test suite. Rebuild the wheel/image after source changes; stale worker code is rejected by its fingerprint. On an access point, run `htc-preflight` and `condor_submit -dry-run` against a newly prepared batch before a small authorized pilot.
