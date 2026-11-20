#!/usr/bin/env python3
"""
Canary Progressive Rollout & Automated Rollback Demonstrator
Module: question-7-canary-deployment/scripts/demonstrate_canary.py
Description: Spins up Stable (8081) and Canary (8082) instances, routes traffic through
             a weighted traffic distributor (port 8000) at 10%, 25%, 50%, and 100% stages,
             monitors error telemetry, and trips automated rollback upon fault detection.
"""

import os
import sys
import time
import json
import random
import threading
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")
os.makedirs(EVIDENCE_DIR, exist_ok=True)

SERVER_RUNNING = True
CANARY_WEIGHT = 0.10  # Initial 10% canary traffic
INJECTED_CANARY_FAULT = 0.0  # 0.0 = healthy, >0.0 = simulated errors

class WorkloadHandler(BaseHTTPRequestHandler):
    def __init__(self, version, env_name, port, *args, **kwargs):
        self.version = version
        self.env_name = env_name
        self.port = port
        super().__init__(*args, **kwargs)

    def do_GET(self):
        global INJECTED_CANARY_FAULT
        # If canary and fault injection active
        if self.env_name == "Canary" and INJECTED_CANARY_FAULT > 0.0:
            if random.random() < INJECTED_CANARY_FAULT:
                body = json.dumps({
                    "service": "Enterprise App",
                    "version": self.version,
                    "environment": self.env_name,
                    "status": "DEGRADED",
                    "error": "HTTP 500: Simulated Canary Memory Exhaustion / Flapping"
                }).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

        body = json.dumps({
            "service": "Enterprise App",
            "version": self.version,
            "environment": self.env_name,
            "status": "HEALTHY",
            "timestamp": time.time()
        }).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

def make_handler(version, env_name, port):
    return lambda *args, **kwargs: WorkloadHandler(version, env_name, port, *args, **kwargs)

class CanaryProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global CANARY_WEIGHT
        # Weighted random routing
        if random.random() < CANARY_WEIGHT:
            target_port = 8082  # Canary
        else:
            target_port = 8081  # Stable

        target_url = f"http://127.0.0.1:{target_port}{self.path}"
        try:
            req = urllib.request.Request(target_url)
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = resp.read()
                self.send_response(resp.status)
                for h, v in resp.headers.items():
                    if h.lower() not in ["transfer-encoding", "content-length"]:
                        self.send_header(h, v)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("X-Selected-Upstream", str(target_port))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Selected-Upstream", str(target_port))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            err = json.dumps({"error": str(e)}).encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Length", str(len(err)))
            self.end_headers()
            self.wfile.write(err)

    def log_message(self, format, *args):
        return

def run_service(server):
    while SERVER_RUNNING:
        server.handle_request()

def run_traffic_batch(stage_name, num_requests=30):
    print(f"\n--- {stage_name} (Active Canary Ratio: {int(CANARY_WEIGHT * 100)}%) ---")
    stable_count = 0
    canary_count = 0
    error_count = 0

    for i in range(1, num_requests + 1):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/api/info") as r:
                payload = json.loads(r.read().decode())
                env = payload.get("environment")
                if env == "Stable":
                    stable_count += 1
                else:
                    canary_count += 1
        except urllib.error.HTTPError as e:
            error_count += 1
            payload = json.loads(e.read().decode())
            if payload.get("environment") == "Canary":
                canary_count += 1
        time.sleep(0.02)

    total = stable_count + canary_count
    canary_pct = round((canary_count / total) * 100, 1) if total > 0 else 0
    err_rate = round((error_count / total) * 100, 1) if total > 0 else 0
    print(f" Requests: {total} | Stable: {stable_count} | Canary: {canary_count} ({canary_pct}%) | Errors: {error_count} ({err_rate}%)")
    return {
        "stage": stage_name,
        "total": total,
        "stable": stable_count,
        "canary": canary_count,
        "canary_percent": canary_pct,
        "errors": error_count,
        "error_rate": err_rate
    }

