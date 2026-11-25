"""The handbook-specific settings the template's acceptance tests read. Every other file in tests/ is the
template's and stays identical across plugins (see TEMPLATE_GUIDE.md)."""

from pathlib import Path

import contract

ROOT = Path(__file__).resolve().parents[1]

# Ids that are published or taken: a new plugin never reuses one (MASTER_PLAN section 4, "id check").
PUBLISHED_IDS = {
    "aiib-delegation-entitlement", "ec-mission-cabin-allowance", "ftr-city-pair-fare-selection",
    "gates-vendor-flight-ranking", "njc-cabin-meal-allowance", "sfc-travel-preapproval", "uc-g28-expense-audit",
    "un-staff-air-travel-audit", "vt-airfare-policy-booking", "wa-saam-travel-versioned-audit",
    "energy-corporate-flight-booking", "pharma-distributor-flight-booking", "shipping-company-flight-booking",
    "telecommunications-flight-booking", "preference-aware-flight-booking", "llm-context-compress",
    "weather-alert", "word-check", "arxiv-source",
}

# The frozen original's SHA256SUMS, when this checkout sits beside pilot_work/ (skipped elsewhere).
FROZEN_SHA256SUMS = ROOT.parents[1] / "pilot_work" / "originals" / "caltrans-ch15" / "frozen" / "SHA256SUMS"

# Scenario mix by primary category (EDGE_CASES.md section 5.2; the 32-scenario row).
MIX = {"easy": 6, "boundary_twin": 8, "multi_rule": 5, "hidden_clause": 3, "distractor": 3, "refusal": 3, "flag": 4}

# Overlay minimums (EDGE_CASES.md section 5.3) for the rules this handbook has. "upgrade_not_taken" is the
# YCAL upgrade (lines 206-207) or a better cabin the chapter never grants; the overnight-stop multi-leg case is
# left out, since the chapter has no overnight-stop rule.
OVERLAY_MINIMUMS = {
    "multi_leg": 3, "date_arithmetic": 2, "month_end": 1, "personal_travel": 1, "multi_traveller": 1,
    "dearer_option": 2, "upgrade_not_taken": 2, "outside_air_section": 2,
}

# Words a scenario id may not contain beyond the template's universal list: this handbook's rule and role
# terms.
ID_FORBIDDEN_TERMS = {
    "caltrans", "california", "contract", "contracted", "dgs", "ycal", "capacity", "controlled", "refundable",
    "refund", "nonrefundable", "southwest", "alaska", "united", "delta", "american", "jal", "air", "canada",
    "airline", "carrier", "concur", "azumano", "agency", "credit", "credits", "ticket", "voucher", "telework",
    "commute", "commuting", "residence", "home", "headquarters", "district", "personal", "spouse", "husband", "wife",
    "family", "companion", "seat", "seats", "armrest", "size", "notice", "advance", "late", "week", "weekly", "month",
    "international", "domestic", "abroad", "foreign", "instate", "coordinator", "division", "innovation",
    "supervisor", "approval", "appointing", "authority", "connection", "connecting", "layover", "nonstop", "stop",
    "stops", "delay", "expedia", "vendor", "bag", "bags", "baggage", "miles", "loyalty", "business", "economy",
    "first", "premium", "cabin", "fare", "fares", "lowest", "cost",
}

# The handbook-specific enums whose member words a scenario id may not contain either.
ID_CATEGORY_ENUMS = [contract.Passenger, contract.Purpose, contract.FareWish, contract.ContractFareKind,
                     contract.SignOffSubject, contract.SignOffStatus]

# How many scenarios a degenerate agent may pass: one that always holds the right offer for approval, and
# one that always books the cheapest seat (with the right section). Set to what each actually passes (README).
MAX_PASS_ALWAYS_FLAG = 2
MAX_PASS_ALWAYS_LOWEST = 13

# This handbook has no flight-length threshold (rules.DURATION_RULES is empty), so no hand-built cases.
DURATION_CASES = []
