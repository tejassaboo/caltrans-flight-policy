# Caltrans Commercial Air Travel Flight Policy

**No affiliation with the California Department of Transportation.** The handbook is Caltrans' public
*Accounting Manual, Chapter 15 - Transportation* (accessible version dated 05/14/24), bundled verbatim for research.
It is a published state government manual, but treat it like the other original handbooks: do not publish this
plugin before the course staff confirm that a verbatim handbook may be redistributed (MASTER_PLAN section 4).

A `nanoagent.plugin/v0001` plugin. An agent handles one Caltrans employee's flight request under the chapter's
commercial air travel rules: it reads the trip record, searches a simulated flight world and submits **BOOK**,
**REFUSE** or **FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and section. A deterministic Python
verifier, with no LLM, rebuilds the offers and the chapter's answer itself and checks every field. Built from the
original-handbook template (`handbook_plugins/_template`); `tests/build_scenarios.py` writes the scenario files
(the JSON files are the truth). Build notes, the blind read and the check outputs are in `tests/BUILD_NOTES.md`.

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 10,950 words, 1,336 lines, sha256 `bad50764...ade17ef`, equal to
`pilot_work/originals/caltrans-ch15/frozen/SHA256SUMS`) is never
paraphrased, and the task text restates no rule. Under stock NanoAgent the agent does not see it: the plugin then
runs as the `off` baseline. The `harness.policy` switch of the NanoAgent fork (github.com/tejassaboo/nanoagent,
branch `policy-switch`) adds it to the system prompt: `harness.policy: full` adds all of it, and the selection
methods add parts of it. These plugins are meant to run with `query: instructions+input`, so a selector sees the
traveller's request.

**What the chapter decides.** It has no cabin-class rule and no flight-length threshold. Its flight rules are about
the fare: the lowest cost airfare (lines 136-137); a non-refundable fare only when it is less than the DGS contracted
refundable rate (167-168; out of state, 186-187); in-state non-refundable Southwest fares (183-185); the
capacity-controlled contract fare before the YCAL fare (203-207); reason code justifications for a non-contracted
carrier, a refundable fare, a domestic flight booked less than 7 days ahead and an international flight booked less
than 30 days ahead (213-221, with Example 1 at 231-234); no personal travel through the system or at contract rates
(141-142, 211-212); no residence-headquarters flights on telework (154-159, 61-65); two supervisor-approved
reservations for an extra seat (246-247); and an out-of-state approval process (248-252). The cases vary the
contract and non-contract airline, refundable and non-refundable fares, and the days booked ahead.

**Contract fares.** The shared offer schema has no contract-fare flag, so each trip record lists its city pair's
contracted fares (`contract_fares`: carrier, `CAPACITY_CONTROLLED` or `YCAL`, one-way fare). A refundable offer of
that carrier at that fare is the contract fare. (A template change request for an offer-level flag is in
`tests/BUILD_NOTES.md`.)

**Size.** The handbook is about 14,600 tokens at 1.33 tokens a word, about 16,100 on the Thornton/NJC calibration
(0.2 a character plus 1,800); its mileage tables come out one cell per line. Under `full` a run makes 3 calls
(`get_trip`, `search_flights`, `submit`), about 50,000 to 53,000 input tokens: under the hosted cap of 65,536.

## Task

- **Input:** `TaskInput`: `scenario` (one of 32 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the trip's route and date, then `submit` (3 of the 6 hosted steps).
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing),
  `reason_code`, `approver` and `clause`, each from a closed list. The reason list is shared by every handbook
  plugin, plus this chapter's codes and decoy codes from other handbooks' rules. Approvers follow the template's
  SYNC_NOTES 4': a BOOK or REFUSE with a sign-off on file accepts that role and `NONE` (the supervisor is the
  appointing authority, lines 55-58, so both names are accepted); a hold accepts only the awaited roles.
- **Success:** every field is one the answer key accepts. Score = fields right / 6.

