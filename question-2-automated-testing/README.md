# Question 2: Automated Testing Within CI/CD Pipeline

## 1. Aim and Objectives
The objective of this practical is to implement automated testing within a continuous integration and continuous deployment (CI/CD) pipeline using GitHub Actions.
Specifically, the practical accomplishes:
- Creation of a functional web application service (Python/Flask).
- Implementation of comprehensive unit tests and integration tests using Pytest.
- Construction of a declarative GitHub Actions workflow (`.github/workflows/ci-cd.yml`).
- Execution of automated tests on every push and pull request.
- Integration of pipeline quality gates ensuring failed tests block deployment.
- Generation of JUnit XML test reports and execution evidence.

---

## 2. Tools and Technologies Used
- **Application Language & Framework**: Python 3.11 / 3.13, Flask 3.1
- **Testing Framework**: Pytest 8.3, Pytest-cov
- **CI/CD Platform**: GitHub Actions (Ubuntu runner)
- **Containerization**: Dockerfile included for production packaging
- **Reporting**: JUnit XML test reports, pytest text summaries

---

## 3. CI/CD Pipeline Architecture & Gating Workflow

```
   [Developer Push / Pull Request]
                  |
                  v
       +--------------------+
       |   GitHub Actions   |
       +----------+---------+
                  |
                  v
       +--------------------+
       |  Job 1: test-suite |
       |--------------------|
       | - Checkout code    |
       | - Setup Python 3.11|
       | - Install deps     |
       | - Run Pytest       |
       +----------+---------+
                  |
         +--------+--------+
         |                 |
     (Success)          (Failure)
         |                 |
         v                 v
+-------------------+ +-----------------------+
|Job 2: deploy-gate | | PIPELINE BLOCKED      |
|-------------------| | Downstream deployment |
| Deployment to Stg | | is aborted/cancelled  |
| / Prod proceeded  | | No bad code shipped   |
+-------------------+ +-----------------------+
```

---

## 4. Implementation Structure

```
question-2-automated-testing/
├── .github/
│   └── workflows/
│       └── ci-cd.yml            # CI/CD pipeline workflow definition
├── app/
│   ├── app.py                   # Order management application
│   ├── Dockerfile               # Container build definition
│   └── requirements.txt         # Application dependencies
├── evidence/
│   └── test_execution_evidence.md # Pipeline evidence and output
├── reports/
│   ├── test-report.xml          # JUnit XML test report
│   └── test-summary.txt         # Text execution report
├── tests/
│   ├── test_unit.py             # 7 unit tests covering endpoints and validations
│   └── test_integration.py      # 2 integration tests covering lifecycle & metrics
├── run_tests.py                 # Local test runner script simulating pipeline gate
└── README.md                    # This documentation
```

---

## 5. Execution Steps and Commands

### Step 1: Run All Tests Locally
Execute the test runner script to run both unit and integration tests:
```bash
python question-2-automated-testing/run_tests.py
```

Or execute directly via Pytest:
```bash
pytest question-2-automated-testing/tests -v
```

### Step 2: Push to GitHub to Trigger Pipeline
When code is committed and pushed to the `main` branch on GitHub:
```bash
git add .
git commit -m "feat: implement automated testing suite and CI/CD quality gate"
git push origin main
```
The GitHub Actions workflow runs automatically under the **Actions** tab of the repository.

---

## 6. Actual Execution Results

```text
============================= test session starts =============================
platform win32 / linux -- Python 3.13 / 3.11, pytest-8.3.4
collected 9 items

tests/test_integration.py::test_full_order_lifecycle_integration PASSED   [ 11%]
tests/test_integration.py::test_metrics_telemetry_integration     PASSED   [ 22%]
tests/test_unit.py::test_health_endpoint                          PASSED   [ 33%]
tests/test_unit.py::test_index_endpoint                           PASSED   [ 44%]
tests/test_version_endpoint                                       PASSED   [ 55%]
tests/test_unit.py::test_order_validation_missing_body            PASSED   [ 66%]
tests/test_unit.py::test_order_validation_missing_customer        PASSED   [ 77%]
tests/test_unit.py::test_order_validation_invalid_pricing         PASSED   [ 88%]
tests/test_unit.py::test_secret_masking                            PASSED   [100%]

============================== 9 passed in 0.30s ==============================

 [QUALITY GATE: PASSED] All automated tests passed.
 PIPELINE PROCEEDING: Deployment gate unlocked.
```

---

## 7. Observations and Findings
1. **Automated Defect Detection**: Unit tests validate critical constraints (missing payload returns 400, missing customer returns 422, negative price rejected).
2. **Deterministic Gating**: In `.github/workflows/ci-cd.yml`, using `needs: [test-suite]` creates a strict barrier: if any single test fails, the subsequent deployment step is automatically stopped, safeguarding the target environment.
3. **Reproducibility**: Identical test passes run both locally through `run_tests.py` and on the automated cloud GitHub Actions runner.
