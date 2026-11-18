# First scenario proposal: Coronado

Version: 0.2 | Date: 2026-11-17 | Authority: OMFA | Status: accepted hypothetical benchmark, not execution-ready

## Accepted benchmark

Use Coronado as the first Phoenix reporting AOI, with a hypothetical 1,000-household population and an initial vehicle-network accounting benchmark. Start quiescent at 03:00 and preserve the accepted three occupancy layers and checkpoint design. The user accepted these experimental choices on 2026-11-17; they remain hypothetical, not estimates of real residents, demand, or AV behavior. The active recipe is implementation/scenarios/coronado-benchmark.json. implementation/proposals/coronado-hypothetical-v1.json preserves the original proposal and is not the active recipe.

## Geographic candidate

Phoenix's published district list defines Coronado from 7th Street to 16th Street and McDowell Road to Thomas Road. These named boundaries give a concrete candidate without inventing exact coordinates or a routable graph. Include a proposed 1,000 m simulation context; test 500 m and 2,000 m alternatives. The City also publishes a study of reversible lanes along 7th Street/7th Avenue. Check actual time-dependent access and turn restrictions for any included 7th Street segments rather than importing a static grid assumption. No current lane schedule or network extract has been obtained.

Coronado is proposed for a bounded first network, with candidate surrounding connections to inspect. Its actual usable alternate routes, junction controls, lanes, speed limits, crossings, land uses, and boundary gateways still require extraction and audit. A larger alternative, for stronger diversion tests at greater cost, is a wider central-Phoenix extract. Neither geographic choice is claimed representative of the city.

Sources inspected: [Phoenix special planning districts](https://web-prod.phoenix.gov/content/dam/phoenix/pddsite/documents/planning-zoning-pz/pdd_pz_pdf_00428.pdf), [7's Reverse Lane Study](https://www.phoenix.gov/content/dam/phoenix/streetssite/documents/reverse_lane_study_december_2021.pdf). The latter is historical evidence of a modeling issue to check, not verification of current operational rules.

## Proposed household and demand realization

Use 250 one-person, 400 two-person, 200 three-person, 100 four-person, and 50 five-person synthetic households: 1,000 households and 2,300 residents. No demographics are inferred. Household positions would be assigned to eligible access locations only after network/land-use inspection; uniformly distributed households would be an additional explicit abstraction requiring review.

All residents begin at home in this first proposal. Select 380 distinct households to supply one departure party each: 320 single-person parties, 50 pairs, and 10 four-person parties. This moves 460 residents in 380 vehicle requests, leaving 1,840 residents without a scheduled departure. Select larger parties first from households large enough to supply them, then select unused households for pairs and singles. No person is duplicated. These choices deliberately omit repeat trips/returns within the window; they are not a household activity model.

Proposed vehicle-request counts are 19 from 03:00–06:00, 76 from 06:00–07:00, 152 from 07:00–08:00, 95 from 08:00–09:00, and 38 from 09:00–10:00. Draw times uniformly within each half-open interval and preserve the sampled realization across policies. Allocate 228 requests to reachable internal destinations and 152 to explicitly modeled outbound gateways. The gateways are scoped trip endpoints, not claims about actual ultimate destinations. Destination opportunity weights and mode choice are not calibrated.

Preposition one autonomous service vehicle per resident party at its household origin, with four seats. These 380 parked service vehicles are supply, not initial on-road occupancy. A party departure has no separate pickup leg in this proposal. This is an important simplification to review against a future shared-fleet model with repositioning and vehicle reuse. Do not silently turn residents into available vehicles.

## Proposed initial and external road traffic

Propose 2 vehicles per eligible directional lane-kilometer at 03:00. Compute the initial on-road count only after the extract defines eligible lane length; no vehicle count is invented before that. Use external through travelers for this initial road population, separate from the 2,300 resident people. Proposed external vehicle occupancy is 5% empty, 80% carrying one person, and 15% carrying two, with two-seat external service vehicles. Allocate integer counts using largest remainder and report realized fractions. Geometry, physical speeds/headways, routes and prior trip histories remain unresolved.

Add 90 external vehicle requests over 03:00–06:00, 360 over 06:00–09:00, and 60 over 09:00–10:00: 510 external requests, plus the 380 resident requests. These fixed counts with uniformly sampled times are not Poisson arrivals and are not measured external demand. Initial on-road vehicles are additional to these 890 future requests and must have distinct trip IDs. All external traffic has explicit boundary accounting. Count discarded/unroutable or unrealized requests instead of silently losing them.

## Alternatives, uncertainty and claim limits

Smaller/larger household totals, initial density and boundary demand can change whether congestion occurs; no loading regime is asserted before a pilot. Proposed sensitivity brackets are half and twice the household count, initial density and external arrivals, keeping the change in experimental meaning explicit. Households/party counts must be rebuilt consistently at each size; do not retain fixed occupancy totals under population changes.

This initial benchmark tests vehicle/person/population accounting, buildup, queues, and state handling. Pedestrian/transit demand, realistic pickup/curb effects, freight and mode choice have not been supplied. Their absence prevents multimodal welfare, real-world safety, or Coronado-policy claims. Preserve relevant infrastructure in the network and add scientifically justified demand before broader policy comparisons. No baseline traffic controller, lane program, dynamics, or source data has been calibrated.

## Readiness

Arithmetic and household-party feasibility were checked. No network, individual road trajectories, congestion results, or engine checkpoint test exists. The user accepted the candidate assumptions as this accounting benchmark; this does not establish empirical validity or resolve missing network/control/physical inputs. The initial SUMO feasibility probe and materialized unrouted demand are documented in implementation/feasibility-report.md. No Phoenix simulation has run.
