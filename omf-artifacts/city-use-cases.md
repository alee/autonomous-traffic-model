# Candidate city use cases
Version: 0.2 | Date: 2026-11-17 | Status: draft, unreviewed | Authority: OMFA | Author: Codex with user-supplied intent

Recommendation is a methodological judgment, not a measured ranking of data completeness or modeling effort. Phoenix is now the first case under the user’s instruction to proceed with the recommended sequence; city details remain modeler defaults.

| Candidate | Proposed scientific role | Particularly useful tests | Evidence and limits |
|---|---|---|---|
| Phoenix | First case | Arterial coordination, route diversion, freeway/surface interaction, correlated fleet faults | Official queryable traffic-count layer includes dates, direction, ADT, and speed fields [S1]. Availability of a field does not establish completeness. City versus metro boundary must be explicit. |
| Chicago | Contrasting second case | Alternative route coordination, neighborhood diversion, transit interaction, regional disruption | Official arterial congestion estimates use CTA bus GPS [S2]. Bus-derived speeds are not complete vehicle trajectories; legacy feed is deprecated, so inspect successor historical coverage. |
| New York City | Multimodal and constrained-access stress case | Crossing access, transit/person throughput, bottleneck disruption and spillback | DOT publishes vehicle/pedestrian counts and bridge/crossing volume resources [S3]. A Manhattan-only case cannot be labeled NYC-wide. Mode and geographic coverage need review. |
| Los Angeles | Freeway/arterial and institutional coordination case | Competing routing operators, ramp diversion, control/information failures | ATSAC adjusts signal timing from detectors and supports transit [S4]. Description of operational infrastructure does not imply public access to signal plans or detector logs. Distinguish City of LA from the county/metro. |

Proceed with Phoenix as the anchor; choose Chicago for a second network comparison or NYC for a stronger multimodal contrast. Elevate LA if freeway/arterial coordination becomes the primary question. Before committing, inspect network, demand, turning, control, occupancy, transit/crossing, and independent evaluation data. Public traffic counts alone do not constitute a runnable calibrated city model. Use toy network checks later for verification while retaining citywide scientific scope.

## Inspected primary sources (2026-11-17 local date)
- S1: [Phoenix Traffic Volumes layer](https://maps.phoenix.gov/pub/rest/services/Public/STR_TrafVol/MapServer/0).
- S2: [Chicago Traffic Tracker regional estimates, deprecated](https://data.cityofchicago.org/Transportation/Chicago-Traffic-Tracker-Congestion-Estimates-by-Re/t2qc-9pjd). Its description points to 2018–2026 historical data; successor data not yet inspected.
- S3: [NYC DOT data feeds and open data](https://www.nyc.gov/html/dot/html/about/datafeeds.shtml).
- S4: [LADOT ATSAC](https://ladot.lacity.gov/projects/transportation-technology/atsac).

## Conceptual literature, not city validation
- [Dresner and Stone (2008), A Multiagent Approach to Autonomous Intersection Management](https://www.cs.utexas.edu/~pstone/Papers/bib2html/b2hd-JAIR08-dresner.html): inspected abstract describes reservation-based intersection coordination; motivates a candidate, not a guarantee under the proposed threat model.
- [Shalev-Shwartz et al., On a Formal Model of Safe and Scalable Self-driving Cars](https://arxiv.org/abs/1708.06374): inspected abstract describes RSS safety assurance; a candidate source for later safety assumptions, not a safety proof for this model. Full mathematical treatment not reviewed here.

## Phoenix refinement
See phoenix-case-study.md for municipal outcomes with regional context, and data-evidence-assessment.md for the inspected metadata and outstanding acquisition/quality gaps.
