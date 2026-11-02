import json
from pathlib import Path

from aml_triage.evaluation import evaluate_alerts
from aml_triage.adversarial_evaluation import run_adversarial_evaluation


def save_report(report: dict, path: Path) -> None:
    """Save an evaluation report as formatted JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run baseline evaluation
    baseline = evaluate_alerts()
    baseline_path = reports_dir / "evaluation_report.json"
    save_report(baseline, baseline_path)

    print("\n=== BASELINE AML TRIAGE EVALUATION ===")
    print(f"Total alerts: {baseline['total_alerts']}")
    print(f"Successful evaluations: {baseline['successful_evaluations']}")
    print(f"Failed evaluations: {baseline['failed_evaluations']}")
    print(f"Accuracy: {baseline['accuracy']:.2%}")
    print(f"Precision: {baseline['precision']:.2%}")
    print(f"Recall: {baseline['recall']:.2%}")
    print(f"F1 score: {baseline['f1_score']:.2%}")
    print(
        "Citation validity rate: "
        f"{baseline['citation_validity_rate']:.2%}"
    )
    print(f"Report saved to: {baseline_path}")

    # 2. Run adversarial component evaluation
    adversarial = run_adversarial_evaluation()
    adversarial_path = (
        reports_dir / "adversarial_evaluation_report.json"
    )
    save_report(adversarial, adversarial_path)

    print("\n=== ADVERSARIAL COMPONENT EVALUATION ===")
    print(f"Total cases: {adversarial['total_cases']}")
    print(f"Passed cases: {adversarial['passed_cases']}")
    print(f"Failed cases: {adversarial['failed_cases']}")
    print(f"Pass rate: {adversarial['pass_rate']:.2%}")

    for result in adversarial["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"  [{status}] {result['case_id']} - "
            f"{result['scenario']}"
        )

    print(f"Report saved to: {adversarial_path}")

    # 3. Summarize execution status
    print("\n=== EVALUATION RUN SUMMARY ===")

    baseline_ok = (
        baseline["failed_evaluations"] == 0
        and baseline["total_alerts"] > 0
    )
    adversarial_ok = adversarial["failed_cases"] == 0

    print(f"Baseline execution successful: {baseline_ok}")
    print(f"Adversarial checks successful: {adversarial_ok}")

    if not baseline_ok or not adversarial_ok:
        raise SystemExit(
            "One or more evaluation checks failed. "
            "Inspect the generated JSON reports."
        )

    print("\nEvaluation workflows completed successfully.")


if __name__ == "__main__":
    main()