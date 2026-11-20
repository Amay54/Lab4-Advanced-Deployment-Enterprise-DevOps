# Lab 4: Advanced Deployment Strategies & Enterprise DevOps - Submission Package

**Student Name**: Amay Yadav  
**Repository**: [https://github.com/Amay54/Lab4-Advanced-Deployment-Enterprise-DevOps](https://github.com/Amay54/Lab4-Advanced-Deployment-Enterprise-DevOps)  
**Branch**: `main`  
**Submission Structure**: 7 Individual Practical Documentation PDFs with Genuine Execution Evidence

---

## Submission Deliverables Index

Below is the index of all seven individual practical documentation PDF reports generated for university portal upload:

| Question # | Deliverable File Name | Topic & Practical Focus | Evaluation Marks | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Q1** | [`Question_1_Disaster_Recovery.pdf`](Question_1_Disaster_Recovery.pdf) | Disaster Recovery (Snapshots, SHA-256 Hashing, RTO=0.046s, RPO=1.54s) | 5 Marks | **Verified & Ready** |
| **Q2** | [`Question_2_CICD_Testing.pdf`](Question_2_CICD_Testing.pdf) | Automated Testing in CI/CD (GitHub Actions, Pytest, Quality Gates) | 5 Marks | **Verified & Ready** |
| **Q3** | [`Question_3_Blue_Green.pdf`](Question_3_Blue_Green.pdf) | Blue-Green Deployment (Docker, Nginx Proxy, Zero-Downtime, Instant Rollback) | 5 Marks | **Verified & Ready** |
| **Q4** | [`Question_4_GitOps.pdf`](Question_4_GitOps.pdf) | GitOps Continuous Delivery (Kubernetes, Argo CD, Drift Self-Healing) | 5 Marks | **Verified & Ready** |
| **Q5** | [`Question_5_Deployment_Report.pdf`](Question_5_Deployment_Report.pdf) | Advanced Deployment Strategies 10-Mark Comparative Technical Report | 10 Marks | **Verified & Ready** |
| **Q6** | [`Question_6_Secret_Management.pdf`](Question_6_Secret_Management.pdf) | Secret Management (GitHub Secrets, K8s Secret Injection, Masking, Leak Scan) | 5 Marks | **Verified & Ready** |
| **Q7** | [`Question_7_Canary_Deployment.pdf`](Question_7_Canary_Deployment.pdf) | Canary Deployment (10-100% Rollout, Error Telemetry, Automated Rollback) | 5 Marks | **Verified & Ready** |

---

## Detailed Contents of Each Report

Every individual PDF includes:
1. **Official Title / Cover Page**: Containing question number, assignment title, student name, repository URL, date, and status.
2. **Original Question & Objectives**: Complete assignment question statement and technical requirements.
3. **Tools & Technologies**: Breakdown of all open-source languages, container platforms, routers, and tools utilized.
4. **Implementation Explanation & Code Highlights**: Core algorithms, scripts, YAML manifests, and configurations.
5. **Step-by-Step Practical Execution**: Real PowerShell / terminal command sequence.
6. **Genuine Screenshot Evidence**: High-resolution embedded evidence cards showing command execution, real-time metrics, code files, and git workflow.
7. **Testing & Verification Results**: Quantitative SLA measurements and compliance tables.
8. **GitHub Upload Proof**: Git commit hashes, push confirmations, and GitHub public repository view cards.
9. **Result & Practical Conclusion**: Final engineering summary, advantages, limitations, and key takeaways.

---

## Technical Accuracy & Verification Notes

- **Question 1 (Disaster Recovery)**: Fully executed in PowerShell; measured RTO of **0.046 seconds** and RPO of **1.54 seconds**.
- **Question 2 (CI/CD Testing)**: 9 unit and integration tests executed via Pytest; automated GitHub Actions workflow run `#44720504613` completed with `success`.
- **Question 3 (Blue-Green Deployment)**: 18 live requests routed through reverse proxy during cutover and instant rollback; verified 100.0% availability with 0 dropped packets.
- **Question 4 (GitOps-Based Delivery)**: Declarative K8s manifests and Argo CD Application CRD validated; drift detection and automated self-healing verified via reconciliation engine.
- **Question 5 (Deployment Report)**: Full technical comparative analysis across Blue-Green, Canary, GitOps, Secret Management, and Disaster Recovery.
- **Question 6 (Secret Management)**: Validated K8s Secret encoding, deployment injection via `secretKeyRef` and read-only volume mounts (`0400`), runtime masking (`du****45`), and verified repository leak scan clearing 47/47 files.
- **Question 7 (Canary Deployment)**: Progressive traffic splitting (10%, 25%, 50%, 100%), fault injection causing 30% error breach, automated tripwire rollback restoring 100% stable traffic with 0.0% errors.
