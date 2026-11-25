"""The answer key's rules for the Caltrans Accounting Manual, Chapter 15 - Transportation (05/14/24), as exact
integer code. Byte-identical in src/plugin/rules.py and verifier/rules.py; it imports only modules a verifier
may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each
unclear phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a
new scenario cannot fall silently into untested logic.

The chapter has no cabin-class rule and no flight-length threshold. Its flight rules are about the fare:

- lines 136-137: "Travelers must purchase the lowest cost airfare whenever possible";
- lines 167-168: a non-refundable fare "may be purchased ... if the airfare is less than the DGS contracted
  refundable rate" (strict), restated for out-of-state travel at lines 186-187 ("less costly than");
- lines 183-185: in-state, non-refundable Southwest "Wanna Get Away" fares may be bought;
- lines 203-207: the capacity-controlled contract fare "should be used when seats are available" before the
  dearer YCAL fare, which it "can be upgraded to ... when necessary";
- lines 213-221: a refundable fare, a non-contracted carrier, a domestic flight booked less than 7 days ahead
  and an international flight booked less than 30 days ahead each need a reason code justification: they are
  booked, with that code, not refused;
- lines 141-142 and 211-212: no personal travel through the system or at the contract rates; lines 154-159
  (and 48-49, 61-65): no flights between residence and headquarters for a teleworker;
- lines 246-247: an extra seat takes two reservations, both approved by the supervisor; lines 248-252: an
  out-of-state approval process.

The offer schema has no contract-fare flag, so the trip record lists the city pair's contracted fares
(carrier, kind, one-way fare); a refundable offer of that carrier at that fare is the contract fare.

The duration hook. No rule turns on how long a flight is, so DURATION_RULES is empty and ``over`` knows no
rule. The one time rule, "as long as the layovers do not significantly impact business or delay travel times"
(lines 174-175), compares offers: a cheaper connection is clearly acceptable when it lands in time and adds at
most CLEAR_ADDED_MINUTES of elapsed time over the nonstop (or the traveller says connections are fine); a
connection that lands too late is out (it impacts business); more added time than that is the unclear phrase.

Approvers (template SYNC_NOTES 4'): a BOOK or REFUSE whose sign-off is on file accepts that role and NONE (the
supervisor is the appointing authority, lines 55-58, so both names are accepted); a hold awaiting a sign-off
accepts only the awaited roles.
"""

from contract import (
    Approver,
    Cabin,
    Clause,
    ContractFareKind,
    Decision,
    FareWish,
    Passenger,
    Purpose,
    ReasonCode,
    SignOffStatus,
    SignOffSubject,
)

from .world import days_between

HANDBOOK = "Caltrans Accounting Manual, Chapter 15 - Transportation (05/14/24)"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.TRANSPORTATION_GENERAL: "GENERAL POLICY",
    Clause.THIRD_PARTY_VENDORS: "THIRD PARTY VENDORS",
    Clause.CHOOSING_MODE: "CHOOSING A MODE OF TRANSPORTATION",
    Clause.EMPLOYEE_RESPONSIBILITY: "EMPLOYEE RESPONSIBILITY",
    Clause.SUPERVISOR_RESPONSIBILITY: "SUPERVISOR RESPONSIBILITY",
    Clause.COMMERCIAL_AIR_TRAVEL: "Commercial Air Travel",
    Clause.NON_REFUNDABLE_AIRFARE: "NON-REFUNDABLE AIRFARE",
    Clause.REFUNDABLE_AIRFARE: "REFUNDABLE AIRFARE",
    Clause.REASON_CODE_JUSTIFICATIONS: "REASON CODE JUSTIFICATION(S) FOR NON-COMPLIANCE AIRFARE",
    Clause.PASSENGERS_OF_SIZE: "PASSENGERS OF SIZE",
    Clause.OUT_OF_STATE_APPROVAL: "OUT OF STATE APPROVAL",
    Clause.INTERNATIONAL_AIRFARE: "INTERNATIONAL AIRFARE",
    Clause.CHECKED_BAGGAGE: "AIRLINE CHECK BAGGAGE POLICY",
    Clause.AIRFARE_REIMBURSEMENT_CLAIMS: "REIMBURSEMENT CLAIMS",
    Clause.PRIVATELY_OWNED_AIRCRAFT: "Privately-Owned Aircraft",
    Clause.AGENCY_RENTED_AIRCRAFT: "Agency Rented Aircraft",
    Clause.COMMERCIAL_CAR_RENTAL: "Commercial Car Rental",
    Clause.PRIVATE_VEHICLE_USE: "Private Vehicle Use",
    Clause.COST_COMPARISON_IN_LIEU: "COST COMPARISON (IN LIEU)",
    Clause.PARKING_AND_TOLLS: "Parking and Tolls",
    Clause.RAIL: "Rail/Amtrak",
    Clause.OTHER_MODES: "Other Modes of Transportation",
}

