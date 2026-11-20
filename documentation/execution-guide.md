# Execution Guide - Lab 4

## Question 1: Disaster Recovery
To execute the automated disaster recovery simulation:
```bash
python question-1-disaster-recovery/scripts/disaster_simulation.py
```
This tests:
1. Baseline database initialization.
2. Checkpoint T0 automated snapshot creation.
3. Ingestion of live post-snapshot delta records.
4. Disaster injection (database corruption).
5. Automated restoration and integrity verification.
6. RTO and RPO calculation.

---

## Question 2: Automated Testing CI/CD
To run the automated test suite locally:
```bash
python question-2-automated-testing/run_tests.py
```
Or directly using Pytest:
```bash
pytest question-2-automated-testing/tests -v
```

In CI/CD, the workflow triggers automatically upon git push to the `main` branch.
