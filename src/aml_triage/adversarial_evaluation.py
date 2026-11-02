import json
from pathlib import Path
from typing import Any

from aml_triage.adversary_agent import generate_adversarial_suite
from aml_triage.citations import validate_decision_citations
from aml_triage.data_access import AMLDataStore
from aml_triage.sanctions import screen_name
from aml_triage.schemas import EvidenceCitation, TriageDecision, Disposition
from aml_triage.typologies import (
    detect_rapid_large_transfers,
    detect_repeated_similar_transfers,
)


def run_adversarial_evaluation(
    store: AMLDataStore | None = None,
) -> dict[str, Any]:
    """
    Run focused adversarial checks against synthetic AML data.

    These are targeted component-level checks, not complete end-to-end
    executions of every scenario through the LangGraph agent.
    """
    data_store = store if store is not None else AMLDataStore()
    cases = generate_adversarial_suite()
    results = []

    for case in cases:
        scenario = case["scenario"]

        result = {
            "case_id": case["case_id"],
            "scenario": scenario,
            "expected_disposition": case["expected_disposition"],
            "observed": None,
            "passed": False,
            "error": None,
            "test_scope": "component-level",
        }

        try:
            if scenario == "STRUCTURING":
                transactions = data_store.get_transactions_for_alert(
                    "ALERT002"
                )
                findings = detect_repeated_similar_transfers(transactions)

                observed = {
                    "detected": bool(findings),
                    "finding_count": len(findings),
                }
                passed = bool(findings)

            elif scenario == "RAPID_LARGE_TRANSFERS":
                transactions = data_store.get_transactions_for_alert(
                    "ALERT003"
                )
                findings = detect_rapid_large_transfers(transactions)

                observed = {
                    "detected": bool(findings),
                    "finding_count": len(findings),
                }
                passed = bool(findings)

            elif scenario == "SANCTIONS_NAME_AMBIGUITY":
                matches = screen_name(
                    "Vladmir Example",
                    ["Vladimir Example"],
                    threshold=80,
                )

                observed = {
                    "candidate_found": bool(matches),
                    "match_type": (
                        matches[0].match_type if matches else None
                    ),
                    "score": matches[0].score if matches else None,
                }

                passed = (
                    bool(matches)
                    and matches[0].match_type == "FUZZY"
                    and matches[0].score < 100
                )

            elif scenario == "BENIGN_LOOKALIKE":
                transactions = data_store.get_transactions_for_alert(
                    "ALERT001"
                )
                findings = detect_repeated_similar_transfers(transactions)

                observed = {
                    "suspicious_pattern_detected": bool(findings),
                    "finding_count": len(findings),
                }
                passed = not findings

            elif scenario == "UNRELATED_EVIDENCE":
                decision = TriageDecision(
                    alert_id="ALERT002",
                    disposition=Disposition.ESCALATE,
                    rationale="Synthetic test for unrelated evidence.",
                    citations=[
                        EvidenceCitation(
                            transaction_id="TXN001",
                            claim="Test citation unrelated to this alert.",
                        )
                    ],
                    risk_score=0.8,
                    requires_human_review=True,
                )

                valid, errors = validate_decision_citations(
                    decision,
                    data_store,
                )

                observed = {
                    "citation_valid": valid,
                    "validation_errors": errors,
                }
                passed = not valid

            else:
                raise ValueError(
                    f"No executable check for scenario: {scenario}"
                )

            result["observed"] = observed
            result["passed"] = passed

        except Exception as exc:
            result["error"] = f"{type(exc).__name__}: {exc}"

        results.append(result)

    total = len(results)
    passed_count = sum(item["passed"] for item in results)
    failed_count = total - passed_count

    return {
        "report_type": "adversarial_component_evaluation",
        "synthetic_data_only": True,
        "total_cases": total,
        "passed_cases": passed_count,
        "failed_cases": failed_count,
        "pass_rate": passed_count / total if total else 0.0,
        "results": results,
        "limitations": [
            (
                "Scenario definitions are metadata; this harness executes "
                "targeted component checks."
            ),
            (
                "The sanctions test uses a fictional reference name, "
                "not an official sanctions list."
            ),
            (
                "A passing component check does not establish production "
                "AML effectiveness."
            ),
            (
                "The benign-lookalike check only tests the repeated-transfer "
                "rule, not every possible typology."
            ),
        ],
    }


def save_adversarial_report(
    output_path: str = "reports/adversarial_evaluation_report.json",
    store: AMLDataStore | None = None,
) -> dict[str, Any]:
    """Run adversarial checks and save their results as JSON."""
    report = run_adversarial_evaluation(store)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    return report