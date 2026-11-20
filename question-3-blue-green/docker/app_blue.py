from flask import Flask, jsonify, render_template_string
import os
import time

app = Flask(__name__)
VERSION = "1.0.0"
COLOR = "Blue"
HEX_COLOR = "#1E88E5"
PORT = int(os.environ.get("PORT", 8081))
START_TIME = time.time()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Blue-Green Deployment - Blue Version</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f4f6f8; }
        .card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; border-top: 8px solid {{ hex_color }}; max-width: 450px; width: 100%; }
        .badge { display: inline-block; background-color: {{ hex_color }}; color: white; padding: 6px 16px; border-radius: 20px; font-weight: bold; font-size: 14px; margin-bottom: 20px; }
        h1 { margin: 0 0 10px 0; color: #2c3e50; }
        p { color: #666; margin: 8px 0; }
        .uptime { font-size: 12px; color: #999; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="badge">{{ color }} Environment</div>
        <h1>Enterprise App v{{ version }}</h1>
        <p>Status: <strong>Operational (Live Traffic)</strong></p>
        <p>Environment: <strong>Production Blue</strong></p>
        <p>Release Tag: <code>release-v1.0.0-stable</code></p>
        <div class="uptime">Uptime: {{ uptime }}s</div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    uptime = round(time.time() - START_TIME, 1)
    return render_template_string(HTML_TEMPLATE, version=VERSION, color=COLOR, hex_color=HEX_COLOR, uptime=uptime)

@app.route("/api/info", methods=["GET"])
def api_info():
    return jsonify({
        "environment": COLOR,
        "version": VERSION,
        "color_hex": HEX_COLOR,
        "status": "HEALTHY",
        "timestamp": time.time()
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "UP", "version": VERSION, "env": COLOR}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
