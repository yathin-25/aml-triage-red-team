from aml_triage.adversarial_evaluation import (
    run_adversarial_evaluation,
)


def test_adversarial_evaluation_processes_all_scenarios():
    report = run_adversarial_evaluation()

    assert report["total_cases"] == 5
    assert len(report["results"]) == 5


def test_adversarial_evaluation_has_no_failures():
    report = run_adversarial_evaluation()

    assert report["failed_cases"] == 0
    assert report["passed_cases"] == 5


def test_adversarial_evaluation_pass_rate_is_valid():
    report = run_adversarial_evaluation()

    assert 0.0 <= report["pass_rate"] <= 1.0


def test_every_adversarial_result_has_required_fields():
    report = run_adversarial_evaluation()

    required_fields = {
        "case_id",
        "scenario",
        "expected_disposition",
        "observed",
        "passed",
        "error",
        "test_scope",
    }

    for result in report["results"]:
        assert required_fields.issubset(result.keys())


def test_adversarial_evaluation_uses_synthetic_data():
    report = run_adversarial_evaluation()

    assert report["synthetic_data_only"] is True
    assert all(
        result["test_scope"] == "component-level"
        for result in report["results"]
    )