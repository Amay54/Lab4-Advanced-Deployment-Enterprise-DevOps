from flask import Flask, jsonify, request
import os
import time

app = Flask(__name__)
VERSION = "1.0.0"
ENV_NAME = "Stable"
PORT = int(os.environ.get("PORT", 8081))
START_TIME = time.time()
REQUESTS_SERVED = 0

@app.route("/", methods=["GET"])
@app.route("/api/info", methods=["GET"])
def info():
    global REQUESTS_SERVED
    REQUESTS_SERVED += 1
    return jsonify({
        "service": "Enterprise Canary Workload",
        "version": VERSION,
        "environment": ENV_NAME,
        "status": "HEALTHY",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "requests_served": REQUESTS_SERVED
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "UP", "version": VERSION, "environment": ENV_NAME}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
