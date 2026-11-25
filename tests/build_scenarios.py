"""Writes the Caltrans Chapter 15 scenario JSON files (authoring aid; the JSON files are the truth).

    python3 tests/build_scenarios.py

Every line number is a line of the frozen handbook (src/plugin/data/policy.txt). Not collected by pytest.
"""

import hashlib
import json
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
POLICY = (PLUGIN / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = PLUGIN / "src/plugin/data/scenarios"


def norm(text):
    return " ".join(text.split())


def keep(a, b, why, quote=None):
    text = norm(" ".join(POLICY[a - 1:b]))
    quote = text if quote is None else quote
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote, "why": why}


def near(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "quote": quote, "why": why}


# ----- the clauses the answers rest on -----
LOWEST = keep(136, 137, "the lowest cost airfare whenever possible",
              "Travelers must purchase the lowest cost airfare whenever possible")
CONCUR = keep(138, 140, "airline reservations only through Concur or the state travel agency",
              "Airline reservations must be purchased using the on-line booking system Concur, or directly with the "
              "state travel agency, CI Azumano.")
PERSONAL_SYSTEM = keep(141, 142, "the reservation system is for state business; personal travel is prohibited")
CREDITS = keep(144, 148, "Southwest unused ticket credits first, usable by any employee")
TELEWORK_AIR = keep(154, 159, "no air travel between residence and headquarters on telework status")
CONSIDER = keep(161, 162, "consider a non-refundable fare first when the dates are fixed",
                "Travelers should first consider purchasing a non-refundable fare if the trip dates are fixed and "
                "there is a low probability of a change in plans.")
NONREF = keep(167, 168, "non-refundable only if less than the DGS contracted refundable rate")
ROUTING = keep(174, 175, "connections as long as the layovers do not significantly delay the trip")
IN_STATE = keep(183, 185, "in-state: non-refundable Southwest 'Wanna Get Away' fares")
OUT_OF_STATE = keep(186, 187, "out-of-state: non-refundable from any carrier if less costly than the contract fare")
CONTRACT = keep(194, 199, "DGS contracted refundable fares for in-state, out-of-state and international city pairs")
CONTROLLED = keep(203, 207, "capacity-controlled contract fares before YCAL when seats are available")
CONTRACT_PERSONAL = keep(211, 212, "contracted rates only for state business, not personal travel")
REASONS = keep(214, 221, "reason code justifications: non-contracted carrier, refundable, short-notice bookings")
EXAMPLE_ONE = keep(231, 234, "a refundable fare for a short-notice assignment, documented by email")
EXTRA_SEAT = keep(246, 247, "two reservations for an extra seat, both approved by the supervisor")
SIZE = keep(241, 245, "who books an additional seat")
OOS_APPROVAL = keep(249, 252, "the out-of-state travel approval process")
ABOVE_CONTRACT = keep(283, 285, "airfare above the state contracted rate is not reimbursable")
COMMUTE = keep(48, 49, "travel between home and headquarters is not allowed")
TELEWORK = keep(61, 65, "telework does not move the headquarters; residence-headquarters travel not reimbursable")
APPOINTING = keep(50, 58, "the appointing authority (a supervisor) approves travel reservations in Concur")

# ----- nearby clauses that must not change the answer -----
D_TIP = near(170, 171, "Non-refundable fares are typically lower in price when reservations are made at least 14 days "
             "in advance.", "a cost-saving tip, not a bar on later non-refundable fares")
D_BAGS = near(262, 266, "The State's policy is to only pay for the cost of the ticket and one bag per traveler.",
              "bag fees are claimed after the trip; they do not change the ticket")
D_EXTRA_BAGS = near(266, 267, "For travelers requesting reimbursement for more than one bag, a justification",
                    "the second bag needs a justification on the claim, not a different flight")
D_VENDORS = near(67, 72, "A justification is required on the TEC explaining why the department's travel reservation "
                 "system (via CI Azumano) was not used.", "third-party purchases are a claim question, not a fare")
D_EXPEDIA = near(288, 288, "Third party vendor purchases (Expedia, Priceline, etc.).",
                 "the outside fare is not one the department buys")
D_MILES = near(93, 95, "State employees may use frequent flyer miles and/or points for personal use",
               "miles may be kept; they do not make a dearer fare allowed")
D_PHONE = near(254, 257, "state employees are encouraged to make their reservations via telephonic reservation",
               "how to book abroad, not which fare")
D_ANYTIME = near(208, 210, "The \"Anytime\" fare is fully refundable.", "a Southwest refundable fare, not offered here")
D_PENALTY = near(178, 182, "Penalties incurred for flight changes or cancellations may be the responsibility of the "
                 "employee", "change penalties after booking, not the fare choice")
D_ONE_WAY = near(200, 200, "Note: Prices indicated reflect a one-way fare.", "contract fares are one way")
D_UPGRADE = near(206, 207, "The fares can be upgraded to YCAL when necessary.", "an upgrade only when necessary")
D_MODE = near(84, 85, "Distance to be traveled.", "choosing a mode, not a fare")
D_NO_MOTOR = near(988, 991, "Privately owned motorcycles and motor-driven bicycles are not authorized",
                  "another mode's rule")

DISTRICT_4 = "Caltrans District 4 office, Oakland, CA"
DISTRICT_7 = "Caltrans District 7 office, Los Angeles, CA"
DISTRICT_11 = "Caltrans District 11 office, San Diego, CA"
HOME = {"SFO": ("Oakland, CA", DISTRICT_4), "LAX": ("Los Angeles, CA", DISTRICT_7), "SAN": ("San Diego, CA", DISTRICT_11)}
REGION = {"SFO": "California", "LAX": "California", "SAN": "California", "DEN": "Colorado", "SEA": "Washington",
          "PHX": "Arizona", "LAS": "Nevada", "LHR": "United Kingdom", "NRT": "Japan", "YVR": "Canada"}

# The DGS contracted fares per city pair (either direction): carrier, capacity-controlled and YCAL, one way.
CONTRACT_FARES = {
    frozenset(("LAX", "SFO")): ("Alaska Airlines", 13900, 26800),
    frozenset(("SAN", "SFO")): ("Alaska Airlines", 15400, 29800),
    frozenset(("LAX", "DEN")): ("United Airlines", 21900, 41200),
    frozenset(("LAX", "SEA")): ("Alaska Airlines", 16900, 33800),
    frozenset(("SFO", "SEA")): ("Alaska Airlines", 16900, 33800),
    frozenset(("LAX", "PHX")): ("American Airlines", 19800, 37600),
    frozenset(("SFO", "DEN")): ("United Airlines", 22900, 43800),
    frozenset(("SAN", "PHX")): ("American Airlines", 17900, 33600),
    frozenset(("LAX", "LAS")): ("Delta Air Lines", 12900, 24800),
    frozenset(("SFO", "LHR")): ("United Airlines", 118000, 196000),
    frozenset(("SFO", "NRT")): ("United Airlines", 142000, 228000),
    frozenset(("SFO", "YVR")): ("United Airlines", 38900, 71000),
}


def contract_fares(origin, destination):
    carrier, controlled, ycal = CONTRACT_FARES[frozenset((origin, destination))]
    return [{"carrier": carrier, "kind": "CAPACITY_CONTROLLED", "fare_cents": controlled},
            {"carrier": carrier, "kind": "YCAL", "fare_cents": ycal}]


