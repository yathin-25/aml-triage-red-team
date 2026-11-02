from aml_triage.data_access import AMLDataStore
from aml_triage.schemas import TriageDecision


def validate_decision_citations(
    decision: TriageDecision,
    store: AMLDataStore,
) -> tuple[bool, list[str]]:
    """
    Check whether every citation refers to a real transaction
    belonging to the alert's customer and alert transaction list.
    """
    errors = []

    try:
        alert = store.get_alert(decision.alert_id)
    except KeyError:
        return False, [f"Unknown alert ID: {decision.alert_id}"]

    if not decision.citations:
        errors.append("Decision contains no evidence citations.")

    for citation in decision.citations:
        try:
            transaction = store.get_transaction(citation.transaction_id)
        except KeyError:
            errors.append(
                f"Unknown transaction ID: {citation.transaction_id}"
            )
            continue

        if transaction.customer_id != alert.customer_id:
            errors.append(
                f"Transaction {citation.transaction_id} belongs to "
                "a different customer."
            )

        if citation.transaction_id not in alert.transaction_ids:
            errors.append(
                f"Transaction {citation.transaction_id} is not linked "
                f"to alert {decision.alert_id}."
            )

        if not citation.claim.strip():
            errors.append(
                f"Citation for {citation.transaction_id} has an empty claim."
            )

    return len(errors) == 0, errors