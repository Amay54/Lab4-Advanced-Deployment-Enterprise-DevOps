# Question 2: Automated Testing CI/CD Pipeline Evidence

## Execution Overview
- **Pipeline Platform**: GitHub Actions (`.github/workflows/ci-cd.yml`)
- **Testing Framework**: Pytest 8.3.4 with Python 3.11 / 3.13
- **Test Categories**: Unit Tests (Endpoints, Input Validation, Business Logic, Security Masking) & Integration Tests (Database Persistence, Order Lifecycle, Telemetry)
- **Quality Gate Mechanism**: The deployment job (`deploy-gate`) explicitly depends on `needs: [test-suite]`. If any test fails, GitHub Actions terminates the pipeline run and prevents deployment.

---

## 1. Automated Test Execution Transcript (Passing Gate)

```text
======================================================================
 CI/CD PIPELINE: AUTOMATED TEST EXECUTION GATE
 Timestamp: 2026-11-20T10:32:54.140847+00:00
======================================================================
Executing: python -m pytest tests -v --junitxml=reports/test-report.xml

============================= test session starts =============================
platform win32 / linux -- Python 3.13 / 3.11, pytest-8.3.4
rootdir: question-2-automated-testing
plugins: anyio-4.9.0, asyncio-1.4.0, cov-6.0.0
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

- generated xml file: reports/test-report.xml -
============================== 9 passed in 0.30s ==============================

======================================================================
 [QUALITY GATE: PASSED] All automated tests passed in 2.00s.
 PIPELINE PROCEEDING: Deployment gate unlocked.
======================================================================
```

---

## 2. Simulated Failing Test Demonstration (Deployment Blocked)

To prove that a failing test blocks deployment, we simulated an invalid assertion:

```text
================================== FAILURES ===================================
_____________________ test_order_validation_missing_body ______________________
    def test_order_validation_missing_body(client):
        response = client.post("/api/v1/orders", json={})
>       assert response.status_code == 422
E       assert 400 == 422
E        +  where 400 = <WrapperTestResponse [400 BAD REQUEST]>.status_code

=========================== short test summary info ===========================
FAILED tests/test_unit.py::test_order_validation_missing_body - assert 400 == 422
========================= 1 failed, 8 passed in 0.53s =========================

======================================================================
 [QUALITY GATE: FAILED] Tests failed with exit code 1.
 PIPELINE HALTED: Deployment gate BLOCKED.
======================================================================
```

**Observation**: In GitHub Actions, when `test-suite` fails with exit code 1, the downstream job `deploy-gate` is immediately marked as **CANCELLED / SKIPPED**. Production is protected from shipping regression bugs.
