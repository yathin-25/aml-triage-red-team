from aml_triage.data_access import AMLDataStore
from aml_triage.citations import validate_decision_citations
from aml_triage.schemas import (
    Disposition,
    EvidenceCitation,
    TriageDecision,
)


def make_decision(alert_id, citations):
    return TriageDecision(
        alert_id=alert_id,
        disposition=Disposition.ESCALATE,
        rationale="Synthetic test decision.",
        citations=citations,
        risk_score=0.8,
        requires_human_review=True,
    )


def test_valid_citation_passes():
    store = AMLDataStore()

    decision = make_decision(
        "ALERT002",
        [
            EvidenceCitation(
                transaction_id="TXN006",
                claim="Transfer is part of the alert's transaction set.",
            )
        ],
    )

    valid, errors = validate_decision_citations(decision, store)

    assert valid is True
    assert errors == []


def test_missing_citations_fail():
    store = AMLDataStore()
    decision = make_decision("ALERT002", [])

    valid, errors = validate_decision_citations(decision, store)

    assert valid is False
    assert any("no evidence citations" in error for error in errors)


def test_unknown_transaction_fails():
    store = AMLDataStore()

    decision = make_decision(
        "ALERT002",
        [
            EvidenceCitation(
                transaction_id="TXN-DOES-NOT-EXIST",
                claim="Unsupported evidence.",
            )
        ],
    )

    valid, errors = validate_decision_citations(decision, store)

    assert valid is False
    assert any("Unknown transaction ID" in error for error in errors)


def test_transaction_from_another_alert_fails():
    store = AMLDataStore()

    decision = make_decision(
        "ALERT002",
        [
            EvidenceCitation(
                transaction_id="TXN001",
                claim="This transaction is not linked to ALERT002.",
            )
        ],
    )

    valid, errors = validate_decision_citations(decision, store)

    assert valid is False
    assert any("not linked to alert" in error for error in errors)


def test_empty_claim_fails():
    store = AMLDataStore()

    decision = make_decision(
        "ALERT002",
        [
            EvidenceCitation(
                transaction_id="TXN006",
                claim="   ",
            )
        ],
    )

    valid, errors = validate_decision_citations(decision, store)

    assert valid is False
    assert any("empty claim" in error for error in errors)


def test_unknown_alert_fails():
    store = AMLDataStore()

    decision = make_decision(
        "ALERT-UNKNOWN",
        [
            EvidenceCitation(
                transaction_id="TXN006",
                claim="Synthetic claim.",
            )
        ],
    )

    valid, errors = validate_decision_citations(decision, store)

    assert valid is False
    assert any("Unknown alert ID" in error for error in errors)