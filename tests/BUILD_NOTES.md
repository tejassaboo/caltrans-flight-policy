# Build notes: caltrans-flight-policy

Wave 3 build of 2026-11-24 (overnight), following `pilot_work/tier_plan/build/WAVE3_BUILD_BRIEF.md`. No paid
calls, no network, no pushes. Decisions were taken without asking, as the brief says; each is recorded here.

## Handbook

- Frozen text: `pilot_work/originals/caltrans-ch15/frozen/caltrans-ch15_policy.txt`, 10,950 words, 1,336 lines,
  sha256 `bad50764...ade17ef` (raw PDF `03bce487...678f25`). Over 10,000 words, so 32 scenarios (EDGE_CASES 5.1).
- Task id `book-caltrans-flight` (`--task-id`: the slug's digits "15" occur in the text). Plugin id
  `caltrans-flight-policy`. Background offers are off (`background_offers: 0`, and every pinned search has
  `"background": 0`).
- Instantiated with `_template/instantiate.py`; shared files untouched (`check_shared.py`: ok).

## What the chapter decides, and what it lacks

Mandatory flight clauses and their operators:

| Clause | Lines | Operator / force | Coded as |
|---|---|---|---|
| Lowest cost airfare | 136-137 | "must ... whenever possible" | default choice among allowed fares |
| Concur or CI Azumano only | 138-140 | must | the agent books from the search, never an outside fare (alder-rook) |
| No personal travel in the system | 141-142 | prohibited | REFUSE |
| Telework: no residence-headquarters flights | 154-159 (and 48-49, 61-65) | not reimbursable | REFUSE |
| Non-refundable only below the contract rate | 167-168 | "less than" (strict) | non-refundable fare allowed iff fare < rate |
| In-state: Southwest non-refundable | 183-185 | "may" | Southwest allowed in-state; other airlines' in-state non-refundable fares below the rate are the unclear phrase |
| Out-of-state: any carrier, if less costly | 186-187 | "less costly than" (strict) | same strict test |
| Capacity-controlled before YCAL | 203-207 | "should be used when seats are available" | YCAL only when the controlled seats are sold out |
| Contract rates only for state business | 211-212 | "may only be used" | REFUSE (personal, spouse) |
| Reason code justifications | 214-221 | required code, not a bar | accepted reason codes on the BOOK: non-contracted carrier, refundable fare, domestic < 7 days, international < 30 days (strict "less than") |
| Example 1: refundable for a short-notice assignment | 231-234 | example of a justification | a refundable request with the assignment email on file and plans open books the contract fare |
| Extra seat: two reservations, supervisor approves both | 246-247 | "will need to approve both" | hold until both approved |
| Out-of-state approval process | 248-252 | an approval process | hold while the request is pending |

Soft clauses and tips: 161-162 (consider non-refundable first when the dates are fixed), 170-177 (cost-saving
factors: 14 days ahead, flexible window, routing, alternate airports), 144-148 (Southwest unused ticket credits
"encouraged" first), 254-257 (international bookings by phone "encouraged"), 262-271 (one bag).

What it lacks, so not invented: **no cabin-class rule at all** (no business, premium or first permission; a business
request is declined on the lowest-fare rule, `cypress-lark`), **no flight-length threshold**
(`DURATION_RULES = ()`, `DURATION_CASES = []`, `rules.over` raises; the 3 skipped tests are the empty duration
parametrizations), no overnight-stop rule (the multi-leg overlay has no overnight case), no multi-traveller rule
beyond "Number of employees traveling to the same place" as a mode factor (line 88) (the spouse refusal and the
extra seat carry the overlay), and no advance-purchase bar (7/30 days only call for a reason code).

## Decisions taken without asking

1. **Contract fares in the trip record.** The shared offer schema has no contract-fare flag. Each trip record lists
   its city pair's DGS fares (`contract_fares`: carrier, `CAPACITY_CONTROLLED` or `YCAL`, one-way fare, the same
   fares for a city pair in every case, either direction). A refundable offer of that carrier at that fare is the
   contract fare; no other refundable fare appears in any case. Template change request 1.