| Scenario | Category | Expected decision (offer slots) | Accepted reasons | Accepted approvers | Accepted clauses | must_keep lines |
|---|---|---|---|---|---|---|
| `agate-cove` | easy | BOOK (wn-saver) | LOWEST_FARE, NON_CONTRACT_CARRIER_JUSTIFIED, NON_REFUNDABLE_BELOW_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 136-137, 186-187, 167-168, 249-252 |
| `bodega-fern` | easy | BOOK (as-controlled) | CAPACITY_CONTROLLED_FARE_AVAILABLE, LOWEST_FARE, NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE, REFUNDABLE_FARE_JUSTIFIED, STATE_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 136-137, 194-199, 203-207, 167-168 |
| `cypress-lark` | easy | BOOK (ba-saver) | LOWEST_FARE, UPGRADE_NOT_ELIGIBLE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, INTERNATIONAL_AIRFARE, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 136-137, 167-168, 249-252 |
| `dune-sparrow` | easy | BOOK (as-controlled) | CAPACITY_CONTROLLED_FARE_AVAILABLE, LOWEST_FARE, NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE, REFUNDABLE_FARE_JUSTIFIED, STATE_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 136-137, 194-199, 203-207, 167-168 |
| `elkhorn-reed` | easy | BOOK (wn-saver) | ADVANCE_PURCHASE_TOO_LATE, DOMESTIC_SHORT_NOTICE_JUSTIFIED, LOWEST_FARE, NON_CONTRACT_CARRIER_JUSTIFIED | APPOINTING_AUTHORITY, NONE, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 136-137, 183-185, 167-168, 174-175, 214-221 |
| `sage-inlet` | easy | BOOK (wn-saver) | REFUNDABLE_FARE_NOT_ALLOWED | APPOINTING_AUTHORITY, NONE, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 136-137, 161-162, 183-185, 214-221 |
| `garnet-slough` | boundary_twin | BOOK (dl-saver) | LOWEST_FARE, LOYALTY_PROGRAM_PREFERENCE, NON_CONTRACT_CARRIER_JUSTIFIED, NON_REFUNDABLE_BELOW_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 186-187, 167-168, 194-199, 249-252 |
| `heron-quay` | boundary_twin | BOOK (as-controlled) | NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE, PREFERRED_CARRIER_REQUIRED, STATE_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | AIRFARE_REIMBURSEMENT_CLAIMS, COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REFUNDABLE_AIRFARE | 186-187, 167-168, 194-199, 249-252, 283-285 |
| `indigo-mesa` | boundary_twin | BOOK (jl-saver) | LOWEST_FARE, NON_CONTRACT_CARRIER_JUSTIFIED, NON_REFUNDABLE_BELOW_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, INTERNATIONAL_AIRFARE, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 167-168, 136-137, 194-199, 249-252 |
| `juniper-tide` | boundary_twin | BOOK (ua-controlled) | CAPACITY_CONTROLLED_FARE_AVAILABLE, LOWEST_FARE, NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE, REFUNDABLE_FARE_JUSTIFIED, STATE_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, INTERNATIONAL_AIRFARE, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 167-168, 136-137, 194-199, 249-252 |
| `kelp-ridge` | boundary_twin | BOOK (aa-saver) | ADVANCE_PURCHASE_TOO_LATE, DOMESTIC_SHORT_NOTICE_JUSTIFIED, LOWEST_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 136-137, 186-187, 249-252, 214-221 |
| `laurel-wash` | boundary_twin | BOOK (aa-saver) | LOWEST_FARE, NON_REFUNDABLE_BELOW_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REFUNDABLE_AIRFARE | 136-137, 186-187, 249-252 |
| `manzanita-pool` | boundary_twin | BOOK (ua-saver) | ADVANCE_PURCHASE_TOO_LATE, INTERNATIONAL_SHORT_NOTICE_JUSTIFIED, LOWEST_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, INTERNATIONAL_AIRFARE, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 136-137, 167-168, 249-252, 214-221 |
| `nopal-crest` | boundary_twin | BOOK (ua-saver) | LOWEST_FARE, NON_REFUNDABLE_BELOW_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, INTERNATIONAL_AIRFARE, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REFUNDABLE_AIRFARE | 136-137, 167-168, 249-252 |
| `fennel-bluff` | multi_rule | BOOK (as-ycal) | CAPACITY_CONTROLLED_SOLD_OUT, LOWEST_FARE, NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE, REFUNDABLE_FARE_JUSTIFIED, STATE_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 203-207, 194-199, 186-187, 249-252 |
| `poppy-ledge` | multi_rule | BOOK (as-controlled) | CAPACITY_CONTROLLED_FARE_AVAILABLE, UPGRADE_NOT_ELIGIBLE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, REFUNDABLE_AIRFARE | 203-207, 194-199, 186-187, 249-252 |
| `oriole-bend` | multi_rule | BOOK (ua-controlled) | CAPACITY_CONTROLLED_FARE_AVAILABLE, LOWEST_FARE, NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE, REFUNDABLE_FARE_JUSTIFIED, STATE_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 136-137, 186-187, 194-199, 203-207, 249-252 |
| `quail-hollow` | multi_rule | BOOK (as-connect) | ALTERNATE_ROUTE_WITHIN_MARGIN, COST_SAVINGS, LOWEST_FARE, NON_REFUNDABLE_BELOW_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REFUNDABLE_AIRFARE | 136-137, 174-175, 186-187, 249-252 |
| `redwood-spur` | multi_rule | BOOK (as-controlled) | CAPACITY_CONTROLLED_FARE_AVAILABLE, LOWEST_FARE, REFUNDABLE_FARE_JUSTIFIED, STATE_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 136-137, 174-175, 194-199, 249-252 |
| `tule-marsh` | hidden_clause | BOOK (as-controlled, wn-saver) | ADVANCE_PURCHASE_TOO_LATE, DOMESTIC_SHORT_NOTICE_JUSTIFIED, LOWEST_FARE, REFUNDABLE_FARE_JUSTIFIED, SOUTHWEST_IN_STATE_FARE, STATE_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 231-234, 214-221, 161-162, 194-199, 136-137, 183-185 |
| `umber-canyon` | hidden_clause | BOOK (wn-saver) | LOWEST_FARE, NON_CONTRACT_CARRIER_JUSTIFIED, NON_REFUNDABLE_BELOW_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 61-65, 154-159, 136-137, 186-187, 249-252 |
| `vireo-point` | hidden_clause | BOOK (as-controlled) | CAPACITY_CONTROLLED_FARE_AVAILABLE, EXTRA_SEAT_APPROVED, LOWEST_FARE, NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE, REFUNDABLE_FARE_JUSTIFIED, STATE_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, PASSENGERS_OF_SIZE, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 241-245, 246-247, 136-137, 194-199 |
| `willow-flat` | distractor | BOOK (ua-saver) | LOWEST_FARE, NON_REFUNDABLE_BELOW_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REFUNDABLE_AIRFARE | 136-137, 186-187, 249-252 |
| `yucca-strand` | distractor | BOOK (wn-saver) | LOWEST_FARE, NON_CONTRACT_CARRIER_JUSTIFIED, NON_REFUNDABLE_BELOW_CONTRACT_FARE, UNUSED_TICKET_CREDIT_APPLIED | APPOINTING_AUTHORITY, NONE, RESOURCE_AND_INNOVATION_DIVISION, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, OUT_OF_STATE_APPROVAL, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 136-137, 186-187, 144-148, 249-252 |
| `alder-rook` | distractor | BOOK (as-controlled) | CAPACITY_CONTROLLED_FARE_AVAILABLE, LOWEST_FARE, NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE, REFUNDABLE_FARE_JUSTIFIED, STATE_CONTRACT_FARE | APPOINTING_AUTHORITY, NONE, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE, REASON_CODE_JUSTIFICATIONS, REFUNDABLE_AIRFARE | 138-140, 136-137, 194-199, 203-207 |
| `basalt-cliff` | refusal | REFUSE (none) | CONTRACT_FARE_NOT_FOR_PERSONAL_TRAVEL, PERSONAL_TRAVEL_NOT_COVERED | NONE | COMMERCIAL_AIR_TRAVEL, REFUNDABLE_AIRFARE | 141-142, 211-212 |
| `coyote-dell` | refusal | REFUSE (none) | COMMUTING_NOT_REIMBURSABLE, PERSONAL_TRAVEL_NOT_COVERED | APPOINTING_AUTHORITY, NONE, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, TRANSPORTATION_GENERAL | 154-159, 61-65, 48-49 |
| `dove-terrace` | refusal | REFUSE (none) | COMPANION_NOT_COVERED, CONTRACT_FARE_NOT_FOR_PERSONAL_TRAVEL, PERSONAL_TRAVEL_NOT_COVERED | NONE | COMMERCIAL_AIR_TRAVEL, REFUNDABLE_AIRFARE | 141-142, 211-212 |
| `egret-shoal` | flag | FLAG_FOR_APPROVAL (as-controlled, ua-saver) | APPROVAL_REQUIRED, UNCLEAR_POLICY_TEXT | APPOINTING_AUTHORITY, NOT_NAMED, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE | 183-185, 186-187, 167-168, 136-137 |
| `finch-arroyo` | flag | FLAG_FOR_APPROVAL (wn-saver) | APPROVAL_REQUIRED | NOT_NAMED, PROGRAM_TRAVEL_COORDINATOR, RESOURCE_AND_INNOVATION_DIVISION | OUT_OF_STATE_APPROVAL | 249-252, 136-137, 186-187 |
| `granite-wren` | flag | FLAG_FOR_APPROVAL (as-controlled) | APPROVAL_REQUIRED | APPOINTING_AUTHORITY, SUPERVISOR | PASSENGERS_OF_SIZE | 246-247, 241-245, 136-137 |
| `hazel-kiln` | flag | FLAG_FOR_APPROVAL (as-connect, as-controlled) | APPROVAL_REQUIRED, UNCLEAR_POLICY_TEXT | APPOINTING_AUTHORITY, NOT_NAMED, SUPERVISOR | COMMERCIAL_AIR_TRAVEL, NON_REFUNDABLE_AIRFARE | 174-175, 136-137, 186-187, 249-252 |