def sign(role, name, subject, status="APPROVED", date="2026-11-20"):
    return {"role": role, "name": name, "subject": subject, "status": status, "date": date}


# connections_ok is false when the traveller has said nothing about connections; validation w3 showed the bare
# field read as a refusal, so the records whose cheapest fare connects say so in words.
NO_CONNECTION_VIEW = "The traveller has not said whether a connecting flight would be acceptable."


def trip_ok(name="Dana Whitfield", date="2026-11-20"):
    return sign("SUPERVISOR", name, "TRIP", date=date)


def oos_ok(date="2026-11-20", status="APPROVED"):
    return sign("RESOURCE_AND_INNOVATION_DIVISION", "Division of Resource and Innovation", "OUT_OF_STATE_TRIP",
                status=status, date=date)


def trip(origin, destination, **fields):
    residence, office = HOME[origin]
    base = {
        "traveller_name": "", "traveller_title": "", "passenger": "EMPLOYEE", "accompanies": "",
        "headquarters": office, "residence": residence, "on_telework": False, "origin": origin,
        "destination": destination, "destination_region": REGION[destination], "travel_date": "",
        "booking_date": "2026-11-23", "purpose": "", "purpose_kind": "MEETING", "must_arrive_by": "",
        "requested_cabin": "ECONOMY", "requested_airline": "", "requested_fare": "ANY", "connections_ok": False,
        "plans_fixed": True, "assignment_email_on_file": False, "extra_seat_needed": False,
        "contract_fares": contract_fares(origin, destination), "ticket_credits": [],
        "sign_offs": [trip_ok()] + ([] if REGION[destination] == "California" else [oos_ok()]), "notes": [],
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    return base


def fl(carrier, depart, minutes=None, via=None, layovers=None):
    spec = {"carrier": carrier, "depart": depart}
    if via:
        spec["via"] = via
    if minutes:
        spec["minutes"] = minutes
    if layovers:
        spec["layovers"] = layovers
    return spec


def of(slot, flight, cents, refundable=False, seats=True, cabin="ECONOMY"):
    data = {"slot": slot, "flight": flight, "cabin": cabin, "fare_cents": cents}
    if not seats:
        data["seats"] = False
    if refundable:
        data["refundable"] = True
    return data


def contract_offers(prefix, flight, origin, destination, controlled_seats=True):
    _, controlled, ycal = CONTRACT_FARES[frozenset((origin, destination))]
    return [of(f"{prefix}-controlled", flight, controlled, refundable=True, seats=controlled_seats),
            of(f"{prefix}-ycal", flight, ycal, refundable=True)]


def search(origin, destination, date, flights, offers):
    return {"name": "out", "origin": origin, "destination": destination, "date": date, "return_date": "",
            "background": 0, "flights": flights, "offers": offers}


def expected(decision, slots, reasons, approvers, clauses, phrase="", cabins=("ECONOMY",)):
    return {"decision": decision, "offer_slots": sorted(slots), "cabins": sorted(cabins) if slots else ["NONE"],
            "reason_codes": sorted(reasons), "approvers": sorted(approvers), "clauses": sorted(clauses),
            "unclear_phrase": phrase}


IN_OK = ["APPOINTING_AUTHORITY", "NONE", "SUPERVISOR"]
OUT_OK = IN_OK + ["RESOURCE_AND_INNOVATION_DIVISION"]
BASE = ["COMMERCIAL_AIR_TRAVEL", "NON_REFUNDABLE_AIRFARE", "REFUNDABLE_AIRFARE"]
OUT_BASE = BASE + ["OUT_OF_STATE_APPROVAL"]
INTL_BASE = OUT_BASE + ["INTERNATIONAL_AIRFARE"]
JUST = ["REASON_CODE_JUSTIFICATIONS"]
CONTRACT_CODES = ["CAPACITY_CONTROLLED_FARE_AVAILABLE", "LOWEST_FARE", "REFUNDABLE_FARE_JUSTIFIED", "STATE_CONTRACT_FARE"]
GAP = ["APPOINTING_AUTHORITY", "NOT_NAMED", "SUPERVISOR"]
S = []


def scenario(id, category, overlays, request, trip_, searches, exp, must_keep, notes, twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=()):
    S.append({
        "id": id, "category": category, "overlays": overlays, "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request, "trip": trip_,
        "world": {"searches": searches}, "expected": exp, "must_keep": must_keep, "distractors": list(distractors),
        "design_notes": notes,
    })


# ============================== easy ==============================
scenario(
    "agate-cove", "easy", [],
    "Please book my flight from Los Angeles to Denver on December 10 for the Western States bridge preservation "
    "conference. The conference starts the next morning.",
    trip("LAX", "DEN", traveller_name="Marisol Ortega", traveller_title="Transportation Engineer (Civil)",
         travel_date="2026-12-10", purpose="Western States bridge preservation conference, Denver, from December 11",
         purpose_kind="CONFERENCE"),
    [search("LAX", "DEN", "2026-12-10",
            {"ua": fl("UA", "07:00"), "wn": fl("WN", "09:20")},
            [*contract_offers("ua", "ua", "LAX", "DEN"), of("ua-saver", "ua", 23900), of("wn-saver", "wn", 16400)])],
    expected("BOOK", ["wn-saver"], ["LOWEST_FARE", "NON_REFUNDABLE_BELOW_CONTRACT_FARE",
                                    "NON_CONTRACT_CARRIER_JUSTIFIED"], OUT_OK, OUT_BASE + JUST),
    [LOWEST, OUT_OF_STATE, NONREF, OOS_APPROVAL],
    "Out-of-state trip, approval on file. Southwest's non-refundable 16400 is less than United's contracted 21900 "
    "(186-187), and it is the lowest cost airfare (136-137); Southwest is not the contract carrier, so the "
    "non-contracted-carrier justification (218) applies too. United's own saver fare is above the contract rate.",
    distractors=[D_ONE_WAY])

scenario(
    "bodega-fern", "easy", ["upgrade_not_taken"],
    "I need to fly from San Francisco down to San Diego on December 9 for a 1 p.m. meeting at the "
    "District 11 office. Please book it.",
    trip("SFO", "SAN", traveller_name="Kenji Watanabe", traveller_title="Associate Transportation Planner",
         travel_date="2026-12-09", purpose="Corridor planning meeting at the District 11 office, 13:00"),
    [search("SFO", "SAN", "2026-12-09",
            {"as": fl("AS", "07:15"), "ua": fl("UA", "08:40")},
            [*contract_offers("as", "as", "SFO", "SAN"), of("as-saver", "as", 16900), of("ua-saver", "ua", 17900)])],
    expected("BOOK", ["as-controlled"], CONTRACT_CODES + ["NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE"], IN_OK, BASE + JUST),
    [LOWEST, CONTRACT, CONTROLLED, NONREF],
    "In-state. Both non-refundable fares (16900, 17900) are above the 15400 capacity-controlled contract fare, so "
    "lines 167-168 do not allow them, and the contract fare is the lowest cost airfare anyway. The YCAL fare is "
    "listed but not necessary (203-207).",
    distractors=[D_UPGRADE])

scenario(
    "cypress-lark", "easy", ["upgrade_not_taken"],
    "Please book me business class from San Francisco to London on January 12 for the international road safety "
    "conference; it's a long trip. If business isn't allowed, book what the policy allows; I have to be at the "
    "conference, which opens on the 14th.",
    trip("SFO", "LHR", traveller_name="Priya Raman", traveller_title="Senior Transportation Engineer",
         travel_date="2027-01-12", purpose="International road safety conference, London, January 14-16",
         purpose_kind="CONFERENCE", requested_cabin="BUSINESS"),
    [search("SFO", "LHR", "2027-01-12",
            {"ua": fl("UA", "13:30"), "ba": fl("BA", "16:40")},
            [*contract_offers("ua", "ua", "SFO", "LHR"), of("ua-business", "ua", 540000, cabin="BUSINESS"),
             of("ba-saver", "ba", 84000), of("ba-business", "ba", 498000, cabin="BUSINESS")])],
    expected("BOOK", ["ba-saver"], ["LOWEST_FARE", "UPGRADE_NOT_ELIGIBLE"], OUT_OK, INTL_BASE + JUST),
    [LOWEST, NONREF, OOS_APPROVAL],
    "The chapter has no cabin rule at all, and lines 136-137 require the lowest cost airfare: the BA economy fare, "
    "non-refundable and below United's contract fare (167-168). The business request is declined on the lowest-fare "
    "rule itself, so LOWEST_FARE stands beside UPGRADE_NOT_ELIGIBLE. Booked 50 days ahead (no 30-day code).",
    distractors=[D_PHONE])

scenario(
    "dune-sparrow", "easy", ["dearer_option", "multi_leg"],
    "I have to be at an Oakland hearing that starts at 9:30 a.m. on December 8. Please book my flight up from "
    "Los Angeles that morning.",
    trip("LAX", "SFO", traveller_name="Tomas Reyes", traveller_title="Right of Way Agent", travel_date="2026-12-08",
         purpose="Eminent domain hearing in Oakland, 09:30", purpose_kind="HEARING",
         must_arrive_by="2026-12-08 08:45",
         notes=["Getting from SFO to the hearing room takes about 45 minutes."]),
    [search("LAX", "SFO", "2026-12-08",
            {"wn": fl("WN", "06:00", via=["LAS"], layovers=[50]), "as": fl("AS", "06:30"), "ua": fl("UA", "07:15")},
            [of("wn-saver", "wn", 9900), *contract_offers("as", "as", "LAX", "SFO"), of("ua-saver", "ua", 15900)])],
    expected("BOOK", ["as-controlled"], CONTRACT_CODES + ["NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE"], IN_OK, BASE + JUST),
    [LOWEST, CONTRACT, CONTROLLED, NONREF],
    "Southwest via Las Vegas is cheapest but lands 09:05, after the 08:45 limit; United's non-refundable 15900 is "
    "above the 13900 contract fare (167-168). The capacity-controlled Alaska fare, landing 07:40, is the lowest cost "
    "airfare that works.",
    distractors=[D_PENALTY])

scenario(
    "elkhorn-reed", "easy", ["multi_leg", "date_arithmetic"],
    "Please get me from San Diego to San Francisco on December 15 for the asset management training that starts "
    "the next morning. Connecting is fine with me.",
    trip("SAN", "SFO", traveller_name="Aaliyah Brooks", traveller_title="Transportation Engineer (Electrical)",
         travel_date="2026-12-15", booking_date="2026-12-10",
         purpose="Asset management training, Oakland, from December 16", purpose_kind="TRAINING",
         connections_ok=True),
    [search("SAN", "SFO", "2026-12-15",
            {"wn": fl("WN", "07:10", via=["LAS"], layovers=[45]), "as": fl("AS", "08:00"), "ua": fl("UA", "10:00")},
            [of("wn-saver", "wn", 11900), *contract_offers("as", "as", "SAN", "SFO"), of("ua-saver", "ua", 18900)])],
    expected("BOOK", ["wn-saver"], ["ADVANCE_PURCHASE_TOO_LATE", "DOMESTIC_SHORT_NOTICE_JUSTIFIED", "LOWEST_FARE",
                                    "NON_CONTRACT_CARRIER_JUSTIFIED"], IN_OK, BASE + JUST),
    [LOWEST, IN_STATE, NONREF, ROUTING, REASONS],
    "In-state: lines 183-185 allow Southwest's non-refundable fare, which is also below the 15400 contract fare "
    "(167-168) and the lowest cost airfare. The traveller accepts the connection and the training is the next day. "
    "Booked December 10 for December 15: 5 days, less than 7 (220), and Concur asks for the justification before "
    "it books (224-226), so a justification this booking needs is accepted: short notice, or Southwest as a "
    "non-contracted carrier (218). Nothing asked for is declined, so LOWEST_FARE (136-137) is accepted too.",
    distractors=[D_ANYTIME])

scenario(
    "sage-inlet", "easy", ["multi_leg"],
    "Could you get me a refundable ticket from San Diego to San Francisco on December 17, just in case? The "
    "training starts the next morning and the dates are set. A connection is fine.",
    trip("SAN", "SFO", traveller_name="Lucas Ferreira", traveller_title="Transportation Surveyor",
         travel_date="2026-12-17", purpose="Survey methods training, Oakland, December 18-19", purpose_kind="TRAINING",
         requested_fare="REFUNDABLE", connections_ok=True),
    [search("SAN", "SFO", "2026-12-17",
            {"wn": fl("WN", "07:10", via=["LAS"], layovers=[45]), "as": fl("AS", "08:00")},
            [of("wn-saver", "wn", 11900), *contract_offers("as", "as", "SAN", "SFO")])],
    expected("BOOK", ["wn-saver"], ["REFUNDABLE_FARE_NOT_ALLOWED"], IN_OK, BASE + JUST),
    [LOWEST, CONSIDER, IN_STATE, REASONS],
    "The dates are fixed and a change is unlikely, so lines 161-162 put the non-refundable fare first, and lines "
    "136-137 require the lowest cost airfare; nothing on file justifies a refundable fare (219, 231-239). The "
    "request is declined because nothing justifies the refundable fare (a justified one is booked although dearer, "
    "tule-marsh), so only REFUNDABLE_FARE_NOT_ALLOWED is accepted (lesson 12): book Southwest (183-185).",
    distractors=[D_PENALTY])

# ============================== boundary twins ==============================
for name, twin, delta_fare in (("garnet-slough", "heron-quay", 16899), ("heron-quay", "garnet-slough", 16900)):
    granted = delta_fare < 16900
    scenario(
        name, "boundary_twin", [] if granted else ["dearer_option"],
        "I fly Delta for the miles; please put me on Delta from Los Angeles to Seattle on December 14. If Delta "
        "isn't allowed, book what the policy allows; I have to be at the conference, which starts the next morning.",
        trip("LAX", "SEA", traveller_name="Grace Kim", traveller_title="Environmental Planner",
             travel_date="2026-12-14", purpose="Western transportation environmental conference, Seattle, from "
             "December 15", purpose_kind="CONFERENCE", requested_airline="Delta Air Lines"),
        [search("LAX", "SEA", "2026-12-14",
                {"dl": fl("DL", "07:00"), "as": fl("AS", "08:15")},
                [of("dl-saver", "dl", delta_fare), *contract_offers("as", "as", "LAX", "SEA"),
                 of("as-saver", "as", 18400)])],
        expected("BOOK", ["dl-saver"], ["LOWEST_FARE", "LOYALTY_PROGRAM_PREFERENCE", "NON_CONTRACT_CARRIER_JUSTIFIED",
                                        "NON_REFUNDABLE_BELOW_CONTRACT_FARE"], OUT_OK, OUT_BASE + JUST)
        if granted else
        expected("BOOK", ["as-controlled"], ["NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE", "PREFERRED_CARRIER_REQUIRED",
                                             "STATE_CONTRACT_FARE"], OUT_OK, OUT_BASE + ["AIRFARE_REIMBURSEMENT_CLAIMS"]),
        [OUT_OF_STATE, NONREF, CONTRACT, OOS_APPROVAL] + ([] if granted else [ABOVE_CONTRACT]),
        ("Delta's non-refundable 16899 is less costly than the 16900 contracted fare (186-187, 'less costly than'): "
         "allowed, the lowest cost airfare, and the airline asked for.") if granted else
        ("Delta's non-refundable 16900 equals the 16900 contracted fare: not 'less costly than' it (186-187), so it "
         "is not allowed even though the price is the same; book the contract fare. The ground for declining Delta "
         "is the contract-rate rule, not the lowest-fare rule, so LOWEST_FARE is not accepted."),
        twin_of=twin, twin_fact="Delta's non-refundable fare 16899 or 16900 cents against the 16900 contract fare",
        distractors=[D_MILES])

for name, twin, japan_fare in (("indigo-mesa", "juniper-tide", 141999), ("juniper-tide", "indigo-mesa", 142000)):
    cheaper = japan_fare < 142000
    scenario(
        name, "boundary_twin", [] if cheaper else ["dearer_option"],
        "Please book my flight from San Francisco to Tokyo on January 14 for the seismic retrofit workshop, which "
        "begins on the 16th.",
        trip("SFO", "NRT", traveller_name="Daniel Okafor", traveller_title="Senior Bridge Engineer",
             travel_date="2027-01-14", purpose="Seismic retrofit workshop, Tokyo, January 16-18", purpose_kind="TRAINING"),
        [search("SFO", "NRT", "2027-01-14",
                {"jl": fl("JL", "11:00"), "ua": fl("UA", "12:30")},
                [of("jl-saver", "jl", japan_fare), *contract_offers("ua", "ua", "SFO", "NRT"),
                 of("ua-saver", "ua", 149000)])],
        expected("BOOK", ["jl-saver"], ["LOWEST_FARE", "NON_CONTRACT_CARRIER_JUSTIFIED",
                                        "NON_REFUNDABLE_BELOW_CONTRACT_FARE"], OUT_OK, INTL_BASE + JUST)
        if cheaper else
        expected("BOOK", ["ua-controlled"], CONTRACT_CODES + ["NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE"], OUT_OK,
                 INTL_BASE + JUST),
        [NONREF, LOWEST, CONTRACT, OOS_APPROVAL],
        ("JAL's non-refundable 141999 is less than United's 142000 contracted refundable rate (167-168): allowed, "
         "and the lowest cost airfare.") if cheaper else
        ("JAL's non-refundable 142000 is not less than the 142000 contracted refundable rate (167-168), so it may not "
         "be bought; the contract fare costs the same and is the lowest allowed fare."),
        twin_of=twin, twin_fact="JAL's non-refundable fare 141999 or 142000 cents against the 142000 contract fare",
        distractors=[D_PHONE])

for name, twin, booked_on in (("kelp-ridge", "laurel-wash", "2026-11-25"), ("laurel-wash", "kelp-ridge", "2026-11-24")):
    short = booked_on == "2026-11-25"
    scenario(
        name, "boundary_twin", ["date_arithmetic", "month_end", "dearer_option"],
        "I've been called to testify at an Arizona Department of Transportation hearing in Phoenix at 1 p.m. on "
        "December 1. Please book my flight from Los Angeles that morning.",
        trip("LAX", "PHX", traveller_name="Hannah Lee", traveller_title="Supervising Transportation Engineer",
             travel_date="2026-12-01", booking_date=booked_on, purpose="Testimony at a hearing in Phoenix, 13:00",
             purpose_kind="HEARING", must_arrive_by="2026-12-01 12:30",
             sign_offs=[trip_ok(date="2026-11-24"), oos_ok(date="2026-11-24")]),
        [search("LAX", "PHX", "2026-12-01",
                {"aa": fl("AA", "07:00"), "wn": fl("WN", "11:30")},
                [of("aa-saver", "aa", 15900), *contract_offers("aa", "aa", "LAX", "PHX"), of("wn-saver", "wn", 12900)])],
        expected("BOOK", ["aa-saver"], ["ADVANCE_PURCHASE_TOO_LATE", "DOMESTIC_SHORT_NOTICE_JUSTIFIED", "LOWEST_FARE"]
                 if short
                 else ["LOWEST_FARE", "NON_REFUNDABLE_BELOW_CONTRACT_FARE"], OUT_OK,
                 OUT_BASE + (JUST if short else [])),
        [LOWEST, OUT_OF_STATE, OOS_APPROVAL] + ([REASONS] if short else []),
        ("Booked November 25 for December 1: 6 calendar days, less than 7 (220), and Concur asks for the "
         "justification before it books (224-226): the short-notice justification is accepted beside LOWEST_FARE, "
         "since nothing asked for is declined. ")
        if short else
        ("Booked November 24 for December 1: 7 calendar days, not less than 7 (220): no short-notice justification. ")
        + "Southwest lands 13:40 local, after the 12:30 limit; American's non-refundable 15900 is below its 19800 "
        "contract fare (186-187) and is the lowest cost airfare that works.",
        twin_of=twin, twin_fact="booked November 25 or November 24 for a December 1 flight (6 or 7 days ahead)",
        distractors=[D_TIP])

for name, twin, booked_on in (("manzanita-pool", "nopal-crest", "2026-11-24"),
                              ("nopal-crest", "manzanita-pool", "2026-11-23")):
    short = booked_on == "2026-11-24"
    scenario(
        name, "boundary_twin", ["date_arithmetic", "month_end", "dearer_option"],
        "Please book my flight from San Francisco to Vancouver on December 23 for the cross-border freight corridor "
        "meeting at 4 p.m. that day.",
        trip("SFO", "YVR", traveller_name="Owen Fitzgerald", traveller_title="Transportation Planner",
             travel_date="2026-12-23", booking_date=booked_on, purpose="Cross-border freight corridor meeting, "
             "Vancouver, 16:00", must_arrive_by="2026-12-23 15:30",
             sign_offs=[trip_ok(date="2026-11-20"), oos_ok(date="2026-11-20")]),
        [search("SFO", "YVR", "2026-12-23",
                {"ac": fl("AC", "08:00"), "ua": fl("UA", "09:00"), "ws": fl("WS", "14:00")},
                [of("ac-saver", "ac", 31900), of("ua-saver", "ua", 29900), *contract_offers("ua", "ua", "SFO", "YVR"),
                 of("ws-saver", "ws", 24900)])],
        expected("BOOK", ["ua-saver"], ["ADVANCE_PURCHASE_TOO_LATE", "INTERNATIONAL_SHORT_NOTICE_JUSTIFIED",
                                        "LOWEST_FARE"] if short
                 else ["LOWEST_FARE", "NON_REFUNDABLE_BELOW_CONTRACT_FARE"], OUT_OK,
                 INTL_BASE + (JUST if short else [])),
        [LOWEST, NONREF, OOS_APPROVAL] + ([REASONS] if short else []),
        ("Booked November 24 for December 23: 29 calendar days, less than 30 (221), and Concur asks for the "
         "justification before it books (224-226): the short-notice justification is accepted beside LOWEST_FARE, "
         "since nothing asked for is declined. ")
        if short else
        ("Booked November 23 for December 23: 30 calendar days, not less than 30 (221): no short-notice "
         "justification. ")
        + "WestJet lands 16:00, after the 15:30 limit; United's own non-refundable 29900 is below its 38900 "
        "contract fare (167-168) and is the lowest cost airfare that works (Air Canada's 31900 is dearer). United is "
        "the contract carrier, so no non-contracted-carrier justification (218) is involved.",
        twin_of=twin, twin_fact="booked November 24 or November 23 for a December 23 flight (29 or 30 days ahead)",
        distractors=[D_PHONE])

# ============================== multi-rule ==============================
for name, twin, seats in (("fennel-bluff", "poppy-ledge", False), ("poppy-ledge", "fennel-bluff", True)):
    scenario(
        name, "multi_rule", [] if not seats else ["upgrade_not_taken"],
        "Please book me the YCAL fare from San Francisco to Seattle on December 11; I like the unrestricted ticket. "
        "If that isn't allowed, book what the policy allows; the meeting is the next morning.",
        trip("SFO", "SEA", traveller_name="Rosa Delgado", traveller_title="Maintenance Area Superintendent",
             travel_date="2026-12-11", purpose="Pacific states maintenance peer exchange, Seattle, December 12",
             requested_fare="YCAL"),
        [search("SFO", "SEA", "2026-12-11",
                {"am": fl("AS", "07:30"), "dl": fl("DL", "09:00"), "pm": fl("AS", "12:00")},
                [*contract_offers("as", "am", "SFO", "SEA", controlled_seats=seats), of("dl-saver", "dl", 36900),
                 of("as-saver", "pm", 35900)])],
        expected("BOOK", ["as-ycal"], ["CAPACITY_CONTROLLED_SOLD_OUT", "LOWEST_FARE",
                                       "NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE", "REFUNDABLE_FARE_JUSTIFIED",
                                       "STATE_CONTRACT_FARE"], OUT_OK, OUT_BASE + JUST)
        if not seats else
        expected("BOOK", ["as-controlled"], ["CAPACITY_CONTROLLED_FARE_AVAILABLE", "UPGRADE_NOT_ELIGIBLE"], OUT_OK,
                 ["COMMERCIAL_AIR_TRAVEL", "REFUNDABLE_AIRFARE"]),
        [CONTROLLED, CONTRACT, OUT_OF_STATE, OOS_APPROVAL],
        ("The capacity-controlled seats are sold out, so the YCAL contract fare (203-207) is what is left, as asked; "
         "both non-refundable fares are above it (186-187), so it is also the lowest allowed fare.") if not seats else
        ("Capacity-controlled seats are available at 16900, and lines 204-207 say they should be used before YCAL; "
         "nothing makes the YCAL upgrade necessary. The request is declined on that contract-fare rule, so "
         "LOWEST_FARE is not accepted."),
        twin_of=twin, twin_fact="capacity-controlled seats sold out or available",
        distractors=[D_UPGRADE])

scenario(
    "oriole-bend", "multi_rule", ["dearer_option"],
    "Please book me from San Francisco to Denver on December 3; the pavement research panel starts at 2 p.m. "
    "Denver time and I have to be there for it.",
    trip("SFO", "DEN", traveller_name="Elena Petrova", traveller_title="Research Program Specialist",
         travel_date="2026-12-03", purpose="Pavement research panel, Denver, 14:00", must_arrive_by="2026-12-03 13:30"),
    [search("SFO", "DEN", "2026-12-03",
            {"ua": fl("UA", "07:30"), "wn": fl("WN", "10:30")},
            [*contract_offers("ua", "ua", "SFO", "DEN"), of("ua-saver", "ua", 23900), of("wn-saver", "wn", 15900)])],
    expected("BOOK", ["ua-controlled"], CONTRACT_CODES + ["NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE"], OUT_OK,
             OUT_BASE + JUST),
    [LOWEST, OUT_OF_STATE, CONTRACT, CONTROLLED, OOS_APPROVAL],
    "Southwest lands 13:50, after the 13:30 limit. United's non-refundable 23900 is above its own 22900 "
    "capacity-controlled contract fare, so 186-187 do not allow it; the contract fare is the lowest cost airfare that "
    "lands in time.",
    distractors=[D_ONE_WAY])

scenario(
    "quail-hollow", "multi_rule", ["multi_leg"],
    "Please book my flight from Los Angeles to Seattle on December 9. The design review is the next morning.",
    trip("LAX", "SEA", traveller_name="Samuel Adeyemi", traveller_title="Transportation Engineer (Civil)",
         travel_date="2026-12-09", purpose="Ferry terminal design review, Seattle, December 10",
         notes=[NO_CONNECTION_VIEW]),
    [search("LAX", "SEA", "2026-12-09",
            {"via": fl("AS", "08:00", via=["SFO"], minutes=[75, 110], layovers=[30]),
             "direct": fl("AS", "09:00", minutes=[170])},
            [of("as-connect", "via", 12900), *contract_offers("as", "direct", "LAX", "SEA")])],
    expected("BOOK", ["as-connect"], ["ALTERNATE_ROUTE_WITHIN_MARGIN", "COST_SAVINGS", "LOWEST_FARE",
                                      "NON_REFUNDABLE_BELOW_CONTRACT_FARE"], OUT_OK, OUT_BASE),
    [LOWEST, ROUTING, OUT_OF_STATE, OOS_APPROVAL],
    "The connection through San Francisco is non-refundable at 12900, below the 16900 contract fare (186-187). Its "
    "elapsed time is 215 minutes against the nonstop's 170 (45 more), landing well before the next-morning review: "
    "the layover does not significantly delay the trip (174-175), so the lowest cost airfare is the connection.",
    distractors=[D_MODE])

scenario(
    "redwood-spur", "multi_rule", ["multi_leg", "dearer_option"],
    "Please book my flight from Los Angeles to Seattle on December 16. The design review starts at 1 p.m. that day.",
    trip("LAX", "SEA", traveller_name="Samuel Adeyemi", traveller_title="Transportation Engineer (Civil)",
         travel_date="2026-12-16", purpose="Ferry terminal design review, Seattle, 13:00",
         must_arrive_by="2026-12-16 12:30"),
    [search("LAX", "SEA", "2026-12-16",
            {"via": fl("AS", "06:00", via=["SFO"], minutes=[75, 110], layovers=[230]),
             "direct": fl("AS", "09:00", minutes=[170])},
            [of("as-connect", "via", 12900), *contract_offers("as", "direct", "LAX", "SEA")])],
    expected("BOOK", ["as-controlled"], CONTRACT_CODES, OUT_OK, OUT_BASE + JUST),
    [LOWEST, ROUTING, CONTRACT, OOS_APPROVAL],
    "The cheaper connection lands 12:55, after the 12:30 limit: its layover impacts the business (174-175). The "
    "nonstop's capacity-controlled contract fare, landing 11:50, is the lowest cost airfare that works.",
    distractors=[D_MODE])

# ============================== hidden clause ==============================
scenario(
    "tule-marsh", "hidden_clause", ["dearer_option", "multi_leg", "date_arithmetic"],
    "Storm damage closed a bridge on Route 1 and I've just been assigned to inspect it in the Bay Area tomorrow. "
    "The schedule could shift hour to hour, so please book me a refundable ticket from San Diego to San Francisco "
    "for tomorrow, November 24.",
    trip("SAN", "SFO", traveller_name="Miguel Santos", traveller_title="Bridge Maintenance Engineer",
         travel_date="2026-11-24", purpose="Emergency inspection of a storm-damaged bridge, Bay Area",
         purpose_kind="SITE_INSPECTION", requested_fare="REFUNDABLE", connections_ok=True, plans_fixed=False,
         assignment_email_on_file=True, sign_offs=[trip_ok(date="2026-11-23")],
         notes=[("Email of 2026-11-23 16:10 from the Structures Maintenance manager: inspect the bridge on November 24; "
                "the inspection is mission critical and its time may move as crews clear the site.")]),
    [search("SAN", "SFO", "2026-11-24",
            {"wn": fl("WN", "07:10", via=["LAS"], layovers=[45]), "as": fl("AS", "09:00")},
            [of("wn-saver", "wn", 11900), *contract_offers("as", "as", "SAN", "SFO")])],
    expected("BOOK", ["as-controlled", "wn-saver"], ["ADVANCE_PURCHASE_TOO_LATE", "DOMESTIC_SHORT_NOTICE_JUSTIFIED",
                                                     "LOWEST_FARE", "REFUNDABLE_FARE_JUSTIFIED",
                                                     "SOUTHWEST_IN_STATE_FARE", "STATE_CONTRACT_FARE"], IN_OK,
             ["COMMERCIAL_AIR_TRAVEL", "NON_REFUNDABLE_AIRFARE", "REASON_CODE_JUSTIFICATIONS", "REFUNDABLE_AIRFARE"]),
    [EXAMPLE_ONE, REASONS, CONSIDER, CONTRACT, LOWEST, IN_STATE],
    "Example 1 of the reason-code section (231-234) names a refundable fare chosen for a short-notice assignment, "
    "documented by an email, as a justification; lines 161-162 put non-refundable fares first only when the dates "
    "are fixed. The traveller asks for refundable: the lowest refundable fare is the capacity-controlled contract "
    "fare. Booked a day ahead, so the short-notice code (220) applies too. Booking Southwest instead is defensible "
    "as well (audit): lines 136-137 ask for the lowest cost airfare whenever possible and lines 183-185 call "
    "Southwest the most flexible carrier for changes, while the chapter never requires a refundable fare; that "
    "booking declines the request on the lowest-fare ground (LOWEST_FARE, SOUTHWEST_IN_STATE_FARE).",
    distractors=[D_PENALTY])

scenario(
    "umber-canyon", "hidden_clause", ["outside_air_section"],
    "I telework from San Diego. Please book my flight to Phoenix on December 10 for the Southwest transportation "
    "safety conference, which starts the next morning.",
    trip("SAN", "PHX", traveller_name="Nadia Haddad", traveller_title="Traffic Safety Engineer",
         headquarters=DISTRICT_4, residence="San Diego, CA", on_telework=True, travel_date="2026-12-10",
         purpose="Southwest transportation safety conference, Phoenix, from December 11", purpose_kind="CONFERENCE"),
    [search("SAN", "PHX", "2026-12-10",
            {"wn": fl("WN", "08:00"), "aa": fl("AA", "09:00")},
            [of("wn-saver", "wn", 10900), *contract_offers("aa", "aa", "SAN", "PHX")])],
    expected("BOOK", ["wn-saver"], ["LOWEST_FARE", "NON_CONTRACT_CARRIER_JUSTIFIED",
                                    "NON_REFUNDABLE_BELOW_CONTRACT_FARE"], OUT_OK, OUT_BASE + JUST),
    [TELEWORK, TELEWORK_AIR, LOWEST, OUT_OF_STATE, OOS_APPROVAL],
    "The telework notes (61-65, 154-159) bar only travel between residence and headquarters; a conference in "
    "Phoenix is state business from wherever the trip starts. Southwest's 10900 is below American's 17900 contract "
    "fare (186-187) and the lowest cost airfare.",
    twin_of="coyote-dell", twin_fact="where the teleworker flies: a Phoenix conference or the Oakland headquarters office",
    distractors=[D_MODE])

scenario(
    "vireo-point", "hidden_clause", ["multi_traveller"],
    "I can't put the armrest down on a standard seat, so I need the seat next to mine as well. My supervisor has "
    "approved both reservations. Please book me from Los Angeles to San Francisco on December 11; the meeting is "
    "the next morning.",
    trip("LAX", "SFO", traveller_name="Robert Castillo", traveller_title="Construction Inspector",
         travel_date="2026-12-11", purpose="Construction claims meeting, Oakland, December 12", extra_seat_needed=True,
         sign_offs=[trip_ok(), sign("SUPERVISOR", "Dana Whitfield", "FIRST_SEAT_RESERVATION"),
                    sign("SUPERVISOR", "Dana Whitfield", "EXTRA_SEAT_RESERVATION")]),
    [search("LAX", "SFO", "2026-12-11",
            {"as": fl("AS", "10:00"), "ua": fl("UA", "12:00")},
            [*contract_offers("as", "as", "LAX", "SFO"), of("ua-saver", "ua", 15900)])],
    expected("BOOK", ["as-controlled"], CONTRACT_CODES + ["EXTRA_SEAT_APPROVED", "NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE"],
             IN_OK, ["PASSENGERS_OF_SIZE"] + BASE + JUST),
    [SIZE, EXTRA_SEAT, LOWEST, CONTRACT],
    "Passengers of size (241-247): an employee who cannot lower the armrests books an additional seat, with two "
    "reservations the supervisor approves; both approvals are on file. The fare for both seats is the lowest cost "
    "airfare, the capacity-controlled contract fare (United's 15900 is above it, 167-168).",
    distractors=[D_PENALTY])

# ============================== distractor ==============================
scenario(
    "willow-flat", "distractor", ["dearer_option"],
    "I'm booking this one later than I'd like. Please get me from Los Angeles to Denver on December 4; the "
    "district coordination meeting starts at 10 a.m. Denver time.",
    trip("LAX", "DEN", traveller_name="Isabel Navarro", traveller_title="Office Chief, Traffic Operations",
         travel_date="2026-12-04", purpose="Multi-state traffic operations coordination meeting, Denver, 10:00",
         must_arrive_by="2026-12-04 09:30"),
    [search("LAX", "DEN", "2026-12-04",
            {"ua": fl("UA", "06:00"), "wn": fl("WN", "07:30")},
            [of("ua-saver", "ua", 17900), *contract_offers("ua", "ua", "LAX", "DEN"), of("wn-saver", "wn", 14900)])],
    expected("BOOK", ["ua-saver"], ["LOWEST_FARE", "NON_REFUNDABLE_BELOW_CONTRACT_FARE"], OUT_OK, OUT_BASE),
    [LOWEST, OUT_OF_STATE, OOS_APPROVAL],
    "Booked 11 days ahead. The 14-day line (170-171) is a cost-saving tip, not a rule, and the domestic reason code "
    "is for less than 7 days (220). Southwest lands 10:40, after the 09:30 limit; United's non-refundable 17900 is "
    "below its 21900 contract fare (186-187) and the lowest cost airfare that works.",
    distractors=[D_TIP])

scenario(
    "yucca-strand", "distractor", [],
    "Please book me from Los Angeles to Las Vegas on December 7 for the transportation technology expo, which "
    "opens the next morning. I'll check two bags of exhibit materials. There's also a Southwest credit on file "
    "from a colleague's cancelled trip, if that helps.",
    trip("LAX", "LAS", traveller_name="Wei Zhang", traveller_title="Information Technology Specialist",
         travel_date="2026-12-07", purpose="Transportation technology expo, Las Vegas, from December 8 (exhibit booth)",
         purpose_kind="CONFERENCE",
         ticket_credits=[{"airline": "Southwest Airlines", "amount_cents": 6000, "holder_name": "Jordan Price",
                          "usable_through": "2027-03-31"}],
         notes=["The traveller will check two bags of exhibit materials."]),
    [search("LAX", "LAS", "2026-12-07",
            {"wn": fl("WN", "08:00"), "dl": fl("DL", "09:00")},
            [of("wn-saver", "wn", 8900), *contract_offers("dl", "dl", "LAX", "LAS"), of("dl-saver", "dl", 11900)])],
    expected("BOOK", ["wn-saver"], ["LOWEST_FARE", "NON_CONTRACT_CARRIER_JUSTIFIED",
                                    "NON_REFUNDABLE_BELOW_CONTRACT_FARE", "UNUSED_TICKET_CREDIT_APPLIED"], OUT_OK,
             OUT_BASE + JUST),
    [LOWEST, OUT_OF_STATE, CREDITS, OOS_APPROVAL],
    "The bag rule (262-271) pays one bag and asks a justification for more on the claim; it does not change the "
    "ticket. Southwest's 8900 is below Delta's 12900 contract fare (186-187) and the lowest cost airfare; the "
    "colleague's Southwest credit can be used by any employee (144-148).",
    distractors=[D_BAGS, D_EXTRA_BAGS])

scenario(
    "alder-rook", "distractor", ["outside_air_section"],
    "I found a San Francisco to San Diego fare on Expedia for $159 on December 8. Should I just buy it there and "
    "claim it, or can you book me? I need to be at a 1 p.m. meeting in San Diego that day.",
    trip("SFO", "SAN", traveller_name="Fatima Noor", traveller_title="Associate Governmental Program Analyst",
         travel_date="2026-12-08", purpose="Grant program meeting at the District 11 office, 13:00",
         notes=["The traveller found a fare of $159 on Expedia for the same day."]),
    [search("SFO", "SAN", "2026-12-08",
            {"as": fl("AS", "07:15"), "ua": fl("UA", "09:30")},
            [*contract_offers("as", "as", "SFO", "SAN"), of("ua-saver", "ua", 17400)])],
    expected("BOOK", ["as-controlled"], CONTRACT_CODES + ["NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE"], IN_OK, BASE + JUST),
    [CONCUR, LOWEST, CONTRACT, CONTROLLED],
    "Airfare is bought through Concur or CI Azumano (138-140); the outside fare ($159) is not an offer the "
    "department can buy, and the third-party clauses (67-72, 288) concern claims after the fact. The "
    "capacity-controlled contract fare (15400) is the lowest cost airfare, below the outside fare too.",
    distractors=[D_VENDORS, D_EXPEDIA])

# ============================== refusal ==============================
scenario(
    "basalt-cliff", "refusal", ["personal_travel"],
    "Can you book me Los Angeles to Las Vegas on December 26 for a family holiday? I'd like the state rate if I "
    "can get it.",
    trip("LAX", "LAS", traveller_name="Carlos Mendoza", traveller_title="Equipment Operator II",
         travel_date="2026-12-26", purpose="Family holiday in Las Vegas", purpose_kind="PERSONAL", sign_offs=[]),
    [search("LAX", "LAS", "2026-12-26",
            {"wn": fl("WN", "09:00"), "dl": fl("DL", "10:00")},
            [of("wn-saver", "wn", 8900), *contract_offers("dl", "dl", "LAX", "LAS")])],
    expected("REFUSE", [], ["CONTRACT_FARE_NOT_FOR_PERSONAL_TRAVEL", "PERSONAL_TRAVEL_NOT_COVERED"], ["NONE"],
             ["COMMERCIAL_AIR_TRAVEL", "REFUNDABLE_AIRFARE"]),
    [PERSONAL_SYSTEM, CONTRACT_PERSONAL],
    "Lines 141-142: using the reservation system for personal travel is prohibited; lines 211-212: the contracted "
    "rates are not extended to employees for personal travel. Buy nothing.",
    distractors=[D_MILES])

scenario(
    "coyote-dell", "refusal", ["outside_air_section"],
    "I telework from San Diego. Please book my flight to San Francisco on December 10 for my in-office days at the "
    "District 4 office in Oakland.",
    trip("SAN", "SFO", traveller_name="Nadia Haddad", traveller_title="Traffic Safety Engineer",
         headquarters=DISTRICT_4, residence="San Diego, CA", on_telework=True, travel_date="2026-12-10",
         purpose="In-office days at the District 4 office, Oakland (the traveller's headquarters)",
         purpose_kind="HEADQUARTERS_OFFICE_DAY"),
    [search("SAN", "SFO", "2026-12-10",
            {"wn": fl("WN", "07:10", via=["LAS"], layovers=[45]), "as": fl("AS", "08:00")},
            [of("wn-saver", "wn", 11900), *contract_offers("as", "as", "SAN", "SFO")])],
    expected("REFUSE", [], ["COMMUTING_NOT_REIMBURSABLE", "PERSONAL_TRAVEL_NOT_COVERED"], IN_OK,
             ["COMMERCIAL_AIR_TRAVEL", "TRANSPORTATION_GENERAL"]),
    [TELEWORK_AIR, TELEWORK, COMMUTE],
    "Lines 154-159 and 61-65: flights between residence and headquarters are not reimbursable for an employee on "
    "telework status, and telework does not move the headquarters (Oakland); lines 48-49 bar home-headquarters "
    "travel. The supervisor's approval on file goes unused (SYNC_NOTES 4(b)): NONE or the supervisor.",
    twin_of="umber-canyon", twin_fact="where the teleworker flies: the Oakland headquarters office or a Phoenix "
    "conference")

scenario(
    "dove-terrace", "refusal", ["personal_travel", "multi_traveller"],
    "My husband is coming with me to the Denver conference on December 10. Please book him on my flight from Los "
    "Angeles at the state contract rate; we'll pay for his seat.",
    trip("LAX", "DEN", traveller_name="Michael Ortega", traveller_title="Husband of Marisol Ortega",
         passenger="SPOUSE_OR_FAMILY", accompanies="Marisol Ortega, Transportation Engineer (Civil)",
         travel_date="2026-12-10", purpose="Accompanying his wife to a conference in Denver", purpose_kind="PERSONAL",
         sign_offs=[], notes=["Marisol Ortega's own ticket is booked separately."]),
    [search("LAX", "DEN", "2026-12-10",
            {"ua": fl("UA", "07:00"), "wn": fl("WN", "09:20")},
            [*contract_offers("ua", "ua", "LAX", "DEN"), of("wn-saver", "wn", 16400)])],
    expected("REFUSE", [], ["COMPANION_NOT_COVERED", "CONTRACT_FARE_NOT_FOR_PERSONAL_TRAVEL",
                            "PERSONAL_TRAVEL_NOT_COVERED"], ["NONE"], ["COMMERCIAL_AIR_TRAVEL", "REFUNDABLE_AIRFARE"]),
    [PERSONAL_SYSTEM, CONTRACT_PERSONAL],
    "Lines 141-142: the system is for Caltrans employees on state business and personal travel through it is "
    "prohibited; lines 211-212: contracted rates are only for state business. A spouse's ticket is personal: buy "
    "nothing, whoever pays.",
    distractors=[D_MILES])

# ============================== flag ==============================
scenario(
    "egret-shoal", "flag", ["unclear_phrase"],
    "Please book my flight from Los Angeles to San Francisco on December 10. The meeting is the next morning.",
    trip("LAX", "SFO", traveller_name="Jasmine Patel", traveller_title="Transportation Engineer (Civil)",
         travel_date="2026-12-10", purpose="Toll bridge program meeting, Oakland, December 11"),
    [search("LAX", "SFO", "2026-12-10",
            {"ua": fl("UA", "07:30"), "as": fl("AS", "08:00")},
            [of("ua-saver", "ua", 11900), *contract_offers("as", "as", "LAX", "SFO")])],
    expected("FLAG_FOR_APPROVAL", ["as-controlled", "ua-saver"], ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"], GAP,
             ["COMMERCIAL_AIR_TRAVEL", "NON_REFUNDABLE_AIRFARE"], phrase="Travelers may purchase non-refundable airfare for Southwest Airlines"),
    [IN_STATE, OUT_OF_STATE, NONREF, LOWEST],
    "United's in-state non-refundable 11900 is below the 13900 contract fare. Lines 167-168 allow any non-refundable "
    "fare below the contract rate, but the in-state sentence (183-185) names only Southwest, against 'any carrier' "
    "out of state (186-187).",
    flag_twins=["bodega-fern", "garnet-slough"],
    ambiguity={"phrase": "Travelers may purchase non-refundable airfare for Southwest Airlines",
               "readings": [("In-state, only Southwest's non-refundable fares may be bought: book the Alaska contract "
                            "fare."),
                            ("The in-state sentence permits Southwest without limiting lines 167-168: United's "
                            "non-refundable fare is below the contract rate and the lowest cost airfare: book it.")]})

scenario(
    "finch-arroyo", "flag", ["approval_required"],
    "Please book my flight from Los Angeles to Denver on December 15 for the bridge inspection standards "
    "conference. It starts the next morning.",
    trip("LAX", "DEN", traveller_name="Victor Alvarez", traveller_title="Bridge Inspector",
         travel_date="2026-12-15", purpose="Bridge inspection standards conference, Denver, from December 16",
         purpose_kind="CONFERENCE", sign_offs=[trip_ok(), oos_ok(status="PENDING", date="2026-11-19")],
         notes=[("Out-of-state travel request sent through the program's out-of-state travel coordinator on "
                "2026-11-19; no decision yet.")]),
    [search("LAX", "DEN", "2026-12-15",
            {"ua": fl("UA", "07:00"), "wn": fl("WN", "09:20")},
            [*contract_offers("ua", "ua", "LAX", "DEN"), of("ua-saver", "ua", 23900), of("wn-saver", "wn", 16400)])],
    expected("FLAG_FOR_APPROVAL", ["wn-saver"], ["APPROVAL_REQUIRED"],
             ["NOT_NAMED", "PROGRAM_TRAVEL_COORDINATOR", "RESOURCE_AND_INNOVATION_DIVISION"],
             ["OUT_OF_STATE_APPROVAL"]),
    [OOS_APPROVAL, LOWEST, OUT_OF_STATE],
    "Lines 248-252: out-of-state travel goes through an approval process administered by the Division of Resource "
    "and Innovation; the request is still pending. Hold the fare the rules give (Southwest, below the contract fare).",
    flag_twins=["agate-cove", "bodega-fern"],
    ambiguity="none: the out-of-state approval is pending, not unclear")

scenario(
    "granite-wren", "flag", ["approval_required", "multi_traveller"],
    "I can't put the armrest down on a standard seat, so I need the seat next to mine as well. My supervisor has "
    "approved my own reservation and is looking at the second one. Please book me from Los Angeles to San "
    "Francisco on December 14; the meeting is the next morning.",
    trip("LAX", "SFO", traveller_name="Linda Harper", traveller_title="Landscape Architect",
         travel_date="2026-12-14", purpose="Highway landscaping review, Oakland, December 15", extra_seat_needed=True,
         sign_offs=[trip_ok(), sign("SUPERVISOR", "Dana Whitfield", "FIRST_SEAT_RESERVATION"),
                    sign("SUPERVISOR", "Dana Whitfield", "EXTRA_SEAT_RESERVATION", status="PENDING", date="2026-11-21")]),
    [search("LAX", "SFO", "2026-12-14",
            {"as": fl("AS", "10:00"), "ua": fl("UA", "12:00")},
            [*contract_offers("as", "as", "LAX", "SFO"), of("ua-saver", "ua", 15900)])],
    expected("FLAG_FOR_APPROVAL", ["as-controlled"], ["APPROVAL_REQUIRED"], ["APPOINTING_AUTHORITY", "SUPERVISOR"],
             ["PASSENGERS_OF_SIZE"]),
    [EXTRA_SEAT, SIZE, LOWEST],
    "Lines 246-247: two reservations, and the supervisor will need to approve both; the second is pending. Hold the "
    "lowest cost fare (the capacity-controlled contract fare) for the supervisor.",
    flag_twins=["vireo-point", "dune-sparrow"],
    ambiguity="none: the second reservation's approval is pending, not unclear")

scenario(
    "hazel-kiln", "flag", ["unclear_phrase", "multi_leg"],
    "Please book my flight from Los Angeles to Seattle on December 9. The ferry systems workshop is the next "
    "morning.",
    trip("LAX", "SEA", traveller_name="Teresa Morales", traveller_title="Senior Transportation Planner",
         travel_date="2026-12-09", purpose="Ferry systems workshop, Seattle, December 10", purpose_kind="TRAINING",
         notes=[NO_CONNECTION_VIEW]),
    [search("LAX", "SEA", "2026-12-09",
            {"via": fl("AS", "08:00", via=["SFO"], minutes=[75, 110], layovers=[145]),
             "direct": fl("AS", "09:00", minutes=[170])},
            [of("as-connect", "via", 12900), *contract_offers("as", "direct", "LAX", "SEA")])],
    expected("FLAG_FOR_APPROVAL", ["as-connect", "as-controlled"], ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"], GAP,
             ["COMMERCIAL_AIR_TRAVEL", "NON_REFUNDABLE_AIRFARE"],
             phrase="as long as the layovers do not significantly impact business or delay travel times"),
    [ROUTING, LOWEST, OUT_OF_STATE, OOS_APPROVAL],
    "The connection costs 12900 (below the 16900 contract fare) and lands the evening before the workshop, but takes "
    "330 minutes against the nonstop's 170: whether 160 more minutes 'significantly ... delay travel times' "
    "(174-175) is not said.",
    flag_twins=["quail-hollow", "redwood-spur"],
    ambiguity={"phrase": "as long as the layovers do not significantly impact business or delay travel times",
               "readings": [("160 added minutes are not a significant delay when the business is the next morning: "
                            "book the lowest cost airfare, the connection."),
                            "Nearly doubling the travel time is a significant delay: book the nonstop contract fare."]})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for data in S:
        (OUT / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(S)} scenarios")


if __name__ == "__main__":
    main()
