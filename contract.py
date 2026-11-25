"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only.

The first part is the original-handbook template's shared contract and is the same in every plugin made from
it. The HANDBOOK-SPECIFIC part in the middle is filled per handbook: the scenario ids, the closed lists of
approvers and sections, and the trip record; the shared inputs and outputs after it refer to those names.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output

# ---------------------------------------------------------------------------------------------------------
# SHARED (template): keep identical across plugins, except the agent task's id in Task.BOOK_FLIGHT.
# ---------------------------------------------------------------------------------------------------------


class Tool(Enum):
    BOOKING_REQUIREMENTS = "booking_requirements"
    GET_TRIP = "get_trip"
    SEARCH_FLIGHTS = "search_flights"
    SOLVE_BOOKING = "solve_booking"


class Task(Enum):
    BOOKING_REQUIREMENTS = "booking-requirements"
    SEARCH_FLIGHTS = "search-flights"
    BOOK_FLIGHT = "book-caltrans-flight"


class Decision(Enum):
    BOOK = "BOOK"
    REFUSE = "REFUSE"
    FLAG_FOR_APPROVAL = "FLAG_FOR_APPROVAL"


class Cabin(Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"
    NONE = "NONE"


class ReasonCode(Enum):
    """Why the decision was made. The list is shared by every handbook plugin, so it also holds reasons
    that a given handbook never uses."""

    LOWEST_FARE = "LOWEST_FARE"
    UPGRADE_NOT_ELIGIBLE = "UPGRADE_NOT_ELIGIBLE"
    CLIENT_REIMBURSABLE = "CLIENT_REIMBURSABLE"
    UPGRADE_WITHIN_FARE_MARGIN = "UPGRADE_WITHIN_FARE_MARGIN"
    MEDICAL_NEED = "MEDICAL_NEED"
    COST_SAVINGS = "COST_SAVINGS"
    NO_ECONOMY_SEATS_URGENT = "NO_ECONOMY_SEATS_URGENT"
    TRAVELER_PAYS_UPGRADE = "TRAVELER_PAYS_UPGRADE"
    LONG_FLIGHT_APPROVED = "LONG_FLIGHT_APPROVED"
    LONG_FLIGHT_CONDITION_NOT_MET = "LONG_FLIGHT_CONDITION_NOT_MET"
    PREMIUM_ECONOMY_ALLOWED = "PREMIUM_ECONOMY_ALLOWED"
    UPGRADE_COST_NOT_NOMINAL = "UPGRADE_COST_NOT_NOMINAL"
    ALTERNATE_ROUTE_WITHIN_MARGIN = "ALTERNATE_ROUTE_WITHIN_MARGIN"
    ALTERNATE_ROUTE_TOO_EXPENSIVE = "ALTERNATE_ROUTE_TOO_EXPENSIVE"
    LOYALTY_PROGRAM_PREFERENCE = "LOYALTY_PROGRAM_PREFERENCE"
    COMPANION_NOT_COVERED = "COMPANION_NOT_COVERED"
    PERSONAL_TRAVEL_NOT_COVERED = "PERSONAL_TRAVEL_NOT_COVERED"
    OUTSIDE_POLICY_SCOPE = "OUTSIDE_POLICY_SCOPE"
    NO_COMPLIANT_OFFER = "NO_COMPLIANT_OFFER"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    UNCLEAR_POLICY_TEXT = "UNCLEAR_POLICY_TEXT"
    ADVANCE_PURCHASE_TOO_LATE = "ADVANCE_PURCHASE_TOO_LATE"
    DISTANCE_BELOW_MINIMUM = "DISTANCE_BELOW_MINIMUM"
    DRIVING_EXPECTED = "DRIVING_EXPECTED"
    RAIL_PREFERRED = "RAIL_PREFERRED"
    REFUNDABLE_FARE_NOT_ALLOWED = "REFUNDABLE_FARE_NOT_ALLOWED"
    PREFERRED_CARRIER_REQUIRED = "PREFERRED_CARRIER_REQUIRED"
    CONNECTION_TOO_LONG = "CONNECTION_TOO_LONG"
    OVERNIGHT_STOP_REQUIRED = "OVERNIGHT_STOP_REQUIRED"
    NATIONAL_CARRIER_REQUIRED = "NATIONAL_CARRIER_REQUIRED"
    SENIOR_ROLE_ENTITLEMENT = "SENIOR_ROLE_ENTITLEMENT"
    INTERNATIONAL_LONG_FLIGHT = "INTERNATIONAL_LONG_FLIGHT"
    TRAVELLER_LIMIT_PER_FLIGHT = "TRAVELLER_LIMIT_PER_FLIGHT"
    # HANDBOOK-SPECIFIC reason codes go below this line; keep every shared one above.
    STATE_CONTRACT_FARE = "STATE_CONTRACT_FARE"
    CAPACITY_CONTROLLED_FARE_AVAILABLE = "CAPACITY_CONTROLLED_FARE_AVAILABLE"
    CAPACITY_CONTROLLED_SOLD_OUT = "CAPACITY_CONTROLLED_SOLD_OUT"
    NON_REFUNDABLE_BELOW_CONTRACT_FARE = "NON_REFUNDABLE_BELOW_CONTRACT_FARE"
    NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE = "NON_REFUNDABLE_NOT_BELOW_CONTRACT_FARE"
    SOUTHWEST_IN_STATE_FARE = "SOUTHWEST_IN_STATE_FARE"
    NON_CONTRACT_CARRIER_JUSTIFIED = "NON_CONTRACT_CARRIER_JUSTIFIED"
    REFUNDABLE_FARE_JUSTIFIED = "REFUNDABLE_FARE_JUSTIFIED"
    DOMESTIC_SHORT_NOTICE_JUSTIFIED = "DOMESTIC_SHORT_NOTICE_JUSTIFIED"
    INTERNATIONAL_SHORT_NOTICE_JUSTIFIED = "INTERNATIONAL_SHORT_NOTICE_JUSTIFIED"
    UNUSED_TICKET_CREDIT_APPLIED = "UNUSED_TICKET_CREDIT_APPLIED"
    EXTRA_SEAT_APPROVED = "EXTRA_SEAT_APPROVED"
    CONTRACT_FARE_NOT_FOR_PERSONAL_TRAVEL = "CONTRACT_FARE_NOT_FOR_PERSONAL_TRAVEL"
    COMMUTING_NOT_REIMBURSABLE = "COMMUTING_NOT_REIMBURSABLE"
    PRIVATE_AIRCRAFT_NOT_APPROVED = "PRIVATE_AIRCRAFT_NOT_APPROVED"
    # Decoys: codes for rules of other handbooks that this one lacks, so the list hints at none of its own rules.
    WEEKEND_TRAVEL_HOME = "WEEKEND_TRAVEL_HOME"
    WEEKEND_TRIP_NOT_EARNED = "WEEKEND_TRIP_NOT_EARNED"
    NEXT_OF_KIN_TRAVEL = "NEXT_OF_KIN_TRAVEL"
    FLY_AMERICA_US_CARRIER_REQUIRED = "FLY_AMERICA_US_CARRIER_REQUIRED"
    OPEN_SKIES_AGREEMENT = "OPEN_SKIES_AGREEMENT"
    CREATIVE_TICKETING = "CREATIVE_TICKETING"
    CHANCELLOR_WRITTEN_AUTHORIZATION = "CHANCELLOR_WRITTEN_AUTHORIZATION"
    DOUBLE_BOOKING_PROHIBITED = "DOUBLE_BOOKING_PROHIBITED"
    SAME_CLASS_AS_CUSTOMER = "SAME_CLASS_AS_CUSTOMER"
    CANDIDATE_TRIP_NOT_COVERED = "CANDIDATE_TRIP_NOT_COVERED"
    DENIED_BOARDING_NOT_ALLOWED = "DENIED_BOARDING_NOT_ALLOWED"


class TripType(Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class Topic(Enum):
    ALL = "ALL"
    FIELDS = "FIELDS"
    AIRPORTS = "AIRPORTS"


CODE = "An IATA airport code, e.g. JFK"


@dataclass
class Airport(Output):
    code: Annotated[str, CODE]
    name: Annotated[str, "The airport's name"]
    city: Annotated[str, "The city it serves"]
    country: Annotated[str, "Its country, as an ISO code"]


@dataclass
class Segment(Output):
    flight_number: Annotated[str, "The airline's flight number, e.g. BA 117"]
    origin: Annotated[str, CODE]
    destination: Annotated[str, CODE]
    depart_local: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, local time at that airport"]
    arrive_local: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, local time at that airport"]
    depart_utc: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, UTC"]
    arrive_utc: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, UTC"]
    scheduled_minutes: Annotated[int, "Its scheduled time from departure to arrival, in minutes"]


@dataclass
class Offer(Output):
    offer_id: Annotated[str, "The offer's id, to submit when booking or holding it"]
    carrier: Annotated[str, "The airline"]
    trip_type: Annotated[TripType, "ONE_WAY, or ROUND_TRIP when the fare covers the flights out and back"]
    cabin: Annotated[Cabin, "The cabin sold on every flight of the offer"]
    fare_cents: Annotated[int, "The whole fare for one passenger, in cents of the search's currency"]
    seats_available: Annotated[bool, "False when this cabin is sold out on these flights: it is listed but cannot be bought"]
    refundable: Annotated[bool, "Whether the fare can be refunded or changed without a fee"]
    stops: Annotated[int, "Connections on the way out; zero for a nonstop"]
    segments: Annotated[list[Segment], "The flights out, in order"]
    layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights out"]
    stopover_nights: Annotated[list[bool], "Per connection out: true when it is a ticketed stopover with a hotel night booked"]
    flying_minutes: Annotated[int, "The flights' scheduled minutes out added together, ground time left out"]
    elapsed_minutes: Annotated[int, "Minutes from the first departure out to the last arrival, ground time included"]
    return_segments: Annotated[list[Segment], "For a round trip, the flights back, in order; empty otherwise"]
    return_layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights back"]
    return_stopover_nights: Annotated[list[bool], "Per connection back: true for a ticketed stopover with a hotel night"]
    return_flying_minutes: Annotated[int, "The flights' scheduled minutes back added together; zero one way"]
    return_elapsed_minutes: Annotated[int, "Minutes from the first departure back to the last arrival; zero one way"]


# ---------------------------------------------------------------------------------------------------------
# HANDBOOK-SPECIFIC: Caltrans Accounting Manual, Chapter 15 - Transportation (05/14/24).
# ---------------------------------------------------------------------------------------------------------


class Scenario(Enum):
    AGATE_COVE = "agate-cove"
    BODEGA_FERN = "bodega-fern"
    CYPRESS_LARK = "cypress-lark"
    DUNE_SPARROW = "dune-sparrow"
    ELKHORN_REED = "elkhorn-reed"
    SAGE_INLET = "sage-inlet"
    GARNET_SLOUGH = "garnet-slough"
    HERON_QUAY = "heron-quay"
    INDIGO_MESA = "indigo-mesa"
    JUNIPER_TIDE = "juniper-tide"
    KELP_RIDGE = "kelp-ridge"
    LAUREL_WASH = "laurel-wash"
    MANZANITA_POOL = "manzanita-pool"
    NOPAL_CREST = "nopal-crest"
    FENNEL_BLUFF = "fennel-bluff"
    POPPY_LEDGE = "poppy-ledge"
    ORIOLE_BEND = "oriole-bend"
    QUAIL_HOLLOW = "quail-hollow"
    REDWOOD_SPUR = "redwood-spur"
    TULE_MARSH = "tule-marsh"
    UMBER_CANYON = "umber-canyon"
    VIREO_POINT = "vireo-point"
    WILLOW_FLAT = "willow-flat"
    YUCCA_STRAND = "yucca-strand"
    ALDER_ROOK = "alder-rook"
    BASALT_CLIFF = "basalt-cliff"
    COYOTE_DELL = "coyote-dell"
    DOVE_TERRACE = "dove-terrace"
    EGRET_SHOAL = "egret-shoal"
    FINCH_ARROYO = "finch-arroyo"
    GRANITE_WREN = "granite-wren"
    HAZEL_KILN = "hazel-kiln"


class Approver(Enum):
    """Roles that may sign off. NONE: the decision relies on no one's sign-off, given or awaited (one for
    something else may be on file). NOT_NAMED: one is needed, but the handbook names no role."""

    NONE = "NONE"
    NOT_NAMED = "NOT_NAMED"
    SUPERVISOR = "SUPERVISOR"
    APPOINTING_AUTHORITY = "APPOINTING_AUTHORITY"
    RESOURCE_AND_INNOVATION_DIVISION = "RESOURCE_AND_INNOVATION_DIVISION"
    PROGRAM_TRAVEL_COORDINATOR = "PROGRAM_TRAVEL_COORDINATOR"
    DIRECTOR = "DIRECTOR"
    GOVERNORS_OFFICE = "GOVERNORS_OFFICE"
    STATE_CONTROLLERS_OFFICE = "STATE_CONTROLLERS_OFFICE"
    ACCOUNTING = "ACCOUNTING"
    TRAVEL_AGENCY = "TRAVEL_AGENCY"
    GENERAL_SERVICES = "GENERAL_SERVICES"
    CHIEF_FINANCIAL_OFFICER = "CHIEF_FINANCIAL_OFFICER"
    VICE_PRESIDENT = "VICE_PRESIDENT"


class Clause(Enum):
    """The handbook's sections, by heading."""

    TRANSPORTATION_GENERAL = "TRANSPORTATION_GENERAL"
    THIRD_PARTY_VENDORS = "THIRD_PARTY_VENDORS"
    CHOOSING_MODE = "CHOOSING_MODE"
    EMPLOYEE_RESPONSIBILITY = "EMPLOYEE_RESPONSIBILITY"
    SUPERVISOR_RESPONSIBILITY = "SUPERVISOR_RESPONSIBILITY"
    COMMERCIAL_AIR_TRAVEL = "COMMERCIAL_AIR_TRAVEL"
    NON_REFUNDABLE_AIRFARE = "NON_REFUNDABLE_AIRFARE"
    REFUNDABLE_AIRFARE = "REFUNDABLE_AIRFARE"
    REASON_CODE_JUSTIFICATIONS = "REASON_CODE_JUSTIFICATIONS"
    PASSENGERS_OF_SIZE = "PASSENGERS_OF_SIZE"
    OUT_OF_STATE_APPROVAL = "OUT_OF_STATE_APPROVAL"
    INTERNATIONAL_AIRFARE = "INTERNATIONAL_AIRFARE"
    CHECKED_BAGGAGE = "CHECKED_BAGGAGE"
    AIRFARE_REIMBURSEMENT_CLAIMS = "AIRFARE_REIMBURSEMENT_CLAIMS"
    PRIVATELY_OWNED_AIRCRAFT = "PRIVATELY_OWNED_AIRCRAFT"
    AGENCY_RENTED_AIRCRAFT = "AGENCY_RENTED_AIRCRAFT"
    COMMERCIAL_CAR_RENTAL = "COMMERCIAL_CAR_RENTAL"
    PRIVATE_VEHICLE_USE = "PRIVATE_VEHICLE_USE"
    COST_COMPARISON_IN_LIEU = "COST_COMPARISON_IN_LIEU"
    PARKING_AND_TOLLS = "PARKING_AND_TOLLS"
    RAIL = "RAIL"
    OTHER_MODES = "OTHER_MODES"


class Passenger(Enum):
    EMPLOYEE = "EMPLOYEE"
    SPOUSE_OR_FAMILY = "SPOUSE_OR_FAMILY"


class Purpose(Enum):
    MEETING = "MEETING"
    CONFERENCE = "CONFERENCE"
    TRAINING = "TRAINING"
    HEARING = "HEARING"
    SITE_INSPECTION = "SITE_INSPECTION"
    HEADQUARTERS_OFFICE_DAY = "HEADQUARTERS_OFFICE_DAY"
    PERSONAL = "PERSONAL"


class FareWish(Enum):
    """The kind of fare the traveller asks for."""

    ANY = "ANY"
    REFUNDABLE = "REFUNDABLE"
    YCAL = "YCAL"


class ContractFareKind(Enum):
    CAPACITY_CONTROLLED = "CAPACITY_CONTROLLED"
    YCAL = "YCAL"


class SignOffSubject(Enum):
    TRIP = "TRIP"
    OUT_OF_STATE_TRIP = "OUT_OF_STATE_TRIP"
    FIRST_SEAT_RESERVATION = "FIRST_SEAT_RESERVATION"
    EXTRA_SEAT_RESERVATION = "EXTRA_SEAT_RESERVATION"


class SignOffStatus(Enum):
    APPROVED = "APPROVED"
    PENDING = "PENDING"


@dataclass
class ContractFare(Output):
    carrier: Annotated[str, "The airline, as search_flights names it"]
    kind: Annotated[ContractFareKind, "Which of the state's contracted fares it is"]
    fare_cents: Annotated[int, "The contracted fare for one passenger, one way, in cents of the search's currency"]


@dataclass
class SignOff(Output):
    role: Annotated[Approver, "The role of the person or office that signs"]
    name: Annotated[str, "Their name, or the office's"]
    subject: Annotated[SignOffSubject, "What it covers"]
    status: Annotated[SignOffStatus, "APPROVED when given; PENDING when asked for and not yet given"]
    date: Annotated[str, "The day it was given or asked for, YYYY-MM-DD"]


@dataclass
class TicketCredit(Output):
    airline: Annotated[str, "The airline that holds it, as search_flights names it"]
    amount_cents: Annotated[int, "Its value, in cents of the search's currency"]
    holder_name: Annotated[str, "The employee the cancelled ticket was issued to"]
    usable_through: Annotated[str, "The last local departure date of a flight it can pay for, YYYY-MM-DD"]


@dataclass
class Trip(Output):
    traveller_name: Annotated[str, "Who flies"]
    traveller_title: Annotated[str, "Their job title, or their relation to the employee they go with"]
    passenger: Annotated[Passenger, "What the person flying is to the department"]
    accompanies: Annotated[str, "For a spouse or family member, the employee they go with; empty otherwise"]
    headquarters: Annotated[str, "The traveller's designated headquarters: office, city and state"]
    residence: Annotated[str, "Where the traveller lives: city and state"]
    on_telework: Annotated[bool, "True when the traveller is on telework status"]
    origin: Annotated[Airport, "Where the flight leaves from"]
    destination: Annotated[Airport, "Where it goes"]
    destination_region: Annotated[str, "The U.S. state the destination is in, or its country outside the United States"]
    travel_date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport"]
    booking_date: Annotated[str, "Today in this world, the day the ticket is bought, YYYY-MM-DD"]
    purpose: Annotated[str, "Why the trip is made, in plain words"]
    purpose_kind: Annotated[Purpose, "The kind of trip"]
    must_arrive_by: Annotated[
        str, "The latest local date and time at the destination, YYYY-MM-DD HH:MM, at which the traveller can land and still do the business; empty when there is no such limit"
    ]
    requested_cabin: Annotated[Cabin, "The cabin the traveller asks for"]
    requested_airline: Annotated[str, "An airline the traveller asks for, as search_flights names it; empty when none"]
    requested_fare: Annotated[FareWish, "The kind of fare the traveller asks for; ANY when they ask for none"]
    connections_ok: Annotated[bool, "True when the traveller says a connecting flight is fine with them"]
    plans_fixed: Annotated[bool, "True when the trip's dates are settled and a change of plans is unlikely"]
    assignment_email_on_file: Annotated[
        bool, "True when an email on file sets out a last-minute assignment and why the trip cannot wait"
    ]
    extra_seat_needed: Annotated[bool, "True when the traveller needs the seat beside theirs as well, on the same flight"]
    contract_fares: Annotated[
        list[ContractFare], "The state's contracted fares for this trip's city pair, as the travel agency lists them"
    ]
    ticket_credits: Annotated[list[TicketCredit], "Unused ticket credits from cancelled tickets that are on file"]
    sign_offs: Annotated[list[SignOff], "Sign-offs on file for this trip, given or asked for"]
    notes: Annotated[list[str], "Other facts on file for this trip"]


# ---------------------------------------------------------------------------------------------------------
# SHARED (template), continued: the tools' and tasks' inputs and outputs.
# ---------------------------------------------------------------------------------------------------------


@dataclass
class TaskInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    request: Annotated[str, "The traveller's request, in their own words"]


@dataclass
class TripInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id, as the task input gives it"]


@dataclass
class TripOutput(Output):
    scenario: Annotated[Scenario, "The case id"]
    request: Annotated[str, "The traveller's request, in their own words"]
    trip: Annotated[Trip, "The trip record behind the request"]


@dataclass
class SearchInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    origin: Annotated[str, "The airport to leave from: An IATA airport code, e.g. JFK"]
    destination: Annotated[str, "The airport to fly to: An IATA airport code, e.g. JFK"]
    date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport, on or after the booking date"]
    return_date: Annotated[str, "For round-trip fares, the day to fly back, YYYY-MM-DD, local at the destination; empty for one way"]


@dataclass
class SearchOutput(Output):
    note: Annotated[str, "Where the offers come from, and a word when this case lists none for the search"]
    currency: Annotated[str, "The currency of every fare, as an ISO code"]
    offers: Annotated[list[Offer], "Every offer leaving on that local date, in departure order"]


@dataclass
class BookingOutput(Output):
    decision: Annotated[
        Decision,
        "BOOK: buy offer_id now. REFUSE: buy nothing, because the organisation buys no ticket at all for this request. "
        "FLAG_FOR_APPROVAL: hold offer_id and buy nothing yet, because someone must approve it first or "
        "the handbook's words leave the answer open",
    ]
    offer_id: Annotated[str, "The offer bought or held, exactly as search_flights listed it; empty when refusing"]
    cabin: Annotated[Cabin, "That offer's cabin; NONE when refusing"]
    reason_code: Annotated[ReasonCode, "Why, from the closed list"]
    approver: Annotated[
        Approver,
        "The role whose sign-off this decision relies on, whether already on file or still awaited; NONE when "
        "this decision relies on no one's sign-off, even if a sign-off for something else is on file; NOT_NAMED "
        "when a sign-off is needed but the handbook names no role",
    ]
    clause: Annotated[Clause, "The handbook section the decision rests on"]


@dataclass
class SolveOutput(Output):
    trip: Annotated[Trip, "The trip record"]
    offers: Annotated[list[Offer], "Every offer on the trip's route and date"]
    decision: Annotated[Decision, "The correct decision"]
    offer_ids: Annotated[list[str], "Every offer id that is a correct choice; empty when refusing"]
    cabins: Annotated[list[Cabin], "Every correct cabin"]
    reason_codes: Annotated[list[ReasonCode], "Every accepted reason"]
    approvers: Annotated[list[Approver], "Every accepted approver"]
    clauses: Annotated[list[Clause], "Every accepted section"]
    unclear_phrase: Annotated[str, "For a hold over unclear words, those words; empty otherwise"]
    explanation: Annotated[str, "How the answer key reached the answer"]


@dataclass
class FieldHelp(Output):
    name: Annotated[str, "The trip record field's name"]
    kind: Annotated[str, "Its type"]
    description: Annotated[str, "What it means"]


@dataclass
class RequirementsInput(Output):
    topic: Annotated[Topic, "ALL for everything, FIELDS for the trip record's fields, AIRPORTS for the airport list"]


@dataclass
class RequirementsOutput(Output):
    fields: Annotated[list[FieldHelp], "The trip record's fields; empty for AIRPORTS"]
    conventions: Annotated[list[str], "How times, dates, fares and seats work in this world; empty for AIRPORTS"]
    airports: Annotated[list[Airport], "The airports the simulated world knows; empty for FIELDS"]


TOOLS = {
    Tool.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Tool.GET_TRIP: (TripInput, TripOutput),
    Tool.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Tool.SOLVE_BOOKING: (TaskInput, SolveOutput),
}
TASKS = {
    Task.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Task.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Task.BOOK_FLIGHT: (TaskInput, BookingOutput),
}
