# Independent audit: caltrans-flight-policy (2026-11-25)

I audited the builder's commit 7aba2d1 against `WAVE3_AUDIT_BRIEF.md`, `WAVE3_BUILD_BRIEF.md` (lessons 1-12),
MASTER_PLAN section 4, EDGE_CASES 1-3 and 5, and the Georgia, FedEx Office, Goodman and Hill-Rom audits. I spent no
money and pushed nothing. Line numbers are lines of the frozen handbook (`src/plugin/data/policy.txt`).

## Method

I printed every scenario's trip record and pinned offers through the plugin's own `answer_key` path: fares, refundable
flag, seats, segments and local arrival times. Then I answered each case from lines 40-275 of the chapter alone. After
that I compared my answers with every accept set: decision, offer, cabin, reason, approver and clause.

## Verdict

**Pass after fixes.** On all 28 non-flag cases, my decision and booked offer agree with the key. The defects were in
the reason-code sets, plus one case where a second booking is defensible.

The four holds are sound:

- `egret-shoal`: lines 183-185 name only Southwest for in-state non-refundable fares. Lines 167-168 allow any fare
  below the contract rate. Both readings are defensible, and the hold accepts both offers.
- `hazel-kiln`: the connection takes 330 minutes against 170 for the nonstop and lands the afternoon before the
  workshop. Whether that "significantly ... delay[s] travel times" (174-175) is open. Both offers are accepted.
- `finch-arroyo`: the out-of-state request is pending (248-252).
- `granite-wren`: the second seat is not yet approved (246-247).

Twins differ in one fact each, and no request uses rule wording. The decline sentence is the last line of the task
instructions.

## Builder's open items, settled

1. **The short-notice twins test the rule now.** Before, `kelp-ridge`/`laurel-wash` and `manzanita-pool`/`nopal-crest`
   differed only in accepted reason codes, and LOWEST_FARE passed on both sides.
   - Lines 220-221 make a domestic booking under 7 days, or an international one under 30, a non-compliance booking.
     Lines 224-226 say Concur "will prompt and require that a Reason Code Justification(s) be provided before
     proceeding". So on the short side the reason is the justification.
   - `kelp-ridge` (6 days) accepts only DOMESTIC_SHORT_NOTICE_JUSTIFIED and ADVANCE_PURCHASE_TOO_LATE.
     `laurel-wash` (7 days) keeps LOWEST_FARE and NON_REFUNDABLE_BELOW_CONTRACT_FARE.
   - `manzanita-pool` booked Air Canada, a non-contracted carrier, so it needed a second justification (218). An agent
     giving NON_CONTRACT_CARRIER_JUSTIFIED would have passed both sides, and the twin would not have tested line 221.
     The world now offers United's own non-refundable 29900 on the contract flight, and Air Canada moves to 31900,
     which is allowed but dearer. United is the contract carrier, so the only justification is short notice.
   - The answer changes from ac-saver to ua-saver in both twins. The category, the ids and the twin fact (booked
     November 24 or 23) are unchanged. `manzanita-pool` (29 days) accepts only INTERNATIONAL_SHORT_NOTICE_JUSTIFIED
     and ADVANCE_PURCHASE_TOO_LATE. `nopal-crest` (30 days) accepts LOWEST_FARE and
     NON_REFUNDABLE_BELOW_CONTRACT_FARE.
   - In rules.py, a short-notice booking with nothing declined gives the justifications it needs (contract or
     refundable, non-contracted carrier, short notice) in place of the generic codes (`justification_codes`).
2. **`tule-marsh`: both bookings accepted.** The key now accepts {as-controlled, wn-saver}.
   - For the refundable contract fare: Example 1 (231-234) covers exactly this case, a short-notice assignment with
     the email on file. Lines 161-162 put non-refundable first only when the dates are fixed.
   - For Southwest: lines 136-137 are a "must ... whenever possible". Lines 183-185 say Southwest "offers the most
     flexibility in changing non-refundable flight reservations", which meets a schedule that may shift. The chapter
     never requires a refundable fare, and the Southwest flight is in-state, below the 15400 rate, and lands 10:15,
     before the 10:20 nonstop. It breaks no constraint.
   - A Southwest booking declines the request on the lowest-fare ground, so LOWEST_FARE and SOUTHWEST_IN_STATE_FARE
     are added (lesson 12). COMMERCIAL_AIR_TRAVEL (136-137) is added to the clauses.
   - The always-cheapest agent now passes this case. That is the price of not failing a defensible answer.
