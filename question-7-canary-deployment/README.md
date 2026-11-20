# Question 7: Canary Deployment Strategy

## 1. Aim and Objectives
The objective of this practical is to design, implement, and verify a **Canary Deployment Strategy** to incrementally roll out new application releases to a subset of users, monitor error telemetry, and trigger automated rollbacks if health metrics degrade.

Specifically, this practical accomplishes:
- Deployment of a **Stable** release (v1.0.0, port 8081) and a **Canary** candidate release (v2.0.0, port 8082).
- Configuring weighted traffic splitting across discrete stages: **10%**, **25%**, **50%**, and **100%**.
- Implementing Nginx weighted routing configurations and Docker Compose definitions.
- Simulating live request traffic across each stage to evaluate real-world routing distributions.
- Demonstrating an automated rollback tripwire: injecting faults into the Canary workload, observing telemetry exceeding the 5% error SLA, and immediately reverting 100% of traffic to the Stable version.
- Documenting operational advantages, limitations, and risk controls.

---

## 2. Tools and Technologies Used
- **Application Workloads**: Python 3 / Flask (Lightweight HTTP services)
- **Containerization**: Dockerfile (`Dockerfile.stable`, `Dockerfile.canary`) & Docker Compose
- **Traffic Routing**: Nginx Weighted Upstream (`weight=9` vs `weight=1`)
- **Telemetry & Progressive Engine**: `demonstrate_canary.py` (Weighted proxy router, telemetry collector, and rollback tripwire)
- **Kubernetes Manifests**: `kubernetes/canary-deployment.yaml` (Pod-ratio traffic splitting)

---

## 3. Canary Architecture and Progressive Stages

```
                       [ Incoming User Requests ]
                                   |
                                   v
             +-------------------------------------------+
             |         Nginx / Canary Traffic Router     |
             |                  (Port 8000)              |
             +---------------------+---------------------+
                                   |
             +---------------------+---------------------+
             | (e.g. 90% Traffic)                        | (e.g. 10% Traffic)
             v                                           v
+-------------------------+                 +-------------------------+
|     Stable Workload     |                 |     Canary Workload     |
|  - Container: app-stable|                 |  - Container: app-canary|
|  - Version: 1.0.0       |                 |  - Version: 2.0.0       |
|  - Port: 8081           |                 |  - Port: 8082           |
+-------------------------+                 +------------+------------+
             ^                                           |
             |                                           v
             |                              [ Telemetry & Error Monitor ]
             |                              - Error Rate < 5% (Healthy)
             |                              - Error Rate > 5% (Degraded)
             |                                           |
             +<------------------------------------------+
                  [ Automated Rollback Tripwire Reverts 100% Traffic ]
```

### Progressive Rollout Stages:
1. **Stage 1 (10% Canary)**: Only 1 out of 10 incoming requests hits the canary workload. Verifies baseline system stability.
2. **Stage 2 (25% Canary)**: 1 out of 4 requests hits the canary. Evaluates database query performance and cache load.
3. **Stage 3 (50% Canary)**: Equal traffic distribution between Stable and Canary.
4. **Stage 4 (100% Full Promotion)**: 100% of traffic routed to Version 2.0.0. The stable workload is decommissioned.
5. **Rollback Trigger**: If errors, latencies, or faults exceed 5% at any stage, the router instantly reverts to 100% Stable.

---

## 4. Directory Structure

```
question-7-canary-deployment/
├── docker/
│   ├── app_stable.py            # Stable workload (v1.0.0)
│   ├── app_canary.py            # Canary workload with fault simulation (v2.0.0)
│   ├── Dockerfile.stable        # Docker build for Stable
│   ├── Dockerfile.canary        # Docker build for Canary
│   ├── docker-compose.yml       # Orchestration for Stable, Canary, and Nginx
│   ├── nginx.conf               # Master Nginx reverse proxy
│   ├── nginx-10pct.conf         # 90:10 weight configuration
│   ├── nginx-25pct.conf         # 75:25 weight configuration
│   ├── nginx-50pct.conf         # 50:50 weight configuration
│   └── nginx-100pct.conf        # 0:100 full promotion configuration
├── kubernetes/
│   └── canary-deployment.yaml   # Pod-ratio Kubernetes manifests (9:1 replica ratio)
├── scripts/
│   └── demonstrate_canary.py    # Automated progressive rollout & rollback demonstrator
├── evidence/
│   ├── canary_execution.log     # Terminal execution log
│   └── canary_evidence.json     # Structured verification metrics
└── README.md                    # This documentation
```

