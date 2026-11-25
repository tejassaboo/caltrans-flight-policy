# Validation notes: caltrans-flight-policy (paid wave 3 validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w3_2026-11-25/caltrans-flight-policy@w3/`, arm
`full`, DeepSeek V4 Flash (Nebius fp8), temperature 0, max_steps 6, max_tokens 8192, one run per scenario, at plugin
head bfcdbc0. Line numbers are lines of `src/plugin/data/policy.txt`.

## Results

23/32 valid (71.9%), mean field score 0.891, **easy 4/6** (elkhorn-reed, sage-inlet fail). By category: boundary
5/8, distractor 3/3, easy 4/6, flag 1/4, hidden 3/3, multi 4/5, refusal 3/3. $0.00196 billed per run, 3.94 calls
per run, 19,677 prompt tokens per call, none over the hosted 65,536 cap.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| elkhorn-reed | **easy** | right offer (Southwest wn-saver), LOWEST_FARE; key ADVANCE_PURCHASE_TOO_LATE, DOMESTIC_SHORT_NOTICE_JUSTIFIED or NON_CONTRACT_CARRIER_JUSTIFIED | **grader defect** | It found the short-notice rule ("Booking date Dec 10, travel Dec 15. That's 5 days ... less than 7 days") and weighed the code, then: "we're booking the lowest fare which is compliant ... LOWEST_FARE is the most general and appropriate reason". Nothing the traveller asked for is declined, and the booking rests on lines 136-137. APPROVER_REVIEW section 7 leaves `LOWEST_FARE` on bookings that decline nothing, and says to take it back "if `LOWEST_FARE` persists with the right offer". The audit removed it here only to cut the baseline. |
| kelp-ridge | boundary_twin | right offer (aa-saver), LOWEST_FARE; key the two short-notice codes | **grader defect** | The same reasoning: "Booking date Nov 25, travel Dec 1. That's 6 days ... DOMESTIC_SHORT_NOTICE_JUSTIFIED might be appropriate ... the main decision here is straightforward: book the lowest fare." Lines 224-226 describe what Concur asks the traveller for. The task's reason code is "why", and nothing is declined. This is 3 of 3 short-notice bookings. |
| manzanita-pool | boundary_twin | right offer (ua-saver), LOWEST_FARE; key the two international short-notice codes | **grader defect** | "Reason code LOWEST_FARE seems appropriate." This is the same ground as kelp-ridge, at 29 days against 30 (line 221). |
| sage-inlet | **easy** | no submit: the last call spent all 8,192 tokens on reasoning (8,525 reasoning tokens in the run) and returned empty content; key BOOK Southwest wn-saver, REFUNDABLE_FARE_NOT_ALLOWED | model slip (no answer) | The `.events` stream shows it reaching the keyed answer at least six times ("the refundable request is declined because the dates are fixed and the non-refundable fare is the lowest cost ... REFUNDABLE_FARE_NOT_ALLOWED"), then reopening it ("Hmm, I think the correct answer might be to book the refundable fare the traveller requested"), until max_tokens. Unlike Carter's amber-finch, the request and the record agree: "just in case", "the dates are set", `plans_fixed: true`. Lines 161-162 and 219 settle it, and the reasoning quotes both. Nothing in the case is defective. |
| egret-shoal | flag | BOOK Alaska capacity-controlled $139, CAPACITY_CONTROLLED_FARE_AVAILABLE; key FLAG (United $119 or the contract fare) | model slip | It set out both readings: "this might be interpreted as: in-state, only Southwest non-refundable is allowed ... But the general principle is lowest cost." Then it chose one: "the policy explicitly restricts in-state non-refundable to Southwest". Lines 183-187 against 167-168 and 136-137 are the open text the hold tests. |
| granite-wren | flag | right hold, offer, SUPERVISOR and clause; EXTRA_SEAT_APPROVED; key APPROVAL_REQUIRED | model slip | It saw that the code was wrong ("that reason code seems to indicate the extra seat was approved. But it's pending") and gave it anyway. The second seat's sign-off is PENDING (lines 246-247), so the code says the opposite of the case. |
| hazel-kiln | flag | BOOK nonstop contract fare $169, LOWEST_FARE; key FLAG (connection or nonstop) | **scenario defect** | The record shows `connections_ok: false` (the builder's default, meaning "the traveller has not said"). The request says nothing about connections. The model read the field as a refusal: "connections_ok is false, so the traveler doesn't want connections. So the $129 with a stop is not acceptable." It never reached lines 174-175. Honouring a stated refusal is a fair reading, and the record states one that the scenario does not intend. |
| quail-hollow | multi_rule | BOOK nonstop contract fare $169, CAPACITY_CONTROLLED_FARE_AVAILABLE; key the $129 connection | **scenario defect** | Same record field: "connections_ok false means the traveller doesn't want connections ... The traveller requires a non-stop flight". This is the flag twin of hazel-kiln with the same false field. Only these two records pair `connections_ok: false` with a cheaper connection that the key books or holds; redwood-spur's connection lands too late either way. |
| heron-quay | boundary_twin | BOOK Delta $169 non-refundable, LOWEST_FARE; key Alaska capacity-controlled $169 | model slip | "The Delta fare is the same price as the lowest ... There's no policy prohibiting Delta." It never read line 186-187 ("less costly than the out-of-state contracted airfare"). $169 equals the $169 rate, which is the designed boundary. The twin garnet-slough ($168.99) passed. |

## Fixes (this commit)

1. **Short-notice bookings (grader):** `LOWEST_FARE` is accepted beside the short-notice justifications in
   `default_booking`. The change is in `src/plugin/rules.py` and the byte-identical `verifier/rules.py`, plus the
   three keys in `tests/build_scenarios.py` and the README rows. It affects elkhorn-reed, kelp-ridge and
   manzanita-pool. The fare-describing codes the audit removed stay out.
2. **`connections_ok` records (scenario):** hazel-kiln and quail-hollow now carry the note "The traveller has not
   said whether a connecting flight would be acceptable." The words are the same in both, so the flag twins still
   differ only in layover time. The field, the fares, the keys and the ids are unchanged.

Not loosened: sage-inlet, egret-shoal, granite-wren, heron-quay.

**Cost of fix 1.** The 6/7-day pair (kelp-ridge/laurel-wash) and the 29/30-day pair (manzanita-pool/nopal-crest)
no longer separate `LOWEST_FARE` from the short-notice code. Both sides still need the right offer: the cheapest
seat lands late in all four cases. Lines 220-221 change what Concur asks for, not what the department buys. A twin
that turns on them can only test a code, and that is what produced the three false failures.

## Q2

The always-cheapest agent goes from **12 to 13 of 32 (40.6%)** (`MAX_PASS_ALWAYS_LOWEST = 13`), because elkhorn-reed
is added; its cheapest seat is the keyed Southwest fare. kelp-ridge and manzanita-pool still fail it, since their
cheapest seats land after the business starts. The 0.6 points over 40% are the price of not failing a defensible
answer on an easy case. Always-flag still passes 2.

## Re-score at this head (stored answers, no paid call)

26/32 (81.3%), easy 5/6. sage-inlet has no submission to score. The fix-1 cases now pass. hazel-kiln and
quail-hollow still fail on their old records, which changed.

## Re-run

Required: hazel-kiln and quail-hollow (their records changed), and sage-inlet (an easy case that must come back
valid; it is a slip, and nothing was changed to make it pass). Optional: elkhorn-reed, kelp-ridge and
manzanita-pool, to confirm fix 1.

## Checks

`uv run pytest -q` (244 passed, 3 skipped), `uv run ruff check .`, `uv lock --check`, `check_shared.py`,
`tools/stock_verify.py` (32 scenarios, 0 failures), stock `nanoagent plugin inspect .` (exit 0).
