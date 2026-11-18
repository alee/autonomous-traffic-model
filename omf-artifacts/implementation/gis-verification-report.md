# Scenario and GIS preparation verification

2026-11-17 · OMFB / FAIR · author engineering checks; proposed geometry unreviewed

**33 tests passed**, with lint/format and distribution-build checks. Scenario tests show that moving the start from 03:00 to 22:00 shifts future clocks across midnight while preserving the exact fixed-seed elapsed requests and population. Explicit density/passenger/household/rate overrides recalculate totals; inconsistent request allocations, unknown fields, approval metadata and output overwrites are rejected. The accepted benchmark bytes and original generated demand are preserved.

GIS tests check metre buffering and CRS requirements, segment clipping with reentry, weak/strong directed components, source identity and coverage, context consistency, partial-response rejection, and an offline synthetic OSM conversion with preserved one-way direction. This fixture does not validate OSM completeness or legal driving rules.

## Actual OSM acquisition and conversion

A roads/restrictions-only Overpass request acquired 7,637,247 bytes for a small rectangle surrounding the named Coronado area. Snapshot base time: 2026-11-18T06:40:59Z. The source has 43,359 nodes, 10,593 highway ways and 136 relations; all referenced way nodes are present. An earlier general map API request was rejected by its 50,000-node query limit; no partial response was used. Acquisition requested way bodies, not contributor user metadata. Attribution: © OpenStreetMap contributors; ODbL-1.0.

The proposed AOI envelope derives from OSM intersections of 7th/16th Streets and McDowell/Thomas Roads. Its projected rectangular context expands each side by 1,000 m, with a further 100 m download margin. The named-road boundary and this approximation have not been scientifically reviewed or adopted as the accepted polygon.

The SUMO 1.28.0 conversion/audit reports:

| Diagnostic | Result |
|---|---:|
| External passenger lane-km within proposed AOI | 75.6200 |
| External passenger lane-km within proposed context | 382.1094 |
| External passenger lane-km in full retained network | 454.4030 |
| Conditional initial vehicle count at 2 vehicles/lane-km | 764 |
| Passenger external lanes / regular edges | 13,951 / 9,764 |
| Weak lane-connection / edge-union components | 24 / 16 |
| Largest edge-union component | 9,730 edges |
| OSM highway ways without explicit lanes / maxspeed tags | 8,832 / 9,569 |
| OSM highway ways without oneway tag | 8,306 |
| Native generated signal programs | 345 |

The initial count is a conditional accounting result, not realized vehicle placement. Network tails/padding explain the distinction between retained-network and context length. Missing tags can lead to typemap inference; absent oneway tags do not independently prove bidirectional legality. Native signal count reflects conversion, not audited operational intersections/timing. Converter warnings and separate components remain visible, with no automatic repair or largest-component pruning.

## Retained evidence and reproducibility

[Evidence identities](gis-verification/verification.json), [source metadata](gis-verification/source.json), [compact audit](gis-verification/audit-summary.json), [scope geometry](gis-verification/scope.geojson), [build command](gis-verification/build.json), [converter warnings](gis-verification/netconvert.stderr), [test log](gis-verification/tests.log) and [file digests](gis-verification/files-manifest.json) are tracked. Raw OSM, the full SUMO network and full audit are retained locally under ignored `runs/coronado-gis/` and identified by hashes. Exact reuse needs these bytes; a fresh online query is a new snapshot.

The base Git commit is 161868c6f688ceef5f9b5c05610bea673198e921; this extension was uncommitted during verification. Its package source fingerprint is recorded separately. No traffic simulation, empirical calibration, policy/fault experiment, worker-image rebuild or OSPool execution occurred for this GIS preparation slice. Existing headless fixture tests still pass, but historical container results apply to their own source fingerprint.

Next: review boundary and inferred/legal/control attributes, resolve the disconnected inventory, then define access endpoints, gateways, routes and physical occupancy/history. No observed 03:00 rates or new scientific traffic defaults are claimed.
