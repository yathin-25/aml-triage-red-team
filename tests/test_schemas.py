import pytest
from pydantic import ValidationError

from aml_triage.schemas import (
    AMLAlert,
    Disposition,
    EvidenceCitation,
    TriageDecision,
    Transaction,
)


def test_valid_transaction():
    transaction = Transaction(
        transaction_id="TXN001",
        customer_id="CUST001",
        counterparty_name="Example Trading Ltd",
        amount=5000,
        currency="USD",
        timestamp="2026-10-01T10:00:00Z",
        transaction_type="WIRE",
    )
    assert transaction.amount == 5000


def test_rejects_non_positive_transaction_amount():
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="TXN002",
            customer_id="CUST001",
            counterparty_name="Example Trading Ltd",
            amount=0,
            timestamp="2026-10-01T10:00:00Z",
            transaction_type="WIRE",
        )


def test_alert_requires_transaction_ids():
    with pytest.raises(ValidationError):
        AMLAlert(
            alert_id="ALERT001",
            customer_id="CUST001",
            alert_type="STRUCTURING",
            description="Potential suspicious activity",
            transaction_ids=[],
        )


def test_valid_triage_decision():
    decision = TriageDecision(
        alert_id="ALERT001",
        disposition=Disposition.ESCALATE,
        rationale="Several transactions require further review.",
        citations=[
            EvidenceCitation(
                transaction_id="TXN001",
                claim="The transaction was for USD 5000.",
            )
        ],
        risk_score=0.75,
    )

    assert decision.disposition == Disposition.ESCALATE
    assert decision.risk_score == 0.75


def test_rejects_invalid_risk_score():
    with pytest.raises(ValidationError):
        TriageDecision(
            alert_id="ALERT001",
            disposition=Disposition.CLOSE,
            rationale="No suspicious activity identified.",
            risk_score=1.5,
        )