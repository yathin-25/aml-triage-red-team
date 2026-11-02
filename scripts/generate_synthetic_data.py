import json
from pathlib import Path

OUTPUT_DIR = Path("data/synthetic")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

customers = [
    {
        "customer_id": "CUST001",
        "name": "Aarav Example",
        "occupation": "Software Engineer",
        "risk_rating": "LOW",
        "country": "US",
    },
    {
        "customer_id": "CUST002",
        "name": "Mira Sample",
        "occupation": "Small Business Owner",
        "risk_rating": "MEDIUM",
        "country": "US",
    },
    {
        "customer_id": "CUST003",
        "name": "Dev Fictional",
        "occupation": "Import Export Trader",
        "risk_rating": "HIGH",
        "country": "US",
    },
    {
        "customer_id": "CUST004",
        "name": "Tara Demo",
        "occupation": "Consultant",
        "risk_rating": "LOW",
        "country": "US",
    },
    {
        "customer_id": "CUST005",
        "name": "Noah Test",
        "occupation": "Retail Business Owner",
        "risk_rating": "MEDIUM",
        "country": "US",
    },
]

transactions = [
    {
        "transaction_id": "TXN001",
        "customer_id": "CUST001",
        "counterparty_name": "Example Grocery",
        "amount": 85.50,
        "currency": "USD",
        "timestamp": "2026-10-01T09:00:00Z",
        "transaction_type": "CARD_PAYMENT",
    },
    {
        "transaction_id": "TXN002",
        "customer_id": "CUST001",
        "counterparty_name": "Example Utilities",
        "amount": 120.00,
        "currency": "USD",
        "timestamp": "2026-10-02T10:00:00Z",
        "transaction_type": "BILL_PAYMENT",
    },
    {
        "transaction_id": "TXN003",
        "customer_id": "CUST001",
        "counterparty_name": "Example Salary Services",
        "amount": 3200.00,
        "currency": "USD",
        "timestamp": "2026-10-03T08:00:00Z",
        "transaction_type": "SALARY",
    },
    {
        "transaction_id": "TXN004",
        "customer_id": "CUST002",
        "counterparty_name": "Sample Electronics",
        "amount": 9800.00,
        "currency": "USD",
        "timestamp": "2026-10-04T11:00:00Z",
        "transaction_type": "WIRE",
    },
    {
        "transaction_id": "TXN005",
        "customer_id": "CUST002",
        "counterparty_name": "Sample Electronics",
        "amount": 9700.00,
        "currency": "USD",
        "timestamp": "2026-10-04T13:00:00Z",
        "transaction_type": "WIRE",
    },
    {
        "transaction_id": "TXN006",
        "customer_id": "CUST002",
        "counterparty_name": "Sample Electronics",
        "amount": 9600.00,
        "currency": "USD",
        "timestamp": "2026-10-04T15:00:00Z",
        "transaction_type": "WIRE",
    },
    {
        "transaction_id": "TXN007",
        "customer_id": "CUST003",
        "counterparty_name": "Fictional Overseas Trading",
        "amount": 25000.00,
        "currency": "USD",
        "timestamp": "2026-10-05T09:00:00Z",
        "transaction_type": "WIRE",
    },
    {
        "transaction_id": "TXN008",
        "customer_id": "CUST003",
        "counterparty_name": "Fictional Overseas Trading",
        "amount": 24800.00,
        "currency": "USD",
        "timestamp": "2026-10-05T09:30:00Z",
        "transaction_type": "WIRE",
    },
    {
        "transaction_id": "TXN009",
        "customer_id": "CUST003",
        "counterparty_name": "Demo International Services",
        "amount": 49000.00,
        "currency": "USD",
        "timestamp": "2026-10-05T10:00:00Z",
        "transaction_type": "WIRE",
    },
    {
        "transaction_id": "TXN010",
        "customer_id": "CUST004",
        "counterparty_name": "Demo Office Supplies",
        "amount": 240.00,
        "currency": "USD",
        "timestamp": "2026-10-06T12:00:00Z",
        "transaction_type": "CARD_PAYMENT",
    },
    {
        "transaction_id": "TXN011",
        "customer_id": "CUST004",
        "counterparty_name": "Demo Internet Services",
        "amount": 75.00,
        "currency": "USD",
        "timestamp": "2026-10-07T12:00:00Z",
        "transaction_type": "BILL_PAYMENT",
    },
    {
        "transaction_id": "TXN012",
        "customer_id": "CUST005",
        "counterparty_name": "Test Wholesale Market",
        "amount": 12000.00,
        "currency": "USD",
        "timestamp": "2026-10-08T08:00:00Z",
        "transaction_type": "WIRE",
    },
    {
        "transaction_id": "TXN013",
        "customer_id": "CUST005",
        "counterparty_name": "Test Wholesale Market",
        "amount": 11800.00,
        "currency": "USD",
        "timestamp": "2026-10-08T09:00:00Z",
        "transaction_type": "WIRE",
    },
    {
        "transaction_id": "TXN014",
        "customer_id": "CUST005",
        "counterparty_name": "Test Wholesale Market",
        "amount": 11600.00,
        "currency": "USD",
        "timestamp": "2026-10-08T10:00:00Z",
        "transaction_type": "WIRE",
    },
    {
        "transaction_id": "TXN015",
        "customer_id": "CUST005",
        "counterparty_name": "Example Community Charity",
        "amount": 500.00,
        "currency": "USD",
        "timestamp": "2026-10-09T10:00:00Z",
        "transaction_type": "DONATION",
    },
]

