from datetime import datetime, timedelta, timezone

from aml_triage.adversary_agent import (
    generate_adversarial_case,
    generate_adversarial_suite,
)
from aml_triage.citations import validate_decision_citations
from aml_triage.data_access import AMLDataStore
from aml_triage.schemas import (
    Disposition,
    EvidenceCitation,
    Transaction,
    TriageDecision,
)
from aml_triage.typologies import (
    detect_rapid_large_transfers,
    detect_repeated_similar_transfers,
)


def make_transaction(
    transaction_id,
    amount,
    timestamp,
    counterparty="Fictional Trading Ltd",
) -> Transaction:
    return Transaction(
        transaction_id=transaction_id,
        customer_id="ADV_CUSTOMER",
        counterparty_name=counterparty,
        amount=amount,
        currency="USD",
        timestamp=timestamp.isoformat(),
        transaction_type="WIRE",
    )


def test_adversarial_suite_contains_five_scenarios():
    cases = generate_adversarial_suite()

    assert len(cases) == 5
    assert all(case["synthetic"] for case in cases)
    assert all(case["requires_human_review"] for case in cases)


def test_unknown_adversarial_scenario_is_rejected():
    try:
        generate_adversarial_case("UNKNOWN_SCENARIO")
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown scenarios must be rejected.")


def test_repeated_similar_transfers_are_detected():
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)

    transactions = [
        make_transaction("ADV-TX-001", 9800, start),
        make_transaction("ADV-TX-002", 9700, start + timedelta(hours=2)),
        make_transaction("ADV-TX-003", 9600, start + timedelta(hours=4)),
    ]

    findings = detect_repeated_similar_transfers(transactions)

    assert any(
        finding.finding_type == "REPEATED_SIMILAR_TRANSFERS"
        for finding in findings
    )


def test_two_large_transfers_within_two_hours_are_detected():
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)

    transactions = [
        make_transaction("ADV-TX-004", 25000, start),
        make_transaction(
            "ADV-TX-005",
            24800,
            start + timedelta(minutes=30),
        ),
    ]

    findings = detect_rapid_large_transfers(transactions)

    assert any(
        finding.finding_type == "RAPID_LARGE_TRANSFERS"
        for finding in findings
    )


def test_large_transfers_outside_window_are_not_flagged_as_rapid():
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)

    transactions = [
        make_transaction("ADV-TX-006", 25000, start),
        make_transaction(
            "ADV-TX-007",
            24800,
            start + timedelta(hours=3),
        ),
    ]

    findings = detect_rapid_large_transfers(transactions)

    assert not any(
        finding.finding_type == "RAPID_LARGE_TRANSFERS"
        for finding in findings
    )


def test_benign_transactions_do_not_trigger_pattern_rules():
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)

    transactions = [
        make_transaction("ADV-TX-008", 40, start),
        make_transaction(
            "ADV-TX-009",
            125,
            start + timedelta(hours=30),
        ),
    ]

    repeated_findings = detect_repeated_similar_transfers(transactions)
    rapid_findings = detect_rapid_large_transfers(transactions)

    assert repeated_findings == []
    assert rapid_findings == []


def test_adversarial_cross_customer_citation_is_rejected():
    store = AMLDataStore()

    decision = TriageDecision(
        alert_id="ALERT002",
        disposition=Disposition.ESCALATE,
        rationale="Adversarial evidence-integrity test.",
        citations=[
            EvidenceCitation(
                transaction_id="TXN001",
                claim="Attempted use of an unrelated transaction.",
            )
        ],
        risk_score=0.8,
        requires_human_review=True,
    )

    valid, errors = validate_decision_citations(decision, store)

    assert valid is False
    assert any("different customer" in error for error in errors)
    assert any("not linked to alert" in error for error in errors)