# No flight-length threshold in this handbook (see the module docstring).
DURATION_RULES = ()

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# The world's California airports: every trip leaves from one (the traveller's Caltrans district).
CALIFORNIA_AIRPORTS = {"LAX", "SFO", "SAN"}
IN_STATE_REGION = "California"
SOUTHWEST = "Southwest Airlines"
# Lines 220-221: "booked less than 7 days in advance" (domestic), "less than 30 days in advance"
# (international); strict.
DOMESTIC_NOTICE_DAYS = 7
INTERNATIONAL_NOTICE_DAYS = 30
# Lines 174-175: a connection adding at most this much elapsed time over the nonstop, and landing in time, is
# clearly not a significant delay (a design zone, not a handbook number; BUILD_NOTES.md).
CLEAR_ADDED_MINUTES = 60

IN_STATE_PHRASE = "Travelers may purchase non-refundable airfare for Southwest Airlines"
LAYOVER_PHRASE = "as long as the layovers do not significantly impact business or delay travel times"
# Who may settle a reading the text leaves open: nobody is named; the supervisor (the appointing authority)
# approves the reservation in Concur (lines 50-58, 138-140) and judges the reasonableness of the mode and its
# time against its cost (lines 112-117).
GAP_APPROVERS = [Approver.NOT_NAMED, Approver.SUPERVISOR, Approver.APPOINTING_AUTHORITY]
SUPERVISOR_ROLES = [Approver.SUPERVISOR, Approver.APPOINTING_AUTHORITY]
# Lines 248-252: the Division of Resource and Innovation administers the out-of-state approval process, and
# the program's out-of-state travel coordinator answers for it; neither is said to sign, so NOT_NAMED too.
OUT_OF_STATE_ROLES = [Approver.RESOURCE_AND_INNOVATION_DIVISION, Approver.PROGRAM_TRAVEL_COORDINATOR,
                      Approver.NOT_NAMED]


def over(rule, offer):
    """The duration hook: this handbook has no duration rule, so every name is unknown."""
    raise ValueError(f"this handbook has no duration rule {rule!r}")


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def lowest(offers, what):
    """The single cheapest offer; a scenario never ties two offers for a choice that matters."""
    if not offers:
        raise ValueError(f"no offer for {what}")
    low = min(offer.fare_cents for offer in offers)
    found = [offer for offer in offers if offer.fare_cents == low]
    if len(found) != 1:
        raise ValueError(f"{len(found)} offers tie for {what}; a scenario gives exactly one")
    return found[0]


def approved(trip, subject, roles=None):
    return [record for record in trip.sign_offs if record.subject == subject and record.status == SignOffStatus.APPROVED
            and (roles is None or record.role in roles) and days_between(record.date, trip.booking_date) >= 0]


def pending(trip, subject):
    return [record for record in trip.sign_offs if record.subject == subject and record.status == SignOffStatus.PENDING]


def roles_on_file(trip):
    """Every role whose sign-off is given and on file; a supervisor's is also the appointing authority's."""
    roles = []
    for record in trip.sign_offs:
        if record.status != SignOffStatus.APPROVED:
            continue
        roles.extend(SUPERVISOR_ROLES if record.role in SUPERVISOR_ROLES else [record.role])
    return roles


def scope_of(trip):
    """IN_STATE, OUT_OF_STATE or INTERNATIONAL, from the destination (every trip leaves California)."""
    if trip.origin.code not in CALIFORNIA_AIRPORTS:
        raise ValueError("a trip that does not leave California is not modelled")
    if trip.destination.country != "US":
        return "INTERNATIONAL"
    in_state = trip.destination_region == IN_STATE_REGION
    if in_state != (trip.destination.code in CALIFORNIA_AIRPORTS):
        raise ValueError("the destination region disagrees with the destination airport")
    return "IN_STATE" if in_state else "OUT_OF_STATE"


