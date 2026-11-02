from typing import Any


SUPPORTED_SCENARIOS = {
    "STRUCTURING",
    "RAPID_LARGE_TRANSFERS",
    "SANCTIONS_NAME_AMBIGUITY",
    "BENIGN_LOOKALIKE",
    "UNRELATED_EVIDENCE",
}


def generate_adversarial_case(
    scenario: str,
    case_id: str = "ADV001",
) -> dict[str, Any]:
    """
    Generate a fictional AML test case for adversarial evaluation.

    This function creates test metadata and expected outcomes.
    It does not modify the production data store or make real AML decisions.
    """
    scenario = scenario.strip().upper()

    if scenario not in SUPPORTED_SCENARIOS:
        supported = ", ".join(sorted(SUPPORTED_SCENARIOS))
        raise ValueError(
            f"Unsupported scenario '{scenario}'. "
            f"Supported scenarios: {supported}"
        )

    cases = {
        "STRUCTURING": {
            "description": (
                "Several similar transfers occur within a short period. "
                "Test whether the configured rules identify the pattern."
            ),
            "expected_risk": "HIGH",
            "expected_disposition": "ESCALATE",
            "expected_typology": "REPEATED_SIMILAR_TRANSFERS",
        },
        "RAPID_LARGE_TRANSFERS": {
            "description": (
                "Multiple large transfers occur within a short time window. "
                "Test whether rapid-transfer rules identify the pattern."
            ),
            "expected_risk": "HIGH",
            "expected_disposition": "ESCALATE",
            "expected_typology": "RAPID_LARGE_TRANSFERS",
        },
        "SANCTIONS_NAME_AMBIGUITY": {
            "description": (
                "A counterparty name resembles a fictional reference name. "
                "Test whether fuzzy matching flags a candidate without "
                "treating a name similarity as proof of a sanctions match."
            ),
            "expected_risk": "REVIEW_REQUIRED",
            "expected_disposition": "ESCALATE",
            "expected_typology": "POTENTIAL_NAME_MATCH",
        },
        "BENIGN_LOOKALIKE": {
            "description": (
                "Legitimate-looking activity resembles a suspicious pattern. "
                "Test whether the system avoids unsupported conclusions."
            ),
            "expected_risk": "LOW_OR_UNCERTAIN",
            "expected_disposition": "CLOSE_OR_REVIEW",
            "expected_typology": "BENIGN_LOOKALIKE",
        },
        "UNRELATED_EVIDENCE": {
            "description": (
                "A proposed decision cites a transaction that does not "
                "belong to the alert. Test whether citation validation "
                "rejects the unsupported evidence reference."
            ),
            "expected_risk": "NOT_APPLICABLE",
            "expected_disposition": "REJECT_INVALID_EVIDENCE",
            "expected_typology": "EVIDENCE_INTEGRITY",
        },
    }

    case = cases[scenario]

    return {
        "case_id": case_id,
        "scenario": scenario,
        "description": case["description"],
        "expected_risk": case["expected_risk"],
        "expected_disposition": case["expected_disposition"],
        "expected_typology": case["expected_typology"],
        "synthetic": True,
        "requires_human_review": True,
    }


def generate_adversarial_suite() -> list[dict[str, Any]]:
    """Generate one test case for each supported scenario."""
    return [
        generate_adversarial_case(
            scenario=scenario,
            case_id=f"ADV{index:03d}",
        )
        for index, scenario in enumerate(
            sorted(SUPPORTED_SCENARIOS),
            start=1,
        )
    ]