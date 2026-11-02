from collections import defaultdict
from datetime import datetime, timezone

from aml_triage.schemas import InvestigationFinding, Transaction


def _parse_timestamp(value: str) -> datetime:
    """Parse an ISO-8601 timestamp and normalize it to UTC."""
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def detect_repeated_similar_transfers(
    transactions: list[Transaction],
    minimum_count: int = 3,
    amount_tolerance: float = 0.10,
    window_hours: float = 24,
) -> list[InvestigationFinding]:
    """Flag clusters of similar outgoing transfers within a time window.

    This is a screening indicator, not a determination of structuring.
    """
    if minimum_count < 2:
        raise ValueError("minimum_count must be at least 2")

    if not 0 <= amount_tolerance < 1:
        raise ValueError("amount_tolerance must be in [0, 1)")

    if window_hours <= 0:
        raise ValueError("window_hours must be positive")

    grouped = defaultdict(list)

    for transaction in transactions:
        grouped[(transaction.customer_id, transaction.currency)].append(
            transaction
        )

    findings = []

    for group in grouped.values():
        ordered = sorted(group, key=lambda tx: _parse_timestamp(tx.timestamp))

        for start_index, first in enumerate(ordered):
            cluster = [first]
            first_time = _parse_timestamp(first.timestamp)

            for candidate in ordered[start_index + 1:]:
                elapsed = (
                    _parse_timestamp(candidate.timestamp) - first_time
                ).total_seconds() / 3600

                if elapsed > window_hours:
                    break

                relative_difference = (
                    abs(candidate.amount - first.amount) / first.amount
                )

                if relative_difference <= amount_tolerance:
                    cluster.append(candidate)

            if len(cluster) >= minimum_count:
                findings.append(
                    InvestigationFinding(
                        finding_type="REPEATED_SIMILAR_TRANSFERS",
                        description=(
                            f"{len(cluster)} transactions have similar "
                            f"amounts within {window_hours} hours."
                        ),
                        transaction_ids=[
                            tx.transaction_id for tx in cluster
                        ],
                        severity="MEDIUM",
                        confidence=0.70,
                    )
                )
                break

    return findings


def detect_rapid_large_transfers(
    transactions: list[Transaction],
    minimum_amount: float = 20000,
    window_hours: float = 2,
    minimum_count: int = 2,
) -> list[InvestigationFinding]:
    """Flag multiple large transfers occurring within a short window."""
    if minimum_amount <= 0:
        raise ValueError("minimum_amount must be positive")

    if window_hours <= 0:
        raise ValueError("window_hours must be positive")

    if minimum_count < 2:
        raise ValueError("minimum_count must be at least 2")

    grouped = defaultdict(list)

    for transaction in transactions:
        if transaction.amount >= minimum_amount:
            grouped[(transaction.customer_id, transaction.currency)].append(
                transaction
            )

    findings = []

    for group in grouped.values():
        ordered = sorted(group, key=lambda tx: _parse_timestamp(tx.timestamp))

        for start_index, first in enumerate(ordered):
            first_time = _parse_timestamp(first.timestamp)

            cluster = [
                candidate
                for candidate in ordered[start_index:]
                if (
                    _parse_timestamp(candidate.timestamp) - first_time
                ).total_seconds() / 3600 <= window_hours
            ]

            if len(cluster) >= minimum_count:
                findings.append(
                    InvestigationFinding(
                        finding_type="RAPID_LARGE_TRANSFERS",
                        description=(
                            f"{len(cluster)} large transfers occurred "
                            f"within {window_hours} hours."
                        ),
                        transaction_ids=[
                            tx.transaction_id for tx in cluster
                        ],
                        severity="HIGH",
                        confidence=0.80,
                    )
                )
                break

    return findings


def detect_high_risk_customer(
    customer: dict,
    transactions: list[Transaction],
) -> list[InvestigationFinding]:
    """Flag activity associated with a high-risk synthetic customer."""
    if not transactions:
        return []

    if customer.get("risk_rating") != "HIGH":
        return []

    return [
        InvestigationFinding(
            finding_type="HIGH_RISK_CUSTOMER_ACTIVITY",
            description=(
                "Transactions belong to a customer marked HIGH risk "
                "in the synthetic profile."
            ),
            transaction_ids=[
                tx.transaction_id for tx in transactions
            ],
            severity="MEDIUM",
            confidence=0.60,
        )
    ]


def run_all_typology_checks(
    transactions: list[Transaction],
    customer: dict,
) -> list[InvestigationFinding]:
    """Run the initial deterministic typology checks."""
    findings = []

    findings.extend(detect_repeated_similar_transfers(transactions))
    findings.extend(detect_rapid_large_transfers(transactions))
    findings.extend(detect_high_risk_customer(customer, transactions))

    return findings