2. **Which contract rate.** "The DGS contracted refundable rate" is the cheapest contract fare with seats. No case
   puts a non-refundable fare between a sold-out capacity-controlled fare and the open YCAL fare (the rate there is
   unclear); `rules.sort_fares` raises if one does.
3. **In-state non-refundable fares of other airlines** below the contract rate are the unclear phrase (one flag,
   `egret-shoal`). Every other in-state case keeps such fares at or above the contract rate, where both readings
   exclude them.
4. **Reason codes.** A BOOK accepts `LOWEST_FARE` when the booked fare is the lowest allowed and nothing is
   declined, plus the codes that describe the fare (contract or non-refundable below the contract) and each
   justification lines 214-221 call for. A BOOK that declines the request accepts only the ground for declining:
   Delta at the contract fare (`heron-quay`) gives NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE / STATE_CONTRACT_FARE /
   PREFERRED_CARRIER_REQUIRED, YCAL with controlled seats open (`poppy-ledge`) gives
   CAPACITY_CONTROLLED_FARE_AVAILABLE / UPGRADE_NOT_ELIGIBLE (no LOWEST_FARE, brief lesson 12). Declines on the
   lowest-fare rule itself keep LOWEST_FARE (`cypress-lark` business, `sage-inlet` refundable with fixed dates).
5. **Refundable requests.** Granted (`tule-marsh`) only with Example 1's facts: a short-notice assignment email on
   file and plans that may move. Declined (`sage-inlet`) when the dates are fixed and nothing justifies it. Other
   mixes raise.
6. **Layovers (lines 174-175).** A cheaper connection that lands in time and adds at most 60 minutes of elapsed time
   over the nonstop (or that the traveller accepts in words) is clearly fine (`quail-hollow`: 45 minutes, and it
   lands earlier); one that lands after the business starts impacts it (`redwood-spur`); 160 added minutes before a
   next-morning workshop is the unclear phrase (`hazel-kiln`). The 60 minutes is a design zone, not a handbook
   number: no case lies between 61 and 159 minutes.