def refuse(trip, reasons, clauses, why):
    """A refusal relies on no sign-off; a sign-off on file for the trip goes unused (SYNC_NOTES 4(b))."""
    return answer(Decision.REFUSE, [], reasons, [Approver.NONE, *roles_on_file(trip)], clauses, why)


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers of its pinned searches: the decision, and every accepted
    offer id, cabin, reason, approver and section. ``hidden`` (answer_key_inputs) is unused here."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    scope = scope_of(trip)
    personal_clauses = [Clause.COMMERCIAL_AIR_TRAVEL, Clause.REFUNDABLE_AIRFARE]
    if trip.passenger == Passenger.SPOUSE_OR_FAMILY:
        return refuse(trip, [ReasonCode.COMPANION_NOT_COVERED, ReasonCode.CONTRACT_FARE_NOT_FOR_PERSONAL_TRAVEL,
                             ReasonCode.PERSONAL_TRAVEL_NOT_COVERED], personal_clauses,
                      "Lines 141-142: the reservation system is for Caltrans employees who travel on state business, "
                      "and its use for personal travel is prohibited; lines 211-212: contracted rates are only for "
                      "state business. A spouse's or family member's ticket is not state business: buy nothing.")
    if trip.passenger != Passenger.EMPLOYEE:
        raise ValueError(f"a {trip.passenger.value} passenger is not modelled")
    if trip.purpose_kind == Purpose.PERSONAL:
        return refuse(trip, [ReasonCode.PERSONAL_TRAVEL_NOT_COVERED, ReasonCode.CONTRACT_FARE_NOT_FOR_PERSONAL_TRAVEL],
                      personal_clauses,
                      "Lines 141-142: using the reservation system for personal travel is prohibited; lines 211-212: "
                      "contracted airfare rates are not extended to employees for personal travel. Buy nothing.")
    if trip.purpose_kind == Purpose.HEADQUARTERS_OFFICE_DAY:
        if not trip.on_telework:
            raise ValueError("an office day without telework status is not modelled")
        return refuse(trip, [ReasonCode.COMMUTING_NOT_REIMBURSABLE, ReasonCode.PERSONAL_TRAVEL_NOT_COVERED],
                      [Clause.COMMERCIAL_AIR_TRAVEL, Clause.TRANSPORTATION_GENERAL],
                      "Lines 154-159 (and 61-65, 48-49): air travel between residence and headquarters is not "
                      "reimbursable for an employee on telework status, and telework does not move the headquarters. "
                      "The flight takes the teleworker from home to the headquarters office: buy nothing.")
    return business_trip(trip, offers, scope)


def business_trip(trip, offers, scope):
    seated = [offer for offer in offers if offer.seats_available and offer.cabin == Cabin.ECONOMY]
    if trip.must_arrive_by:
        # Lines 136-137 "whenever possible", 174-175 "do not significantly impact business": a flight that lands
        # after the business needs the traveller cannot be the one to buy.
        late = [offer for offer in seated if offer.segments[-1].arrive_local > trip.must_arrive_by]
        if not late:
            raise ValueError("an arrival limit that rules out nothing is not modelled")
        seated = [offer for offer in seated if offer not in late]
    fares = sort_fares(trip, seated, scope)
    clauses = [Clause.COMMERCIAL_AIR_TRAVEL, Clause.NON_REFUNDABLE_AIRFARE, Clause.REFUNDABLE_AIRFARE]
    if scope == "INTERNATIONAL":
        clauses.append(Clause.INTERNATIONAL_AIRFARE)
    if scope != "IN_STATE":
        if pending(trip, SignOffSubject.OUT_OF_STATE_TRIP):
            return out_of_state_hold(trip, fares)
        if not approved(trip, SignOffSubject.OUT_OF_STATE_TRIP, [Approver.RESOURCE_AND_INNOVATION_DIVISION]):
            raise ValueError("an out-of-state trip with no approval asked for is not modelled")
        clauses.append(Clause.OUT_OF_STATE_APPROVAL)
    if not approved(trip, SignOffSubject.TRIP, SUPERVISOR_ROLES):
        raise ValueError("a business trip without the supervisor's approval of the trip is not modelled")
    if trip.extra_seat_needed:
        return extra_seat(trip, fares, clauses)
    if trip.requested_cabin != Cabin.ECONOMY:
        return better_cabin(trip, fares, clauses)
    if trip.requested_fare == FareWish.REFUNDABLE:
        return refundable_wish(trip, fares, clauses)
    if trip.requested_fare == FareWish.YCAL:
        return ycal_wish(trip, fares, clauses)
    if trip.requested_airline:
        return airline_wish(trip, fares, clauses)
    if trip.ticket_credits and not credit_fits(trip, default_choice(fares)[0]):
        raise ValueError("a credit that the booked airline cannot use is not modelled")
    return default_booking(trip, fares, clauses)