Mix (EDGE_CASES.md 5.2): 6 easy, 8 boundary twins, 5 multi-rule, 3 hidden clause, 3 distractor, 3 refusal,
4 flags (12.5%). Decisions: 25 BOOK, 3 REFUSE, 4 FLAG_FOR_APPROVAL. Unclear words are each one flag with clear twins
on both sides: "Travelers may purchase non-refundable airfare for Southwest Airlines" (`egret-shoal`, twins
`bodega-fern` and `garnet-slough`) and "as long as the layovers do not significantly impact business or delay travel
times" (`hazel-kiln`, twins `quail-hollow` and `redwood-spur`). `finch-arroyo` (out-of-state approval pending) and
`granite-wren` (second seat not yet approved) are approval holds, never "no compliant offer".

Degenerate agents (`tests/test_verifier.py`): always-flag passes 2 (`egret-shoal`, `hazel-kiln`); always-cheapest
(cheapest seat, `LOWEST_FARE`, `NONE`, the right clause) passes 13 of 32 (40.6%).

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller, office, route, dates, purpose, what they ask for, contract fares, credits, sign-offs, notes | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date: the pinned scenario offers (no background offers in this plugin); a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-caltrans-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this chapter's scenario ids, approvers, sections and trip record.
- `src/plugin/`: `world.py` (the simulated world: real airports and airline hubs, distance-based times
  and fares, opaque offer ids), `scenarios.py`, `guide.py`, `answer.py`, `tools.py`, `rules.py` (this chapter's
  rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of `world.py`, `scenarios.py`, `guide.py`, `answer.py` and
  `rules.py`, plus `booking.py` (`verify_task`) and `tools.py` (`verify_input`, `verify_output`).
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this chapter's settings;
  `tests/build_scenarios.py` writes the scenarios; `tests/BUILD_NOTES.md` records the build.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 tests/build_scenarios.py   # rewrites src/plugin/data/scenarios/*.json
# from a NanoAgent checkout (stock NanoAgent runs this plugin as the `off` baseline;
# the fork's `harness.policy: full` flag adds the handbook):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/caltrans-flight-policy.tar.gz
<nanoagent>/.venv/bin/python ../_template/tools/stock_verify.py .
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