---

## 5. Execution Steps and Commands

### Step 1: Run Progressive Canary Rollout & Rollback Demonstration
```bash
python question-7-canary-deployment/scripts/demonstrate_canary.py
```

### Step 2: (Optional) Running with Docker Compose
```bash
cd question-7-canary-deployment/docker
docker compose up -d
```
To shift weights in Nginx:
```bash
cp nginx-25pct.conf upstream.conf
docker exec nginx-canary-proxy nginx -s reload
```

---

## 6. Actual Execution Output & Verification Results

```text
===========================================================================
 LAB 4 - QUESTION 7: CANARY DEPLOYMENT PROGRESSIVE ROLLOUT & ROLLBACK
===========================================================================
[INIT] Stable Workload running on http://127.0.0.1:8081 (Version: 1.0.0)
[INIT] Canary Workload running on http://127.0.0.1:8082 (Version: 2.0.0)
[INIT] Nginx/Canary Traffic Router active on http://127.0.0.1:8000

--- Stage 1: Initial Canary Traffic Slice (10%) (Active Canary Ratio: 10%) ---
 Requests: 40 | Stable: 39 | Canary: 1 (2.5%) | Errors: 0 (0.0%)

--- Stage 2: Expanded Canary Traffic Slice (25%) (Active Canary Ratio: 25%) ---
 Requests: 40 | Stable: 28 | Canary: 12 (30.0%) | Errors: 0 (0.0%)

--- Stage 3: High-Confidence Canary Slice (50%) (Active Canary Ratio: 50%) ---
 Requests: 40 | Stable: 19 | Canary: 21 (52.5%) | Errors: 0 (0.0%)

--- Stage 4: Full Promotion (100% Canary) (Active Canary Ratio: 100%) ---
 Requests: 20 | Stable: 0 | Canary: 20 (100.0%) | Errors: 0 (0.0%)

===========================================================================
 AUTOMATED ROLLBACK DEMONSTRATION
===========================================================================
[SIMULATION] Deploying candidate version with defect into 25% Canary slice...

--- Fault-Injection Window (Evaluating SLA Telemetry) (Active Canary Ratio: 25%) ---
 Requests: 30 | Stable: 20 | Canary: 10 (33.3%) | Errors: 9 (30.0%)

[TELEMETRY MONITOR] Observed Error Rate: 30.0% | SLA Threshold: 5.0%
[TRIPWIRE TRIGGERED] Error threshold breached! Executing IMMEDIATE ROLLBACK to Stable (0% Canary)...
[ROLLBACK COMPLETE] Traffic diverted 100% back to Stable (port 8081, v1.0.0).

--- Post-Rollback Health Verification (Active Canary Ratio: 0%) ---
 Requests: 25 | Stable: 25 | Canary: 0 (0.0%) | Errors: 0 (0.0%)

===========================================================================
 CANARY ROLLOUT & ROLLBACK SUMMARY
===========================================================================
 Post-Rollback Error Rate : 0.0% (0% Errors)
 Post-Rollback Stability  : 100% Stable v1.0.0 Restored
===========================================================================
```

---

## 7. Advantages and Limitations

### Advantages:
1. **Minimized Blast Radius**: Bugs or memory leaks are caught when only 10% of users are exposed, protecting 90% of customers from disruption.
2. **Real Production Validation**: Tests software against actual user inputs, production database workloads, and network latency.
3. **Automated Safety Tripwires**: Telemetry monitors trigger automated rollback without requiring human intervention.
4. **Gradual Resource Scaling**: Infrastructure capacity can be shifted incrementally rather than doubling resource footprint.

### Limitations:
1. **High Telemetry Dependency**: Requires mature metrics and APM pipelines (Prometheus, OpenTelemetry) to detect subtle anomalies.
2. **Schema & Multi-version Complexity**: Database schemas must support concurrent requests from both Stable (v1.0) and Canary (v2.0) without conflicts.
3. **User Experience Inconsistency**: Different users may observe different feature versions during the canary window.