def sort_fares(trip, seated, scope):
    """The seated economy offers of a trip sorted by the chapter's fare rules, as a dict: contract fares (lines
    194-207), non-refundable fares allowed below the contract rate (lines 167-168, 183-187), the in-state
    non-refundable fares of other airlines that lines 183-185 leave open, and those excluded."""
    if not trip.contract_fares:
        raise ValueError("a city pair without contract fares is not modelled")
    fares = {"trip": trip, "scope": scope, "carriers": {fare.carrier for fare in trip.contract_fares}}
    fares["contract"] = [offer for offer in seated if kind_of(trip, offer) is not None]
    if any(offer.refundable and kind_of(trip, offer) is None for offer in seated):
        raise ValueError("a refundable fare that is not a contract fare is not modelled")
    if not fares["contract"]:
        raise ValueError("a trip whose contract fares are all sold out is not modelled")
    fares["rate_offer"] = lowest(fares["contract"], "the contract rate")
    rate = fares["rate"] = fares["rate_offer"].fare_cents
    listed = min(fare.fare_cents for fare in trip.contract_fares)
    fares["nonref"] = [offer for offer in seated if not offer.refundable]
    if any(listed <= offer.fare_cents < rate for offer in fares["nonref"]):
        raise ValueError("a non-refundable fare between the sold-out and the open contract rate is not modelled")
    allowed, unclear, excluded = [], [], []
    for offer in fares["nonref"]:
        if scope == "IN_STATE" and offer.carrier == SOUTHWEST:
            if offer.fare_cents >= rate:
                raise ValueError("an in-state Southwest fare at or above the contract rate is not modelled")
            allowed.append(offer)
        elif offer.fare_cents < rate:
            (unclear if scope == "IN_STATE" else allowed).append(offer)
        else:
            excluded.append(offer)
    fares.update(allowed_nonref=allowed, unclear=unclear, excluded=excluded, allowed=fares["contract"] + allowed)
    return fares


def kind_of(trip, offer):
    """The contract fare kind of a refundable offer whose carrier and fare the trip record lists, else None."""
    if not offer.refundable:
        return None
    for fare in trip.contract_fares:
        if fare.carrier == offer.carrier and fare.fare_cents == offer.fare_cents:
            return fare.kind
    return None


def default_choice(fares):
    """(the cheapest allowed offer, a hold over unclear words or None, routing reasons)."""
    trip = fares["trip"]
    low = lowest(fares["allowed"], "the lowest allowed fare")
    if fares["unclear"] and min(offer.fare_cents for offer in fares["unclear"]) < low.fare_cents:
        other = lowest(fares["unclear"], "the lowest in-state non-refundable fare")
        return low, ("in-state", [other, low]), []
    if low.stops == 0:
        return low, None, []
    nonstops = [offer for offer in fares["allowed"] if offer.stops == 0]
    if not nonstops:
        raise ValueError("a connection with no nonstop to compare is not modelled")
    nonstop = lowest(nonstops, "the lowest allowed nonstop")
    added = low.elapsed_minutes - nonstop.elapsed_minutes
    if trip.connections_ok or added <= CLEAR_ADDED_MINUTES:
        return low, None, [ReasonCode.ALTERNATE_ROUTE_WITHIN_MARGIN, ReasonCode.COST_SAVINGS]
    return low, ("layover", [low, nonstop], added), []