3. **`sage-inlet`: LOWEST_FARE dropped.** The booking (Southwest, refundable declined) is right: the dates are fixed,
   "just in case" is no justification (219, 231-239), and 161-162 and 136-137 apply.
   - The ground for declining is not the lowest-fare rule alone, because `tule-marsh` books a justified refundable
     fare although it is dearer. The ground is that nothing justifies the refundable fare.
   - So, like `poppy-ledge` here (YCAL declined at 203-207) and Georgia `hickory-fen`, only REFUNDABLE_FARE_NOT_ALLOWED
     is accepted. The decline sentence in the instructions points an agent to exactly that code.
4. **The 60-minute layover zone.** Only `quail-hollow` relies on it. Its connection adds 45 minutes but lands at
   11:35, before the 11:50 nonstop, the evening before the review, so it delays nothing and any careful reader agrees.
   - `elkhorn-reed`, `sage-inlet` and `tule-marsh` add 105 minutes. Each traveller has said a connection is fine, and
     the business is the next morning or the connection lands first. The key does not rest on the 60-minute number
     there.
   - No case lies between 61 and 159 added minutes. `hazel-kiln` (160) is the flag.
5. **Baseline 13 -> 12.** Item 2 adds `tule-marsh` and item 3 removes `sage-inlet`, which nets to 13. One more
   defensible change was needed: `elkhorn-reed` is now booked December 10 for December 15.
   - Five days is under 7 (220), so the case uses the short-notice rule of item 1 a second time, outside the twin.
   - It accepts DOMESTIC_SHORT_NOTICE_JUSTIFIED, ADVANCE_PURCHASE_TOO_LATE and NON_CONTRACT_CARRIER_JUSTIFIED (WN, 218).
     The booking is unchanged (wn-saver), and the `date_arithmetic` overlay is added.
   - It stays easy: one date subtraction, and the instructions already say days are calendar days.

## Other fixes

- `cypress-lark`: the BA fare needs the non-contracted-carrier justification (218), so the clause
  REASON_CODE_JUSTIFICATIONS is also accepted. It is an addition only.

## Seen and kept

- `poppy-ledge` does not accept LOWEST_FARE. The specific ground is 203-207, which is consistent with `sage-inlet`.
- `cypress-lark` keeps LOWEST_FARE because the chapter has no cabin rule, so the lowest-fare rule is the ground.
- `heron-quay`: Delta ties the contract fare at 16900, so LOWEST_FARE is rightly not accepted.
- `juniper-tide`: JAL at 142000 is not less than the 142000 rate (167-168), so the contract fare is the answer. The
  cheapest-seat agent picks JAL (listed first), so it fails here.
- `laurel-wash` and `nopal-crest` do not accept REASON_CODE_JUSTIFICATIONS as a clause, because their bookings need
  no justification. This matches the builder's choice for laurel-wash.
- The approver sets follow 4'. The out-of-state BOOKs accept the Division whose approval is on file. Unclear holds
  accept NOT_NAMED, SUPERVISOR, APPOINTING_AUTHORITY and APPROVAL_REQUIRED.

`MAX_PASS_ALWAYS_LOWEST`: **13 -> 12** (37.5%). The cases it passes are agate-cove, alder-rook, bodega-fern,
cypress-lark, fennel-bluff, garnet-slough, indigo-mesa, quail-hollow, tule-marsh, umber-canyon, vireo-point and
yucca-strand. I recounted them through the answer key. Always-flag still passes 2.

## Checks

```
uv run pytest -q                      244 passed, 3 skipped
uv run ruff check .                   All checks passed!
uv lock --check                       Resolved 42 packages
python3 ../_template/check_shared.py  : ok
stock_verify.py .                     32 scenarios, 0 failures
nanoagent plugin inspect . (stock)    exit 0
```
