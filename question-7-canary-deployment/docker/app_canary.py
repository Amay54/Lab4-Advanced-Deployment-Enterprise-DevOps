from flask import Flask, jsonify, request
import os
import time
import random

app = Flask(__name__)
VERSION = "2.0.0"
ENV_NAME = "Canary"
PORT = int(os.environ.get("PORT", 8082))
START_TIME = time.time()
REQUESTS_SERVED = 0
ERRORS_RECORDED = 0
FAULT_RATE = float(os.environ.get("FAULT_RATE", "0.0"))

@app.route("/", methods=["GET"])
@app.route("/api/info", methods=["GET"])
def info():
    global REQUESTS_SERVED, ERRORS_RECORDED
    REQUESTS_SERVED += 1
    
    # Fault injection simulation for rollback demonstration
    current_fault_rate = float(request.args.get("fault_rate", FAULT_RATE))
    if current_fault_rate > 0.0 and random.random() < current_fault_rate:
        ERRORS_RECORDED += 1
        return jsonify({
            "service": "Enterprise Canary Workload",
            "version": VERSION,
            "environment": ENV_NAME,
            "status": "DEGRADED",
            "error": "Simulated Canary Service Fault (500 Internal Error)",
            "requests_served": REQUESTS_SERVED,
            "errors_recorded": ERRORS_RECORDED
        }), 500

    return jsonify({
        "service": "Enterprise Canary Workload",
        "version": VERSION,
        "environment": ENV_NAME,
        "status": "HEALTHY",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "requests_served": REQUESTS_SERVED,
        "errors_recorded": ERRORS_RECORDED
    }), 200

@app.route("/health", methods=["GET"])
def health():
    current_fault_rate = float(request.args.get("fault_rate", FAULT_RATE))
    if current_fault_rate > 0.3:
        return jsonify({"status": "DEGRADED", "version": VERSION, "error": "High error rate"}), 500
    return jsonify({"status": "UP", "version": VERSION, "environment": ENV_NAME}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