def notice_codes(trip, scope):
    """Lines 220-221: a reason code justification for a domestic flight booked less than 7 days ahead, or an
    international one less than 30 days ahead (calendar days from the booking date to the travel date)."""
    ahead = days_between(trip.booking_date, trip.travel_date)
    limit, code = ((INTERNATIONAL_NOTICE_DAYS, ReasonCode.INTERNATIONAL_SHORT_NOTICE_JUSTIFIED) if scope == "INTERNATIONAL"
                   else (DOMESTIC_NOTICE_DAYS, ReasonCode.DOMESTIC_SHORT_NOTICE_JUSTIFIED))
    return [code, ReasonCode.ADVANCE_PURCHASE_TOO_LATE] if ahead < limit else []


def justification_codes(trip, fares, chosen):
    """Lines 213-221 and 224-226: the reason code justifications Concur asks for before it books this fare (a
    non-contracted carrier, a refundable fare, a short-notice booking)."""
    codes = []
    if kind_of(trip, chosen) is not None:
        codes.append(ReasonCode.REFUNDABLE_FARE_JUSTIFIED)
    if chosen.carrier not in fares["carriers"]:
        codes.append(ReasonCode.NON_CONTRACT_CARRIER_JUSTIFIED)
    return codes + notice_codes(trip, fares["scope"])


def offer_codes(trip, fares, chosen):
    """The codes that describe the booked fare: contract or non-refundable, and the justifications of lines
    213-221 it needs."""
    codes = []
    kind = kind_of(trip, chosen)
    if kind is not None:
        codes += [ReasonCode.STATE_CONTRACT_FARE, ReasonCode.REFUNDABLE_FARE_JUSTIFIED]
        codes.append(ReasonCode.CAPACITY_CONTROLLED_FARE_AVAILABLE if kind == ContractFareKind.CAPACITY_CONTROLLED
                     else ReasonCode.CAPACITY_CONTROLLED_SOLD_OUT)
        if fares["excluded"]:  # a non-refundable fare passed over for not being below the contract rate
            codes.append(ReasonCode.NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE)
    else:
        codes.append(ReasonCode.NON_REFUNDABLE_BELOW_CONTRACT_FARE)
        if fares["scope"] == "IN_STATE":
            codes.append(ReasonCode.SOUTHWEST_IN_STATE_FARE)
    if chosen.carrier not in fares["carriers"]:
        codes.append(ReasonCode.NON_CONTRACT_CARRIER_JUSTIFIED)
    return codes + notice_codes(trip, fares["scope"])


def credit_fits(trip, chosen):
    """Lines 144-148: Southwest unused ticket credits should be used first, by any employee."""
    if len(trip.ticket_credits) != 1:
        raise ValueError("more than one credit is not modelled")
    credit = trip.ticket_credits[0]
    return credit.airline == chosen.carrier and days_between(trip.travel_date, credit.usable_through) >= 0


def booked(trip, offers, reasons, clauses, why):
    """A BOOK resting on the sign-offs on file: those roles and NONE are accepted (SYNC_NOTES 4')."""
    return answer(Decision.BOOK, offers, reasons, [Approver.NONE, *roles_on_file(trip)], clauses, why)


def unclear_hold(fares, hold, clauses):
    if hold[0] == "in-state":
        return answer(Decision.FLAG_FOR_APPROVAL, hold[1], [ReasonCode.UNCLEAR_POLICY_TEXT, ReasonCode.APPROVAL_REQUIRED],
                      GAP_APPROVERS, [Clause.NON_REFUNDABLE_AIRFARE, Clause.COMMERCIAL_AIR_TRAVEL],
                      "Lines 167-168 allow a non-refundable fare below the DGS contracted refundable rate, from any "
                      "airline; lines 183-185 name only Southwest for in-state travel, against 'any carrier' for "
                      "out-of-state travel at lines 186-187. This in-state fare of another airline is below the "
                      "contract rate: one reading books it as the lowest cost airfare (lines 136-137), the other books "
                      "the contract fare. Hold either for a decision.", phrase=IN_STATE_PHRASE)
    return answer(Decision.FLAG_FOR_APPROVAL, hold[1], [ReasonCode.UNCLEAR_POLICY_TEXT, ReasonCode.APPROVAL_REQUIRED],
                  GAP_APPROVERS, [Clause.NON_REFUNDABLE_AIRFARE, Clause.COMMERCIAL_AIR_TRAVEL],
                  f"Lines 174-175: consider flights with stops 'as long as the layovers do not significantly impact "
                  f"business or delay travel times'. The cheaper connection lands in time but adds {hold[2]} minutes "
                  "over the nonstop, and the chapter does not say what delay is significant: one reading books it "
                  "as the lowest cost airfare (lines 136-137), the other books the nonstop. Hold either.",
                  phrase=LAYOVER_PHRASE)


