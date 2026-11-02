import json
from pathlib import Path

from aml_triage.schemas import AMLAlert, Transaction


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "synthetic"


class AMLDataStore:
    """Loads synthetic AML records and retrieves data for an alert."""

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = Path(data_dir)
        self.customers = self._load_json("customers.json")
        self.transactions = self._load_json("transactions.json")
        self.alert_records = self._load_json("alerts.json")

        self.transactions_by_id = {
            record["transaction_id"]: Transaction.model_validate(record)
            for record in self.transactions
        }

        self.customers_by_id = {
            customer["customer_id"]: customer
            for customer in self.customers
        }

        self.alerts_by_id = {
            record["alert_id"]: record
            for record in self.alert_records
        }

    def _load_json(self, filename: str) -> list[dict]:
        """Load a JSON file and return its list of records."""
        path = self.data_dir / filename

        if not path.exists():
            raise FileNotFoundError(f"Required data file not found: {path}")

        with path.open("r", encoding="utf-8") as file:
            records = json.load(file)

        if not isinstance(records, list):
            raise ValueError(f"Expected a JSON list in {path}")

        return records

    def get_customer(self, customer_id: str) -> dict:
        """Retrieve a customer by ID."""
        customer = self.customers_by_id.get(customer_id)

        if customer is None:
            raise KeyError(f"Unknown customer ID: {customer_id}")

        return customer

    def get_transaction(self, transaction_id: str) -> Transaction:
        """Retrieve a transaction by ID."""
        transaction = self.transactions_by_id.get(transaction_id)

        if transaction is None:
            raise KeyError(f"Unknown transaction ID: {transaction_id}")

        return transaction

    def get_alert(self, alert_id: str) -> AMLAlert:
        """Retrieve an alert and validate its input fields."""
        record = self.alerts_by_id.get(alert_id)

        if record is None:
            raise KeyError(f"Unknown alert ID: {alert_id}")

        return AMLAlert.model_validate(record)

    def get_transactions_for_alert(self, alert_id: str) -> list[Transaction]:
        """Return all transactions referenced by an alert."""
        alert = self.get_alert(alert_id)

        if alert.customer_id not in self.customers_by_id:
            raise ValueError(
                f"Alert {alert_id} references an unknown customer."
            )

        result = []

        for transaction_id in alert.transaction_ids:
            transaction = self.get_transaction(transaction_id)

            if transaction.customer_id != alert.customer_id:
                raise ValueError(
                    f"Transaction {transaction_id} does not belong "
                    f"to customer {alert.customer_id}."
                )

            result.append(transaction)

        return result

    def get_ground_truth(self, alert_id: str) -> str:
        """Return the synthetic evaluation label for an alert."""
        record = self.alerts_by_id.get(alert_id)

        if record is None:
            raise KeyError(f"Unknown alert ID: {alert_id}")

        return record["ground_truth"]