alerts = [
    {
        "alert_id": "ALERT001",
        "customer_id": "CUST001",
        "alert_type": "UNUSUAL_ACTIVITY",
        "description": "Routine activity selected for review.",
        "transaction_ids": ["TXN001", "TXN002", "TXN003"],
        "ground_truth": "CLOSE",
        "adversarial_technique": "BENIGN_CONTROL",
    },
    {
        "alert_id": "ALERT002",
        "customer_id": "CUST002",
        "alert_type": "STRUCTURING",
        "description": "Multiple similar transfers occurred within a short period.",
        "transaction_ids": ["TXN004", "TXN005", "TXN006"],
        "ground_truth": "ESCALATE",
        "adversarial_technique": "THRESHOLD_HUGGING",
    },
    {
        "alert_id": "ALERT003",
        "customer_id": "CUST003",
        "alert_type": "RAPID_MOVEMENT",
        "description": "Large transfers were followed by another substantial transfer.",
        "transaction_ids": ["TXN007", "TXN008", "TXN009"],
        "ground_truth": "ESCALATE",
        "adversarial_technique": "RAPID_MOVEMENT",
    },
    {
        "alert_id": "ALERT004",
        "customer_id": "CUST004",
        "alert_type": "UNUSUAL_ACTIVITY",
        "description": "Small routine payments with no clear suspicious pattern.",
        "transaction_ids": ["TXN010", "TXN011"],
        "ground_truth": "CLOSE",
        "adversarial_technique": "BENIGN_CONTROL",
    },
    {
        "alert_id": "ALERT005",
        "customer_id": "CUST005",
        "alert_type": "STRUCTURING",
        "description": "Repeated transfers may warrant closer review.",
        "transaction_ids": ["TXN012", "TXN013", "TXN014", "TXN015"],
        "ground_truth": "ESCALATE",
        "adversarial_technique": "REPEATED_TRANSFERS",
    },
]

datasets = {
    "customers.json": customers,
    "transactions.json": transactions,
    "alerts.json": alerts,
}

for filename, records in datasets.items():
    output_path = OUTPUT_DIR / filename
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)

print(f"Created {len(customers)} customers.")
print(f"Created {len(transactions)} transactions.")
print(f"Created {len(alerts)} alerts.")
print(f"Output directory: {OUTPUT_DIR.resolve()}")