def default_booking(trip, fares, clauses):
    """Lines 136-137: the lowest cost airfare among the fares the chapter allows."""
    chosen, hold, routing = default_choice(fares)
    if hold is not None:
        return unclear_hold(fares, hold, clauses)
    reasons = [ReasonCode.LOWEST_FARE, *offer_codes(trip, fares, chosen), *routing]
    if notice_codes(trip, fares["scope"]):
        # Lines 220-221 and 224-226: a short-notice booking cannot proceed without its reason code justification,
        # so the reason given is a justification the booking needs (the short-notice one among them), not the
        # generic lowest-fare or fare-describing codes: this is what the 6/7-day and 29/30-day twins test.
        if trip.ticket_credits:
            raise ValueError("a short-notice booking with a ticket credit is not modelled")
        reasons = justification_codes(trip, fares, chosen)
    why = ("Lines 136-137: the lowest cost airfare. Lines 167-168 and 186-187 allow a non-refundable fare only below "
           f"the contract rate of {fares["rate"]} cents")
    if trip.must_arrive_by:
        why += "; a cheaper flight that lands after the business starts cannot serve the trip"
    if routing:
        why += "; the connection's layover does not significantly delay the trip (lines 174-175)"
    if trip.ticket_credits:
        reasons.append(ReasonCode.UNUSED_TICKET_CREDIT_APPLIED)
        why += "; the Southwest credit on file is applied first (lines 144-148: any employee may use it)"
    return booked(trip, [chosen], reasons, clauses + justification_clause(reasons), why + ".")


def justification_clause(reasons):
    justified = {ReasonCode.NON_CONTRACT_CARRIER_JUSTIFIED, ReasonCode.REFUNDABLE_FARE_JUSTIFIED,
                 ReasonCode.DOMESTIC_SHORT_NOTICE_JUSTIFIED, ReasonCode.INTERNATIONAL_SHORT_NOTICE_JUSTIFIED}
    return [Clause.REASON_CODE_JUSTIFICATIONS] if justified & set(reasons) else []


def better_cabin(trip, fares, clauses):
    """No section allows a cabin above economy; lines 136-137 ask for the lowest cost airfare."""
    if trip.requested_cabin != Cabin.BUSINESS:
        raise ValueError("a request for a cabin other than business is not modelled")
    chosen, hold, routing = default_choice(fares)
    if hold is not None or routing:
        raise ValueError("a business request with a routing or in-state question is not modelled")
    if notice_codes(trip, fares["scope"]):
        raise ValueError("a short-notice business request is not modelled")
    # The booked fare may need a justification of lines 213-221 (a non-contracted carrier), so that section is
    # accepted beside the ones the decline rests on.
    return booked(trip, [chosen], [ReasonCode.LOWEST_FARE, ReasonCode.UPGRADE_NOT_ELIGIBLE],
                  clauses + justification_clause(offer_codes(trip, fares, chosen)),
                  "Lines 136-137: travelers must purchase the lowest cost airfare whenever possible, and the chapter "
                  "grants no better cabin: the lowest allowed economy fare, not business.")


