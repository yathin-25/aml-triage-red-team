from aml_triage.evaluation import evaluate_alerts


def test_evaluation_processes_all_synthetic_alerts():
    report = evaluate_alerts()

    assert report["total_alerts"] == 5
    assert report["successful_evaluations"] == 5
    assert report["failed_evaluations"] == 0


def test_evaluation_returns_expected_metrics():
    report = evaluate_alerts()

    expected_metrics = [
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "false_positive_rate",
        "false_negative_rate",
        "citation_validity_rate",
    ]

    for metric in expected_metrics:
        assert metric in report
        assert 0.0 <= report[metric] <= 1.0


def test_evaluation_results_include_each_alert():
    report = evaluate_alerts()

    alert_ids = {
        result["alert_id"]
        for result in report["results"]
    }

    assert alert_ids == {
        "ALERT001",
        "ALERT002",
        "ALERT003",
        "ALERT004",
        "ALERT005",
    }


def test_evaluation_checks_citation_validity():
    report = evaluate_alerts()

    assert report["citation_validity_rate"] == 1.0
    assert all(
        result["citation_valid"]
        for result in report["results"]
    )


def test_confusion_matrix_counts_all_successful_cases():
    report = evaluate_alerts()
    matrix = report["confusion_matrix"]

    total = (
        matrix["true_positive"]
        + matrix["true_negative"]
        + matrix["false_positive"]
        + matrix["false_negative"]
    )

    assert total == report["successful_evaluations"]