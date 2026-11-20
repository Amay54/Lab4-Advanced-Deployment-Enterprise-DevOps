# Lab 4: Advanced Deployment Strategies & Enterprise DevOps

**Author / Student**: Amay Yadav  
**Repository**: [Lab4-Advanced-Deployment-Enterprise-DevOps](https://github.com/Amay54/Lab4-Advanced-Deployment-Enterprise-DevOps)  
**Status**: Practical-based implementations and automated verification across all 7 assignment questions.

---

## Repository Overview

This repository contains practical implementations, scripts, configurations, test suites, and documentation for **Lab 4: Advanced Deployment Strategies & Enterprise DevOps**.

Each question is structured into a dedicated folder containing executable code, test scripts, architectural summaries, and verification logs.

| Question | Topic | Marks | Implementation Status |
| :--- | :--- | :--- | :--- |
| **Question 1** | **Disaster Recovery Mechanism** (Backup, Restore, RTO & RPO) | 5 | **Completed & Verified** |
| **Question 2** | **Automated Testing Within CI/CD Pipeline** (GitHub Actions, Pytest) | 5 | **Completed & Verified** |
| **Question 3** | **Blue-Green Deployment Strategy** (Zero Downtime, Traffic Switch) | 5 | *Folder Structured & Prepared* |
| **Question 4** | **GitOps-Based Delivery** (Argo CD, Declarative Sync) | 5 | *Folder Structured & Prepared* |
| **Question 5** | **Advanced Deployment Strategies Comprehensive Report** | 10 | *Folder Structured & Prepared* |
| **Question 6** | **Secret Management for Pipeline and Deployments** (Vault, K8s) | 5 | *Folder Structured & Prepared* |
| **Question 7** | **Canary Deployment Strategy** (Traffic Splitting, Rollback Triggers) | 5 | *Folder Structured & Prepared* |

---

## Directory Structure

```
Lab4-Advanced-Deployment-Enterprise-DevOps/
├── .github/
│   └── workflows/
│       └── ci-cd.yml                     # Master GitHub Actions CI/CD pipeline
├── question-1-disaster-recovery/
│   ├── backups/                          # Snapshot archives and manifests
│   ├── configs/                          # Backup policy configuration
│   ├── data/                             # Production SQLite database & files
│   ├── evidence/                         # Execution logs & verification JSON
│   ├── scripts/
│   │   ├── backup.py                     # Consistent backup generator
│   │   ├── restore.py                    # Recovery engine
│   │   └── disaster_simulation.py        # End-to-end failure simulation
│   └── README.md                         # Detailed documentation for Q1
├── question-2-automated-testing/
│   ├── app/                              # Flask application & Dockerfile
│   ├── tests/                            # Pytest unit and integration tests
│   ├── reports/                          # Test execution reports
│   ├── evidence/                         # Test output & gating evidence
│   ├── run_tests.py                      # Local automated test runner
│   └── README.md                         # Detailed documentation for Q2
├── question-3-blue-green/                # Blue-Green deployment manifests & scripts
├── question-4-gitops/                    # GitOps (Argo CD) manifests & scripts
├── question-5-deployment-report/         # Comparative report sources and diagrams
├── question-6-secret-management/         # Secret handling & Vault/K8s manifests
├── question-7-canary-deployment/         # Canary deployment & traffic splitting
├── shared/                               # Shared application & docker assets
├── documentation/                        # Setup, execution, and troubleshooting guides
└── submission/                           # Final compiled assignment reports
```

---

## Quick Start & Verification

### Question 1: Disaster Recovery
```bash
python question-1-disaster-recovery/scripts/disaster_simulation.py
```
*Result: Automatically creates baseline data, snapshot backup, triggers database corruption, executes restore, and calculates RTO (0.046s) and RPO (1.54s).*

### Question 2: Automated Testing CI/CD
```bash
python question-2-automated-testing/run_tests.py
```
*Result: Runs 9 Pytest unit and integration tests. All 9 pass. The CI gate verifies that tests must pass before the deployment step proceeds in GitHub Actions.*

---

## CI/CD Pipeline
Continuous Integration and Quality Gating are powered by **GitHub Actions** (`.github/workflows/ci-cd.yml`). Every push to `main` executes the automated test suite on Ubuntu runners, publishes test artifact reports, and guards downstream deployments.