def refundable_wish(trip, fares, clauses):
    """Lines 161-162: consider a non-refundable fare first when the dates are fixed and a change is unlikely;
    lines 219 and 231-234: a refundable fare needs a reason code, justified for example by a short-notice
    assignment documented in an email."""
    cheaper = [offer for offer in fares["allowed_nonref"] if offer.fare_cents < fares["rate"]]
    if not cheaper:
        raise ValueError("a refundable request with no cheaper non-refundable fare is not modelled")
    if trip.assignment_email_on_file and not trip.plans_fixed:
        # Two defensible bookings. Granting the request: Example 1 (lines 231-234) names a refundable fare chosen
        # for a short-notice assignment, documented by email, as a justification, and lines 161-162 put a
        # non-refundable fare first only when the dates are fixed; the lowest refundable fare is the contract fare.
        # Declining it: lines 136-137 ("must purchase the lowest cost airfare whenever possible") still hold, and
        # lines 183-185 say Southwest "offers the most flexibility in changing non-refundable flight reservations",
        # which meets the shifting schedule; the handbook never requires a refundable fare.
        chosen = fares["rate_offer"]
        cheapest, hold, _ = default_choice(fares)
        if hold is not None or cheapest.carrier != SOUTHWEST or fares["scope"] != "IN_STATE":
            raise ValueError("a justified refundable request without an in-state Southwest alternative is not modelled")
        reasons = [ReasonCode.REFUNDABLE_FARE_JUSTIFIED, ReasonCode.STATE_CONTRACT_FARE, *notice_codes(trip, fares["scope"]),
                   ReasonCode.LOWEST_FARE, ReasonCode.SOUTHWEST_IN_STATE_FARE]
        return booked(trip, [chosen, cheapest], reasons,
                      [Clause.REASON_CODE_JUSTIFICATIONS, Clause.REFUNDABLE_AIRFARE, Clause.NON_REFUNDABLE_AIRFARE,
                       Clause.COMMERCIAL_AIR_TRAVEL],
                      "Lines 231-234 (Example 1): a refundable fare chosen for a short-notice assignment is justified "
                      "by the email on file; lines 161-162 put a non-refundable fare first only when the dates are "
                      "fixed. The traveller asks for a refundable fare: the contract fare, the lowest refundable one. "
                      "Booking Southwest instead is defensible too: lines 136-137 ask for the lowest cost airfare "
                      "whenever possible, and lines 183-185 call Southwest the most flexible for changes.")
    if trip.plans_fixed and not trip.assignment_email_on_file:
        chosen, hold, _ = default_choice(fares)
        if hold is not None or kind_of(trip, chosen) is not None:
            raise ValueError("a declined refundable request that does not book a non-refundable fare is not modelled")
        # The ground for declining is that nothing justifies a refundable fare (lines 161-162, 219), not the
        # lowest-fare rule alone (a justified refundable fare is booked although dearer), so LOWEST_FARE is not
        # accepted (brief lesson 12, as for the YCAL request declined at lines 203-207).
        return booked(trip, [chosen], [ReasonCode.REFUNDABLE_FARE_NOT_ALLOWED],
                      clauses + [Clause.REASON_CODE_JUSTIFICATIONS],
                      "Lines 161-162: with the dates fixed and a change unlikely, consider the non-refundable fare "
                      "first; lines 136-137: the lowest cost airfare. Nothing on file justifies a refundable fare "
                      "(lines 219, 231-239): book the lowest allowed fare.")
    raise ValueError("this mix of plans and documentation is not modelled")


def ycal_wish(trip, fares, clauses):
    """Lines 203-207: the capacity-controlled fare is cheaper than YCAL and should be used when seats are
    available; it can be upgraded to YCAL when necessary."""
    controlled = [offer for offer in fares["contract"] if kind_of(trip, offer) == ContractFareKind.CAPACITY_CONTROLLED]
    chosen, hold, routing = default_choice(fares)
    if hold is not None or routing:
        raise ValueError("a YCAL request with a routing or in-state question is not modelled")
    if controlled:
        if chosen not in controlled:
            raise ValueError("a YCAL request where a non-refundable fare is lowest is not modelled")
        return booked(trip, [chosen], [ReasonCode.CAPACITY_CONTROLLED_FARE_AVAILABLE, ReasonCode.UPGRADE_NOT_ELIGIBLE],
                      [Clause.REFUNDABLE_AIRFARE, Clause.COMMERCIAL_AIR_TRAVEL],
                      "Lines 203-207: capacity-controlled contract seats are available, and they should be used "
                      "before the dearer YCAL fare; nothing makes the YCAL upgrade necessary.")
    if kind_of(trip, chosen) != ContractFareKind.YCAL:
        raise ValueError("a YCAL request where another fare is lowest is not modelled")
    return booked(trip, [chosen], [ReasonCode.LOWEST_FARE, *offer_codes(trip, fares, chosen)],
                  clauses + [Clause.REASON_CODE_JUSTIFICATIONS],
                  "Lines 203-207: the capacity-controlled seats are sold out, so the YCAL contract fare, which the "
                  "traveller asks for, is the one to use; it is also the lowest allowed fare (lines 136-137).")


