# AML Triage Red-Team

A Python-based educational project for evaluating an Anti-Money Laundering (AML) alert triage workflow using synthetic transaction data, deterministic detection rules, evidence validation, and adversarial component tests.

## Project Overview

Financial institutions generate alerts that require investigation. This project demonstrates how a structured triage workflow can investigate synthetic alerts, identify configured suspicious transaction patterns, validate evidence references, and produce a structured decision.

The project also includes targeted adversarial checks to test selected detection and evidence-validation components.

**Important:** This is an educational prototype. It does not provide production-grade AML decisions, use official sanctions data, or replace qualified human investigation.

## Key Features

- **Structured outputs:** Pydantic models validate alerts, transactions, findings, and triage decisions.
- **Investigation workflow:** LangGraph organizes the triage process into explicit steps.
- **Transaction pattern detection:** Rules identify repeated similar transfers and rapid large transfers.
- **Fuzzy name matching:** RapidFuzz identifies potential name similarities against supplied reference names.
- **Evidence validation:** Checks whether cited transactions exist and are linked to the relevant alert and customer.
- **Baseline evaluation:** Calculates accuracy, precision, recall, F1 score, false-positive rate, false-negative rate, and citation validity rate.
- **Adversarial component evaluation:** Tests selected suspicious patterns, a fictional fuzzy-name match, benign activity, and unrelated evidence.
- **Automated tests:** Pytest verifies schemas, data access, detection rules, citations, triage behavior, and evaluation logic.
- **JSON reports:** Saves baseline and adversarial evaluation results for reproducibility.

## Technology Stack

- Python 3.12
- Pydantic
- LangGraph
- RapidFuzz
- Pytest

## Architecture

```text
Synthetic JSON Data
        |
        v
    AMLDataStore
        |
        v
  LangGraph Workflow
        |
        +--> Load alert, customer, transactions
        |
        +--> Run configured typology checks
        |
        +--> Generate structured triage decision
        |
        +--> Validate evidence references
        |
        v
   TriageDecision
        |
        v
 Baseline Evaluation
        |
        v
 reports/evaluation_report.json


Adversarial Scenario Definitions
        |
        v
 Adversarial Component Checks
        |
        +--> Repeated-transfer detection
        +--> Rapid-large-transfer detection
        +--> Fuzzy name matching
        +--> Benign pattern check
        +--> Unrelated-evidence rejection
        |
        v
 reports/adversarial_evaluation_report.json
```

The adversarial checks are component-level tests. They do not execute every scenario end-to-end through the LangGraph workflow.

## Project Structure

```text
aml-triage-red-team/
├── config/
│   └── settings.py
├── data/
│   ├── README.md
│   ├── synthetic/
│   │   ├── alerts.json
│   │   ├── customers.json
│   │   └── transactions.json
│   └── reference/
├── docs/
│   ├── architecture.md
│   ├── evaluation_methodology.md
│   └── limitations.md
├── reports/
│   ├── evaluation_report.json
│   └── adversarial_evaluation_report.json
├── scripts/
│   ├── generate_synthetic_data.py
│   └── run_evaluation.py
├── src/
│   └── aml_triage/
│       ├── adversarial_evaluation.py
│       ├── adversary_agent.py
│       ├── citations.py
│       ├── data_access.py
│       ├── evaluation.py
│       ├── sanctions.py
│       ├── schemas.py
│       ├── triage_agent.py
│       └── typologies.py
├── tests/
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.12
- Git
- PowerShell on Windows, or an equivalent terminal

### 1. Clone the repository

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd aml-triage-red-team
```

Replace the placeholder with your actual repository URL after publishing the project.

### 2. Create a virtual environment

```powershell
py -3.12 -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the Python import path

For PowerShell:

```powershell
$env:PYTHONPATH = "src"
```

Set this again when opening a new terminal unless you configure the project as an installable package.

### 5. Run the automated tests

```powershell
python -m pytest -v
```

### 6. Run both evaluation workflows

```powershell
python scripts/run_evaluation.py
```

This runs the baseline alert evaluation and the adversarial component evaluation.

## Evaluation

The baseline evaluator compares predicted dispositions against the synthetic ground-truth labels. `ESCALATE` is treated as the positive class for binary classification metrics.

The adversarial evaluator runs five targeted component checks:

1. Benign lookalike activity.
2. Rapid large transfers.
3. Ambiguous sanctions-style name matching using fictional names.
4. Repeated similar transfers.
5. Rejection of unrelated evidence references.

The current development run passed all five adversarial component checks. The baseline evaluation also achieved 100% accuracy on five synthetic alerts.

These results demonstrate behavior on the current test fixtures only. The dataset is too small to support claims about real-world AML effectiveness or generalization.

### Generated Reports

| File | Purpose |
|---|---|
| `reports/evaluation_report.json` | Baseline metrics and per-alert results |
| `reports/adversarial_evaluation_report.json` | Adversarial component results and limitations |

## Security and Limitations

- All included customer and transaction records are synthetic.
- The fuzzy-name test uses fictional reference names, not an official sanctions list.
- Fuzzy similarity is not proof of identity or a confirmed sanctions match.
- Citation validation checks structural relationships between alerts and transactions. It does not prove that a cited transaction semantically supports a claim.
- Detection rules are simplified educational examples and can produce false positives or false negatives.
- The adversarial suite currently performs targeted component checks rather than full end-to-end scenario execution.
- All triage decisions require human review.
- This project is not suitable for production compliance decisions.

## Future Improvements

- Integrate LangSmith tracing and experiment tracking.
- Add richer adversarial scenarios with independently constructed synthetic transaction datasets.
- Test end-to-end behavior across the full investigation graph.
- Evaluate semantic evidence support separately from citation integrity.
- Expand the synthetic dataset and measure performance across more diverse scenarios.
- Add continuous integration to run pytest on each pull request.
- Add stronger configuration and reproducibility controls.

## Disclaimer

This repository is intended for educational and research purposes. It is not legal, financial, or regulatory advice and must not be used to make real customer compliance decisions.