from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END

from aml_triage.citations import validate_decision_citations
from aml_triage.data_access import AMLDataStore
from aml_triage.schemas import (
    Disposition,
    EvidenceCitation,
    TriageDecision,
    Transaction,
)
from aml_triage.typologies import run_all_typology_checks


class InvestigationState(TypedDict, total=False):
    alert_id: str
    customer: dict[str, Any]
    transactions: list[dict[str, Any]]
    findings: list[dict[str, Any]]
    decision: TriageDecision
    citation_valid: bool
    citation_errors: list[str]


def build_investigation_graph(store: AMLDataStore | None = None):
    """Build a deterministic LangGraph investigation workflow."""
    data_store = store if store is not None else AMLDataStore()

    def load_data(state: InvestigationState) -> dict:
        alert = data_store.get_alert(state["alert_id"])
        customer = data_store.get_customer(alert.customer_id)
        transactions = data_store.get_transactions_for_alert(alert.alert_id)

        return {
            "customer": customer,
            "transactions": [
                tx.model_dump() if hasattr(tx, "model_dump") else tx
                for tx in transactions
            ],
        }

    def run_screening(state: InvestigationState) -> dict:
        transactions = [
            Transaction.model_validate(item)
            for item in state["transactions"]
        ]

        findings = run_all_typology_checks(
            transactions,
            state["customer"],
        )

        return {
            "findings": [
                finding.model_dump()
                if hasattr(finding, "model_dump")
                else finding
                for finding in findings
            ]
        }

    def make_decision(state: InvestigationState) -> dict:
        transactions = state["transactions"]
        findings = state["findings"]

        citations = [
            EvidenceCitation(
                transaction_id=tx["transaction_id"],
                claim=(
                    f"Transaction amount: {tx['amount']} {tx['currency']}; "
                    f"counterparty: {tx['counterparty_name']}."
                ),
            )
            for tx in transactions
        ]

        if findings:
            disposition = Disposition.ESCALATE
            rationale = (
                "Deterministic screening produced one or more findings. "
                "Refer this synthetic case for human compliance review."
            )
            risk_score = max(
                finding["confidence"] for finding in findings
            )
        else:
            disposition = Disposition.CLOSE
            rationale = (
                "No configured typology rules produced findings. "
                "This does not establish that the activity is risk-free."
            )
            risk_score = 0.1

        decision = TriageDecision(
            alert_id=state["alert_id"],
            disposition=disposition,
            rationale=rationale,
            citations=citations,
            risk_score=risk_score,
            requires_human_review=True,
        )

        return {"decision": decision}

    def validate_evidence(state: InvestigationState) -> dict:
        valid, errors = validate_decision_citations(
            state["decision"],
            data_store,
        )

        return {
            "citation_valid": valid,
            "citation_errors": errors,
        }

    graph = StateGraph(InvestigationState)

    graph.add_node("load_data", load_data)
    graph.add_node("run_screening", run_screening)
    graph.add_node("make_decision", make_decision)
    graph.add_node("validate_evidence", validate_evidence)

    graph.add_edge(START, "load_data")
    graph.add_edge("load_data", "run_screening")
    graph.add_edge("run_screening", "make_decision")
    graph.add_edge("make_decision", "validate_evidence")
    graph.add_edge("validate_evidence", END)

    return graph.compile()


def investigate_alert(
    alert_id: str,
    store: AMLDataStore | None = None,
) -> TriageDecision:
    """Run the investigation workflow and return its decision."""
    graph = build_investigation_graph(store)
    result = graph.invoke({"alert_id": alert_id})

    if not result.get("citation_valid", False):
        raise ValueError(
            f"Evidence validation failed: {result.get('citation_errors', [])}"
        )

    return result["decision"]