def airline_wish(trip, fares, clauses):
    """An airline the traveller asks for: granted when its fare is the one the rules give; declined when its
    non-refundable fare is not below the contract rate (lines 167-168, 186-187)."""
    chosen, hold, routing = default_choice(fares)
    if hold is not None or routing:
        raise ValueError("an airline request with a routing or in-state question is not modelled")
    if chosen.carrier == trip.requested_airline:
        return booked(trip, [chosen], [ReasonCode.LOWEST_FARE, ReasonCode.LOYALTY_PROGRAM_PREFERENCE,
                                       *offer_codes(trip, fares, chosen)],
                      clauses + justification_clause(offer_codes(trip, fares, chosen)),
                      f"Lines 167-168 and 186-187: the {chosen.carrier} non-refundable fare is less than the contract "
                      f"rate of {fares["rate"]} cents, so it is allowed, and it is the lowest cost airfare (lines "
                      "136-137): book the airline asked for.")
    theirs = [offer for offer in fares["nonref"] if offer.carrier == trip.requested_airline]
    if not theirs or any(offer in fares["allowed_nonref"] for offer in theirs) or kind_of(trip, chosen) is None:
        raise ValueError("this airline request is not modelled")
    reasons = [ReasonCode.NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE, ReasonCode.STATE_CONTRACT_FARE,
               ReasonCode.PREFERRED_CARRIER_REQUIRED]
    if min(offer.fare_cents for offer in theirs) > chosen.fare_cents:
        reasons.append(ReasonCode.LOWEST_FARE)  # dearer, so the lowest-fare rule declines it too
    return booked(trip, [chosen], reasons, clauses + [Clause.AIRFARE_REIMBURSEMENT_CLAIMS],
                  f"Lines 186-187: a non-refundable fare from any carrier is allowed only if less costly than the "
                  f"contracted airfare; the {trip.requested_airline} fare is not below the contract rate of "
                  f"{fares["rate"]} cents (line 285: airfare above the state contracted rate is not reimbursable). "
                  "Book the contract fare.")


def extra_seat(trip, fares, clauses):
    """Lines 241-247: a traveller who cannot lower the armrests books an additional seat: two reservations, and
    the supervisor approves both."""
    chosen, hold, routing = default_choice(fares)
    if hold is not None or routing or trip.requested_fare != FareWish.ANY or trip.requested_airline:
        raise ValueError("an extra seat with another wish is not modelled")
    first = approved(trip, SignOffSubject.FIRST_SEAT_RESERVATION, SUPERVISOR_ROLES)
    second = approved(trip, SignOffSubject.EXTRA_SEAT_RESERVATION, SUPERVISOR_ROLES)
    if first and second:
        reasons = [ReasonCode.EXTRA_SEAT_APPROVED, ReasonCode.LOWEST_FARE, *offer_codes(trip, fares, chosen)]
        return booked(trip, [chosen], reasons, [Clause.PASSENGERS_OF_SIZE, *clauses, *justification_clause(reasons)],
                      "Lines 246-247: two reservations, both approved by the supervisor, are on file; book the lowest "
                      "cost airfare for both seats (lines 136-137).")
    if not (pending(trip, SignOffSubject.FIRST_SEAT_RESERVATION) or pending(trip, SignOffSubject.EXTRA_SEAT_RESERVATION)):
        raise ValueError("an extra seat with no approval asked for is not modelled")
    return answer(Decision.FLAG_FOR_APPROVAL, [chosen], [ReasonCode.APPROVAL_REQUIRED],
                  SUPERVISOR_ROLES, [Clause.PASSENGERS_OF_SIZE],
                  "Lines 246-247: the supervisor must approve both reservations; only one is approved. Hold the lowest "
                  "cost fare until the second approval is given.")


def out_of_state_hold(trip, fares):
    """Lines 248-252: out-of-state travel goes through an approval process; the request is pending."""
    chosen, hold, _ = default_choice(fares)
    if hold is not None or trip.requested_fare != FareWish.ANY or trip.requested_airline or trip.extra_seat_needed:
        raise ValueError("a pending out-of-state approval with another question is not modelled")
    return answer(Decision.FLAG_FOR_APPROVAL, [chosen], [ReasonCode.APPROVAL_REQUIRED], OUT_OF_STATE_ROLES,
                  [Clause.OUT_OF_STATE_APPROVAL],
                  "Lines 248-252: out-of-state travel goes through the approval process the Division of Resource and "
                  "Innovation administers; the trip's out-of-state request is still pending. Hold the lowest allowed "
                  "fare (lines 136-137, 186-187) until it is approved.")
