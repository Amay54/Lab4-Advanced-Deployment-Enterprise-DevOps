# Question 3: Blue-Green Deployment Strategy

## 1. Aim and Objectives
The objective of this practical is to design, implement, and verify a **Blue-Green Deployment Strategy** for zero-downtime application updates and instantaneous rollback capability.

Specifically, this practical accomplishes:
- Deployment of two isolated application environments: **Blue** (v1.0.0, current live release) and **Green** (v2.0.0, target release).
- Packaging both versions as lightweight containerized workloads via Docker and Docker Compose.
- Configuring an Nginx reverse proxy / traffic switch router to direct incoming user traffic.
- Demonstrating live traffic switching from Blue to Green under continuous request loads.
- Demonstrating instantaneous rollback from Green back to Blue upon request.
- Measuring application availability and ensuring zero dropped packets during transition.
- Documenting operational advantages, limitations, and risk considerations.

---

## 2. Tools and Technologies Used
- **Application Framework**: Python 3 / Flask (Lightweight HTTP service)
- **Container Engine**: Docker & Dockerfile (`Dockerfile.blue`, `Dockerfile.green`)
- **Multi-Container Orchestration**: Docker Compose (`docker-compose.yml`)
- **Traffic Router / Reverse Proxy**: Nginx Alpine (`nginx.conf`, dynamic upstream configuration)
- **Testing & Verification**: Automated HTTP test runner (`demonstrate_blue_green.py`)

---

## 3. Architecture and Traffic Routing Mechanism

```
                         [ Incoming User Requests ]
                                     |
                                     v
                 +---------------------------------------+
                 |       Nginx Reverse Proxy Router      |
                 |               (Port 8000)             |
                 +-------------------+-------------------+
                                     |
             +-----------------------+-----------------------+
             | (Initial Active Route)| (Switched Route)      |
             v                       |                       v
+-------------------------+          |          +-------------------------+
|    Blue Environment     |          |          |    Green Environment    |
|  - Container: app-blue  |          |          |  - Container: app-green |
|  - Version: 1.0.0       |          |          |  - Version: 2.0.0       |
|  - Port: 8081           |          |          |  - Port: 8082           |
|  - Status: ACTIVE       |          |          |  - Status: STAGING/IDLE |
+-------------------------+          |          +-------------------------+
             |                       |                       |
             +-----------------------+-----------------------+
                                     |
                     [ Rollback Target (Instantaneous) ]
```

### Working Mechanism:
1. **Blue Environment Active**: Initially, the reverse proxy routes 100% of incoming production requests to the Blue environment running Version 1.0.0 on port 8081.
2. **Green Environment Staged**: The new Version 2.0.0 is deployed in the Green environment on port 8082 and undergoes independent smoke testing while receiving no production traffic.
3. **Cutover / Traffic Switch**: The reverse proxy configuration is updated (`upstream app_servers -> app-green:8082`) and dynamically reloaded. Incoming requests are instantaneously routed to Version 2.0.0 with zero dropped packets.
4. **Immediate Rollback**: If defects are detected in Green, the reverse proxy upstream is instantly pointed back to Blue without needing redeployment or rebuilding.

---

## 4. Directory Structure

```
question-3-blue-green/
├── docker/
│   ├── app_blue.py               # Blue application source (v1.0.0)
│   ├── app_green.py              # Green application source (v2.0.0)
│   ├── Dockerfile.blue           # Docker build for Blue
│   ├── Dockerfile.green          # Docker build for Green
│   ├── docker-compose.yml        # Orchestration for Blue, Green & Nginx
│   ├── nginx.conf                # Master Nginx reverse proxy configuration
│   ├── nginx-blue.conf           # Upstream pointing to Blue (8081)
│   └── nginx-green.conf          # Upstream pointing to Green (8082)
├── scripts/
│   ├── demonstrate_blue_green.py # End-to-end zero downtime demonstrator
│   └── switch_traffic.py         # Standalone upstream switch utility
├── evidence/
│   ├── blue_green_execution.log  # Plaintext request-by-request log
│   └── blue_green_evidence.json  # Structured execution metrics
└── README.md                     # This documentation
```

---

## 5. Execution Steps and Commands

### Step 1: Run the Automated Zero-Downtime Demonstration
Execute the demonstration script which spins up Blue, Green, and the proxy router, routes traffic, executes cutover, triggers rollback, and verifies continuity:

