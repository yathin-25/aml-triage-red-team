import pytest

from aml_triage.citations import validate_decision_citations
from aml_triage.data_access import AMLDataStore
from aml_triage.schemas import Disposition, TriageDecision
from aml_triage.triage_agent import investigate_alert


def test_investigation_returns_structured_decision():
    decision = investigate_alert("ALERT002")

    assert isinstance(decision, TriageDecision)
    assert decision.alert_id == "ALERT002"
    assert decision.disposition in Disposition
    assert 0.0 <= decision.risk_score <= 1.0


def test_investigation_has_evidence_citations():
    decision = investigate_alert("ALERT002")

    assert len(decision.citations) > 0
    assert all(citation.claim.strip() for citation in decision.citations)


def test_investigation_citations_are_valid():
    store = AMLDataStore()
    decision = investigate_alert("ALERT002", store)

    valid, errors = validate_decision_citations(decision, store)

    assert valid is True, errors


def test_investigation_requires_human_review():
    decision = investigate_alert("ALERT001")

    assert decision.requires_human_review is True


def test_unknown_alert_is_rejected():
    with pytest.raises(KeyError):
        investigate_alert("ALERT-UNKNOWN")


def test_suspicious_alert_is_escalated():
    decision = investigate_alert("ALERT002")

    assert decision.disposition == Disposition.ESCALATE
    assert decision.requires_human_review is True
    assert decision.risk_score > 0.0


def test_high_risk_alert_is_escalated():
    decision = investigate_alert("ALERT003")

    assert decision.disposition == Disposition.ESCALATE
    assert decision.requires_human_review is True
    assert decision.risk_score >= 0.8
