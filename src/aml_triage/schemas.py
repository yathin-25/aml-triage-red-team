
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Disposition(str, Enum):
    """Permitted outcomes of an AML triage investigation."""

    CLOSE = "CLOSE"
    ESCALATE = "ESCALATE"
    DRAFT_SAR = "DRAFT_SAR"


class Transaction(BaseModel):
    """A single transaction associated with a customer."""

    transaction_id: str
    customer_id: str
    counterparty_name: str
    amount: float = Field(gt=0)
    currency: str = "USD"
    timestamp: str
    transaction_type: str


class AMLAlert(BaseModel):
    """An AML alert submitted for investigation."""

    alert_id: str
    customer_id: str
    alert_type: str
    description: str
    transaction_ids: list[str] = Field(min_length=1)


class EvidenceCitation(BaseModel):
    """A reference to evidence supporting an investigation claim."""

    transaction_id: str
    claim: str


class TriageDecision(BaseModel):
    """Structured output produced by the AML triage agent."""

    alert_id: str
    disposition: Disposition
    rationale: str
    citations: list[EvidenceCitation] = Field(default_factory=list)
    risk_score: float = Field(ge=0.0, le=1.0)
    requires_human_review: bool = True


class InvestigationFinding(BaseModel):
    """A finding produced by a deterministic investigation tool."""

    finding_type: str
    description: str
    transaction_ids: list[str] = Field(default_factory=list)
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    confidence: float = Field(ge=0.0, le=1.0)
