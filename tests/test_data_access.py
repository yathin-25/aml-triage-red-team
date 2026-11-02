import pytest

from aml_triage.data_access import AMLDataStore


@pytest.fixture
def store():
    return AMLDataStore()


def test_loads_expected_record_counts(store):
    assert len(store.customers) == 5
    assert len(store.transactions) == 15
    assert len(store.alert_records) == 5


def test_get_customer(store):
    customer = store.get_customer("CUST001")
    assert customer["customer_id"] == "CUST001"


def test_get_alert_transactions(store):
    transactions = store.get_transactions_for_alert("ALERT002")

    assert len(transactions) == 3
    assert all(tx.customer_id == "CUST002" for tx in transactions)


def test_unknown_alert_raises_error(store):
    with pytest.raises(KeyError):
        store.get_alert("UNKNOWN_ALERT")


def test_ground_truth_is_available(store):
    assert store.get_ground_truth("ALERT001") == "CLOSE"