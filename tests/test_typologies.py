import pytest

from aml_triage.data_access import AMLDataStore
from aml_triage.typologies import (
    detect_high_risk_customer,
    detect_rapid_large_transfers,
    detect_repeated_similar_transfers,
    run_all_typology_checks,
)


@pytest.fixture
def store():
    return AMLDataStore()


def test_repeated_transfers_are_flagged(store):
    transactions = store.get_transactions_for_alert("ALERT002")

    findings = detect_repeated_similar_transfers(transactions)

    assert any(
        finding.finding_type == "REPEATED_SIMILAR_TRANSFERS"
        for finding in findings
    )


def test_rapid_large_transfers_are_flagged(store):
    transactions = store.get_transactions_for_alert("ALERT003")

    findings = detect_rapid_large_transfers(
        transactions,
        minimum_amount=20000,
        window_hours=2,
    )

    assert any(
        finding.finding_type == "RAPID_LARGE_TRANSFERS"
        for finding in findings
    )


def test_high_risk_customer_is_flagged(store):
    customer = store.get_customer("CUST003")
    transactions = store.get_transactions_for_alert("ALERT003")

    findings = detect_high_risk_customer(customer, transactions)

    assert len(findings) == 1
    assert findings[0].severity == "MEDIUM"


def test_benign_transactions_do_not_trigger_repeated_transfer_rule(store):
    transactions = store.get_transactions_for_alert("ALERT001")

    findings = detect_repeated_similar_transfers(transactions)

    assert findings == []


def test_all_checks_return_findings(store):
    customer = store.get_customer("CUST003")
    transactions = store.get_transactions_for_alert("ALERT003")

    findings = run_all_typology_checks(transactions, customer)

    assert len(findings) >= 2


def test_invalid_window_is_rejected(store):
    transactions = store.get_transactions_for_alert("ALERT002")

    with pytest.raises(ValueError):
        detect_repeated_similar_transfers(
            transactions,
            window_hours=0,
        )