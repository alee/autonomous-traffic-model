# Phoenix data and evidence assessment
Version: 0.2 | Date: 2026-11-17 | Status: draft, unreviewed | Authority: OMFA | Author: Codex with user-supplied intent

Inspected 2026-11-17 local date. This is a scientific evidence inventory, not a declaration of data quality or reuse permission. No feature rows, GTFS archives, or origin-destination matrices were downloaded. Metadata are observations about available descriptions, not inspected transport measurements.

| ID / component | Inspected evidence | Supported use | Unresolved limitation / next evidence needed |
|---|---|---|---|
| P1 / traffic volumes | Phoenix layer metadata expose count date, volume, direction, count type, and speed fields | Candidate count constraints for baseline demand | Count-only and five-row queries were inaccessible via web tool; shell DNS failed. Row count, date distribution, missingness, units, spatial coverage, and speed completeness unassessed. ADT cannot supply hourly OD. |
| P2 / road network | MAG T2026_Network metadata identify polylines and ID, direction, length, facility type, street, lane fields | Candidate regional network context and comparison | Planning/conformity purpose; scenario year is not proof of as-built status. No feature or connectivity audit, code dictionary, units confirmation, complete local streets, turn restrictions, speeds, or signal timing established. |
| P3 / disruption context | Phoenix traffic-restriction service describes intersection and street restrictions updated hourly | Candidate locations/types for plausible disruption scenarios | No rows, historical archive, reliability, or capacity effects inspected; do not reconstruct a historical event from current metadata. |
| P4 / temporal traffic patterns | MAG System Analysis and Forecasting links public volume/speed tools | Candidate temporal calibration and independent evaluation sources | Portal and descriptions inspected only; raw temporal coverage, access, reuse terms, and calibration/holdout split unassessed. |
| P5 / crossing demand | MAG Active Transportation describes spring 2022 bicycle/pedestrian counts at over 500 regional locations | Candidate crossing-demand evidence | Older regional survey; no Phoenix-specific coverage or time profile audited. Not current demand by default. |
| P6 / transit | Valley Metro developer page points to static and realtime bus/light-rail GTFS | Candidate routes, schedules, and stops | Feed files and terms for the specific distribution not evaluated. Scheduled service does not identify ridership, dwell distributions, or observed reliability. |
| P7 / actual controls and OD | No usable signal timing or trip table acquired | None yet | Use declared hypothetical ensembles for exploratory runs. Do not imply replication of Phoenix's operational signals or actual trips. |

## Source links
P1: https://maps.phoenix.gov/pub/rest/services/Public/STR_TrafVol/MapServer/0?f=pjson

P2: https://geo.azmag.gov/arcgis/rest/services/Transportation/conformity_network_2026/MapServer/1 ; service purpose: https://geo.azmag.gov/arcgis/rest/services/Transportation/conformity_network_2026/MapServer

P3: https://maps.phoenix.gov/pub/rest/services/Public/TrafficRestrictions/MapServer?f=pjson

P4: https://azmag.gov/Programs/Transportation/System-Analysis-and-Forecasting

P5: https://azmag.gov/Programs/Transportation/Active-Transportation

P6: https://www.valleymetro.org/contact/developers-resources

## Evidence classes and consequences
Empirical inspected evidence: source metadata and program descriptions only. Inferred uses: each dataset's possible modeling role. Hypothetical assumptions: every current numerical experiment setting, agent rule, and scenario rate. No expert elicitation or calibrated transport parameters exist.

No preprocessing has occurred. Prospective joins need coordinate/unit reconciliation, date alignment, topology checking, code definitions, duplicates/missingness review, and coverage mapping. Do not project a planning-network line into a turn-level road without evidence. Reuse/access permissions remain to be checked on the actual downloaded products; no contact with an agency or data request has been sent. FAIR owns detailed acquisition provenance, stewardship, and licensing review when acquisition proceeds.

Missing controls or OD permit exploratory policy comparison under stated assumptions, but can reverse rankings. Missing topology prevents even that comparison from being city-grounded. Missing trajectories prevents safety evaluation. Conflicts among counts, travel times, and reconstructed demand require retained alternatives, not hidden parameter tuning.