7. **Arrival limits.** Cases where a cheaper flight lands too late give `Trip.must_arrive_by` (Georgia's field) and
   say the start time in the request (lesson 4); the others say the business is the next morning or later.
8. **Approvers (SYNC_NOTES 4').** Every business trip has the supervisor's trip approval on file; out-of-state and
   international trips also have the out-of-state approval (Division of Resource and Innovation). BOOKs accept
   NONE, SUPERVISOR, APPOINTING_AUTHORITY (lines 55-58: the appointing authority is a supervisor) and, out of
   state, RESOURCE_AND_INNOVATION_DIVISION. The teleworker refusal accepts the unused supervisor approval beside
   NONE (4(b)). Unclear holds accept NOT_NAMED, SUPERVISOR, APPOINTING_AUTHORITY (lines 112-117: the supervisor
   weighs time against cost) and APPROVAL_REQUIRED beside UNCLEAR_POLICY_TEXT (lesson 2). The out-of-state hold
   accepts the Division, the program's travel coordinator and NOT_NAMED (lines 248-252 name who administers the
   process, not who signs).
9. **International is out of state** for the approval process: every international record carries the
   out-of-state approval, and lines 167-168 decide its non-refundable fares.
10. **Requests** never name a threshold (lesson 6); each declined ask has a fallback ("If Delta isn't allowed, book
    what the policy allows; I have to be at the conference", lesson 3). `willow-flat` says only "later than I'd
    like" for the 14-day tip.
11. **Lint renames.** `OUT_OF_STATE_TRAVEL_COORDINATOR` became `PROGRAM_TRAVEL_COORDINATOR` and the sign-off subject
    `OUT_OF_STATE_TRIP`, since "out of state travel coordinator" is a 4-word phrase of line 252; the out-of-state
    `must_keep` starts at line 249 (after the heading).
12. **Decoy reason codes** (grep found none of their subjects in the chapter): WEEKEND_TRAVEL_HOME,
    WEEKEND_TRIP_NOT_EARNED, NEXT_OF_KIN_TRAVEL, FLY_AMERICA_US_CARRIER_REQUIRED, OPEN_SKIES_AGREEMENT,
    CREATIVE_TICKETING, CHANCELLOR_WRITTEN_AUTHORIZATION, DOUBLE_BOOKING_PROHIBITED ("double" occurs only for
    mileage), SAME_CLASS_AS_CUSTOMER, CANDIDATE_TRIP_NOT_COVERED, DENIED_BOARDING_NOT_ALLOWED.
    PRIVATE_AIRCRAFT_NOT_APPROVED stays a handbook code (the chapter has a privately-owned aircraft section) with no
    case. Approver decoys: CHIEF_FINANCIAL_OFFICER, VICE_PRESIDENT.
13. **No `rules.py` class.** The answer key uses plain functions and dicts (no `__init__`), since a verifier may not
    use names starting with `_`.

## Scenarios (32)

Mix: 6 easy, 8 boundary twins, 5 multi-rule, 3 hidden clause, 3 distractor, 3 refusal, 4 flags (12.5%).
Decisions: 25 BOOK, 3 REFUSE, 4 FLAG_FOR_APPROVAL.

Twin pairs (one fact each): `garnet-slough`/`heron-quay` (Delta non-refundable 16899 or 16900 against the 16900
contract fare, lines 186-187), `indigo-mesa`/`juniper-tide` (JAL 141999 or 142000 against 142000, lines 167-168),
`kelp-ridge`/`laurel-wash` (booked 6 or 7 days ahead, line 220; crosses November/December),
`manzanita-pool`/`nopal-crest` (29 or 30 days ahead, line 221), `fennel-bluff`/`poppy-ledge` (controlled seats sold
out or open, lines 203-207), `umber-canyon`/`coyote-dell` (a teleworker flies to a conference or to headquarters).

Flags and the clauses they test:
- `egret-shoal` (unclear): "Travelers may purchase non-refundable airfare for Southwest Airlines" (183-185 against
  167-168 and 186-187): United's in-state non-refundable 11900 under Alaska's 13900 contract fare. Holds either.
  Twins `bodega-fern` (in-state, other non-refundable fares above the rate: contract) and `garnet-slough` (out of
  state, another airline below the rate: book it).
- `hazel-kiln` (unclear): "as long as the layovers do not significantly impact business or delay travel times"
  (174-175): a 12900 connection adding 160 minutes before a next-morning workshop, against the 16900 nonstop
  contract fare. Holds either. Twins `quail-hollow` (45 minutes: connection) and `redwood-spur` (lands late:
  nonstop).
- `finch-arroyo` (approval): out-of-state request pending (248-252). Twins `agate-cove` (approved: book) and
  `bodega-fern` (in state: no out-of-state approval).
- `granite-wren` (approval): second seat's reservation not yet approved (246-247). Twins `vireo-point` (both
  approved: book) and `dune-sparrow` (no extra seat).

Overlays: multi_leg 7, date_arithmetic 5, month_end 4, personal_travel 2, multi_traveller 3, dearer_option 11,
upgrade_not_taken 3 (YCAL not taken in `bodega-fern` and `poppy-ledge`; business not taken in `cypress-lark`),
outside_air_section 3 (`umber-canyon`, `coyote-dell`: lines 61-65 in GENERAL POLICY; `alder-rook`: THIRD PARTY
VENDORS, lines 67-72).

Degenerate agents: always-flag passes 2 (`egret-shoal`, `hazel-kiln`); always-cheapest (cheapest seat,
LOWEST_FARE, NONE, the right clause) passes 13 of 32 (40.6%): agate-cove, bodega-fern, cypress-lark, elkhorn-reed,
sage-inlet, garnet-slough, indigo-mesa, fennel-bluff, quail-hollow, umber-canyon, vireo-point, yucca-strand,
alder-rook. In each the chapter's answer is the lowest allowed fare; it fails the other 19 because a cheaper fare
lands too late (8), the request is declined on a contract rule (2), a tie at the contract fare goes to the contract
(1), a refundable fare is justified (1), or it is a refusal or a hold (7).

## Hosted-cap estimate

Handbook 10,950 words, 71,519 bytes: about 14,600 tokens at 1.33 a word, about 16,100 on the Thornton/NJC
calibration (0.2 a character plus 1,800); the mileage tables come out one cell per line, so the real count may be
nearer the higher figure. Full-handbook prompt per call: about 16,000 to 17,500 input tokens (handbook,
instructions about 280, tool and submit schemas about 1,500, the request, then tool results of about 600 to 1,000
each). A run makes 3 calls (`get_trip`, `search_flights`, `submit`): about 50,000 to 53,000 input tokens, under the
hosted 65,536 cap. No case needs a second search.

## Blind read (no agents; re-derived from the handbook text and the tool outputs, not from rules.py)

I printed every scenario's `get_trip` record and `search_flights` output and answered each non-flag case from the
frozen text. This is a self-read by the builder, not an independent auditor's: treat it as a consistency check.

| Scenario | My answer from the text and the offers | Agrees |
|---|---|---|
| agate-cove | Out of state, approved. WN 16400 non-refundable < UA contract 21900 (186-187), lowest (136-137); UA saver 23900 above the rate. Book WN; non-contract carrier code (218) | yes |
| bodega-fern | In state. AS saver 16900 and UA 17900 are above the 15400 contract fare (167-168): book AS controlled 15400 | yes |
| cypress-lark | No cabin rule; lowest cost (136-137): BA economy 84000 (< UA 118000 contract, 167-168). 50 days ahead | yes |
| dune-sparrow | WN via LAS lands 09:05 > 08:45; UA 15900 > 13900 contract; AS controlled lands 07:40: book it | yes |
| elkhorn-reed | WN via LAS 11900, in-state Southwest (183-185), < 15400; connection accepted, training next day: book WN | yes |
| sage-inlet | Dates fixed, "just in case": 161-162 non-refundable first, 136-137 lowest; no justification on file (219, 231-239): WN 11900, refundable declined | yes |
| garnet-slough | DL 16899 < 16900 (186-187): allowed, lowest, and asked for: book DL | yes |
| heron-quay | DL 16900 not less costly than 16900: not allowed; book AS controlled 16900 (not LOWEST_FARE: the ground is 186-187) | yes |
| indigo-mesa | JL 141999 < 142000 (167-168): book JL | yes |
| juniper-tide | JL 142000 not less than 142000: book UA controlled 142000 | yes |
| kelp-ridge | WN lands 13:40 > 12:30; AA saver 15900 < 19800: book it; 6 days ahead < 7 (220): short-notice code too | yes |
| laurel-wash | Same booking; 7 days ahead is not less than 7: no short-notice code | yes |
| manzanita-pool | WS lands 16:00 > 15:30; AC 29900 < UA 38900 (167-168): book AC; 29 days < 30 (221) and non-contract (218) | yes |
| nopal-crest | Same booking; 30 days: no international short-notice code | yes |
| fennel-bluff | Controlled seats sold out; YCAL 33800 asked for and allowed (203-207); DL 36900, AS 35900 above it: book YCAL | yes |
| poppy-ledge | Controlled seats open: use them before YCAL (204-207); book AS controlled 16900, YCAL declined | yes |
| oriole-bend | WN lands 13:50 > 13:30; UA saver 23900 > 22900 contract (186-187): book UA controlled 22900 | yes |
| quail-hollow | AS via SFO 12900 < 16900; 215 against 170 minutes and lands 11:35, before the nonstop: not a significant delay (174-175); book it | yes |
| redwood-spur | Connection lands 12:55 > 12:30 (impacts business, 174-175): AS nonstop controlled 16900 | yes |
| tule-marsh | Short-notice assignment email on file, schedule may move, refundable asked: Example 1 (231-234) justifies it; 161-162 do not apply; AS controlled 15400 with refundable and <7-day codes. WN 11900 declined as asked | yes (see below) |
| umber-canyon | Telework rule covers only residence-headquarters; Phoenix conference: WN 10900 < AA 17900: book WN | yes |
| vireo-point | Passengers of size (241-247): both reservations approved; AS controlled 13900 is lowest (UA 15900 above the rate) | yes |
| willow-flat | 11 days: the 14-day line is a tip, the code is for < 7. WN lands 10:40 > 09:30; UA saver 17900 < 21900: book it | yes |
| yucca-strand | Bags do not change the ticket (262-271); WN 8900 < DL 12900, lowest; colleague's credit usable by any employee (144-148) | yes |
| alder-rook | Buy through Concur/CI Azumano (138-140); outside $159 is dearer anyway; AS controlled 15400 lowest | yes |
| basalt-cliff | Family holiday: 141-142, 211-212: refuse | yes |
| coyote-dell | Teleworker flying home to headquarters office days: 154-159, 61-65: refuse | yes |
| dove-terrace | Spouse: not state business (141-142, 211-212): refuse whoever pays | yes |

Points I weighed and kept:
- `tule-marsh` accepts only the refundable contract fare. Lines 136-137 ("must purchase the lowest cost airfare
  whenever possible") could be read to require Southwest still; but Example 1 names this exact justification,
  161-162 make non-refundable the first choice only when the dates are fixed, 178-182 put change penalties on the
  employee, and the traveller asks for refundable. Residual risk: a model that books Southwest with a short-notice
  code.
- `sage-inlet` declines a refundable request on fixed dates. Residual risk: a model reading the refundable reason
  code as a free choice. The request says the dates are set and the record shows nothing that justifies it.
- `kelp-ridge`/`laurel-wash` and `manzanita-pool`/`nopal-crest` differ only in the accepted reason codes (the
  numeric rules ask for a justification, not a different fare); an agent giving LOWEST_FARE passes both sides.
  The deadlines make the cheapest seat wrong in both.
- `coyote-dell`: lines 48-49 bar home-headquarters travel for everyone; the telework notes make it explicit.

## Template change requests

1. **Offer-level fare flags.** `Offer` has `refundable` but no contract-fare flag, fare brand ("Wanna Get Away",
   "Anytime", YCAL, capacity-controlled) or booking channel. Government handbooks (Caltrans, Georgia, likely others)
   turn on "contract fare" status. Suggest an optional `fare_basis` string on `Offer` (empty by default). Worked
   around with `Trip.contract_fares`.
2. **California airports and Southwest bases.** The world lacks SMF (Sacramento, Caltrans headquarters), OAK, SJC,
   BUR, ONT and FAT, and Southwest's hubs (LAS, DEN, PHX, AUS, MCO) include no California airport, so every in-state
   Southwest flight must connect through Las Vegas. Suggest SMF and OAK, and OAK/SJC/SMF as WN hubs (check
   `tools/world_diff.py`: adding hubs can move background offers on existing routes). Worked around: district offices
   in Oakland, Los Angeles and San Diego flying from SFO, LAX and SAN; in-state Southwest cases say connections are
   fine, so the layover phrase is not in play.
3. Georgia's request (first scenario in enum order must not be a REFUSE for `test_a_tampered_reference_fails`) still
   applies; `agate-cove`, a BOOK, is first here.

## Check outputs (final commit)

```
$ uv run pytest -q
244 passed, 3 skipped
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .   (stock: nanoagent/nanoagent/.venv/bin/nanoagent)
exit 0
$ nanoagent plugin pack . <scratch>/caltrans.tar.gz   (stock)
packed . into <scratch>/caltrans.tar.gz (182259 bytes)
$ nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py .
32 scenarios, 0 failures
```