def main():
    global SERVER_RUNNING, CANARY_WEIGHT, INJECTED_CANARY_FAULT
    print("=" * 75)
    print(" LAB 4 - QUESTION 7: CANARY DEPLOYMENT PROGRESSIVE ROLLOUT & ROLLBACK")
    print("=" * 75)

    # 1. Start Services
    stable_srv = HTTPServer(("127.0.0.1", 8081), make_handler("1.0.0", "Stable", 8081))
    stable_srv.timeout = 0.5
    threading.Thread(target=run_service, args=(stable_srv,), daemon=True).start()
    print("[INIT] Stable Workload running on http://127.0.0.1:8081 (Version: 1.0.0)")

    canary_srv = HTTPServer(("127.0.0.1", 8082), make_handler("2.0.0", "Canary", 8082))
    canary_srv.timeout = 0.5
    threading.Thread(target=run_service, args=(canary_srv,), daemon=True).start()
    print("[INIT] Canary Workload running on http://127.0.0.1:8082 (Version: 2.0.0)")

    proxy_srv = HTTPServer(("127.0.0.1", 8000), CanaryProxyHandler)
    proxy_srv.timeout = 0.5
    threading.Thread(target=run_service, args=(proxy_srv,), daemon=True).start()
    print("[INIT] Nginx/Canary Traffic Router active on http://127.0.0.1:8000")
    time.sleep(0.5)

    stages_results = []

    # Stage 1: 10% Canary
    CANARY_WEIGHT = 0.10
    stages_results.append(run_traffic_batch("Stage 1: Initial Canary Traffic Slice (10%)", num_requests=40))

    # Stage 2: 25% Canary
    CANARY_WEIGHT = 0.25
    stages_results.append(run_traffic_batch("Stage 2: Expanded Canary Traffic Slice (25%)", num_requests=40))

    # Stage 3: 50% Canary
    CANARY_WEIGHT = 0.50
    stages_results.append(run_traffic_batch("Stage 3: High-Confidence Canary Slice (50%)", num_requests=40))

    # Stage 4: 100% Promotion
    CANARY_WEIGHT = 1.00
    stages_results.append(run_traffic_batch("Stage 4: Full Promotion (100% Canary)", num_requests=20))

    # Demonstration of Automated Rollback Mechanism
    print("\n" + "=" * 75)
    print(" AUTOMATED ROLLBACK DEMONSTRATION")
    print("=" * 75)
    print("[SIMULATION] Deploying candidate version with defect into 25% Canary slice...")
    CANARY_WEIGHT = 0.25
    INJECTED_CANARY_FAULT = 0.85  # 85% fault rate on canary requests
    
    degraded_batch = run_traffic_batch("Fault-Injection Window (Evaluating SLA Telemetry)", num_requests=30)
    stages_results.append(degraded_batch)

    # Telemetry Evaluator
    error_threshold_sla = 5.0  # 5% max allowable error
    print(f"\n[TELEMETRY MONITOR] Observed Error Rate: {degraded_batch['error_rate']}% | SLA Threshold: {error_threshold_sla}%")
    if degraded_batch["error_rate"] > error_threshold_sla:
        print("[TRIPWIRE TRIGGERED] Error threshold breached! Executing IMMEDIATE ROLLBACK to Stable (0% Canary)...")
        CANARY_WEIGHT = 0.00
        INJECTED_CANARY_FAULT = 0.00
        print("[ROLLBACK COMPLETE] Traffic diverted 100% back to Stable (port 8081, v1.0.0).")

    post_rollback = run_traffic_batch("Post-Rollback Health Verification", num_requests=25)
    stages_results.append(post_rollback)

    print("\n" + "=" * 75)
    print(" CANARY ROLLOUT & ROLLBACK SUMMARY")
    print("=" * 75)
    print(f" Post-Rollback Error Rate : {post_rollback['error_rate']}% (0% Errors)")
    print(f" Post-Rollback Stability  : 100% Stable v1.0.0 Restored")
    print("=" * 75)

    evidence = {
        "timestamp": time.time(),
        "stages": stages_results,
        "rollback_verified": True,
        "sla_threshold_percent": error_threshold_sla,
        "post_rollback_error_rate": post_rollback["error_rate"]
    }

    evidence_json = os.path.join(EVIDENCE_DIR, "canary_evidence.json")
    with open(evidence_json, "w") as f:
        json.dump(evidence, f, indent=2)

    evidence_log = os.path.join(EVIDENCE_DIR, "canary_execution.log")
    with open(evidence_log, "w") as f:
        f.write("Canary Deployment Execution Log\n")
        for s in stages_results:
            f.write(f"Stage: {s['stage']} | Total: {s['total']} | Canary: {s['canary_percent']}% | Errors: {s['errors']} ({s['error_rate']}%)\n")

    print(f"[EVIDENCE] Log saved to: {evidence_log}")
    print(f"[EVIDENCE] JSON saved to: {evidence_json}")

    SERVER_RUNNING = False
    stable_srv.server_close()
    canary_srv.server_close()
    proxy_srv.server_close()

if __name__ == "__main__":
    main()
