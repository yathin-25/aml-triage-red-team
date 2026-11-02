from typing import Any

from aml_triage.citations import validate_decision_citations
from aml_triage.data_access import AMLDataStore
from aml_triage.triage_agent import investigate_alert


def evaluate_alerts(
    store: AMLDataStore | None = None,
) -> dict[str, Any]:
    """
    Evaluate the triage agent against synthetic ground-truth labels.

    ESCALATE is treated as the positive class.
    Citation validity measures structural evidence-reference validity,
    not whether the cited evidence semantically proves each claim.
    """
    data_store = store if store is not None else AMLDataStore()

    results = []

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0
    citation_valid_count = 0
    failed_cases = 0

    for alert_record in data_store.alert_records:
        alert_id = alert_record["alert_id"]
        expected = data_store.get_ground_truth(alert_id)

        try:
            decision = investigate_alert(alert_id, data_store)

            predicted = decision.disposition.value

            citations_valid, citation_errors = (
                validate_decision_citations(decision, data_store)
            )

            if citations_valid:
                citation_valid_count += 1

            expected_positive = expected == "ESCALATE"
            predicted_positive = predicted == "ESCALATE"

            if expected_positive and predicted_positive:
                true_positive += 1
            elif not expected_positive and not predicted_positive:
                true_negative += 1
            elif not expected_positive and predicted_positive:
                false_positive += 1
            else:
                false_negative += 1

            results.append(
                {
                    "alert_id": alert_id,
                    "expected": expected,
                    "predicted": predicted,
                    "correct": expected == predicted,
                    "risk_score": decision.risk_score,
                    "citation_valid": citations_valid,
                    "citation_errors": citation_errors,
                    "error": None,
                }
            )

        except Exception as exc:
            failed_cases += 1

            results.append(
                {
                    "alert_id": alert_id,
                    "expected": expected,
                    "predicted": None,
                    "correct": False,
                    "risk_score": None,
                    "citation_valid": False,
                    "citation_errors": [],
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    total = len(results)
    successful = total - failed_cases
    correct_count = sum(
        result["correct"] for result in results
    )

    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative
    f1_denominator = 2 * true_positive + false_positive + false_negative

    precision = (
        true_positive / precision_denominator
        if precision_denominator
        else 0.0
    )

    recall = (
        true_positive / recall_denominator
        if recall_denominator
        else 0.0
    )

    f1_score = (
        2 * true_positive / f1_denominator
        if f1_denominator
        else 0.0
    )

    negative_denominator = true_negative + false_positive
    positive_denominator = true_positive + false_negative

    false_positive_rate = (
        false_positive / negative_denominator
        if negative_denominator
        else 0.0
    )

    false_negative_rate = (
        false_negative / positive_denominator
        if positive_denominator
        else 0.0
    )

    return {
        "total_alerts": total,
        "successful_evaluations": successful,
        "failed_evaluations": failed_cases,
        "accuracy": correct_count / total if total else 0.0,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "false_positive_rate": false_positive_rate,
        "false_negative_rate": false_negative_rate,
        "citation_validity_rate": (
            citation_valid_count / successful
            if successful
            else 0.0
        ),
        "confusion_matrix": {
            "true_positive": true_positive,
            "true_negative": true_negative,
            "false_positive": false_positive,
            "false_negative": false_negative,
        },
        "results": results,
    }