```bash
python question-3-blue-green/scripts/demonstrate_blue_green.py
```

### Step 2: (Alternative) Running with Docker Compose
To run using Docker containers:
```bash
cd question-3-blue-green/docker
docker compose up -d
```
Switch traffic to Green:
```bash
python ../scripts/switch_traffic.py green
docker exec nginx-reverse-proxy nginx -s reload
```
Rollback traffic to Blue:
```bash
python ../scripts/switch_traffic.py blue
docker exec nginx-reverse-proxy nginx -s reload
```

---

## 6. Actual Execution Output & Verification Results

```text
===========================================================================
 LAB 4 - QUESTION 3: BLUE-GREEN DEPLOYMENT & TRAFFIC SWITCHING
===========================================================================
[INIT] Blue Service running on http://127.0.0.1:8081 (Version: 1.0.0, Color: Blue)
[INIT] Green Service running on http://127.0.0.1:8082 (Version: 2.0.0, Color: Green)
[INIT] Nginx/Proxy Router active on http://127.0.0.1:8000 -> Initial route: BLUE

--- Phase 1: Validating Active Traffic on Blue (v1.0.0) ---
 Request #01 -> HTTP 200 | Env: Blue | Version: 1.0.0
 Request #02 -> HTTP 200 | Env: Blue | Version: 1.0.0
 Request #03 -> HTTP 200 | Env: Blue | Version: 1.0.0
 Request #04 -> HTTP 200 | Env: Blue | Version: 1.0.0
 Request #05 -> HTTP 200 | Env: Blue | Version: 1.0.0

--- Phase 2: Executing Live Traffic Switch from Blue -> Green ---

[TRAFFIC ROUTER] >>> Switched traffic route: Pointing to GREEN (port 8082, v2.0.0) <<<
 Request #06 -> HTTP 200 | Env: Green | Version: 2.0.0
 Request #07 -> HTTP 200 | Env: Green | Version: 2.0.0
 Request #08 -> HTTP 200 | Env: Green | Version: 2.0.0
 Request #09 -> HTTP 200 | Env: Green | Version: 2.0.0
 Request #10 -> HTTP 200 | Env: Green | Version: 2.0.0
 Request #11 -> HTTP 200 | Env: Green | Version: 2.0.0
 Request #12 -> HTTP 200 | Env: Green | Version: 2.0.0

--- Phase 3: Demonstrating Instantaneous Rollback (Green -> Blue) ---

[TRAFFIC ROUTER] <<< ROLLBACK TRIGGERED: Pointing back to BLUE (port 8081, v1.0.0) <<<
 Request #13 -> HTTP 200 | Env: Blue | Version: 1.0.0
 Request #14 -> HTTP 200 | Env: Blue | Version: 1.0.0
 Request #15 -> HTTP 200 | Env: Blue | Version: 1.0.0
 Request #16 -> HTTP 200 | Env: Blue | Version: 1.0.0
 Request #17 -> HTTP 200 | Env: Blue | Version: 1.0.0
 Request #18 -> HTTP 200 | Env: Blue | Version: 1.0.0

===========================================================================
 BLUE-GREEN VERIFICATION SUMMARY
===========================================================================
 Total Live Requests Handled: 18
 Successful 200 OK Requests : 18
 Dropped / Failed Requests  : 0 (0% Error Rate)
 Availability During Switch : 100.0% (Zero Downtime)
 Rollback Latency           : Instantaneous (0 milliseconds)
===========================================================================
```

---

## 7. Advantages and Limitations

### Advantages:
1. **Zero Downtime**: Upstream switching takes effect immediately with 0 dropped HTTP connections.
2. **Instantaneous Rollback**: Reverting to the previous stable release requires only redirecting the router/proxy, taking milliseconds without needing to rebuild or redeploy containers.
3. **Safe Production Testing**: The Green environment can be tested under production-like network conditions before a single customer request is routed to it.
4. **Simple Mental Model**: Clear separation between active live traffic and standby staging environments.

### Limitations:
1. **Double Resource Consumption**: Maintaining two identical production environments doubles infrastructure footprint and compute cost during releases.
2. **Database Schema Compatibility**: Both Blue (v1.0.0) and Green (v2.0.0) must remain backward- and forward-compatible with shared state or database schemas during the transition period.
3. **State & Session Handling**: Long-lived WebSocket connections or stateful sessions must be gracefully drained before shutting down the Blue environment.
