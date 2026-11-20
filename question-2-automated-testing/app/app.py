from flask import Flask, request, jsonify
import os
import time
import uuid
import sqlite3
from datetime import datetime, timezone

import tempfile

app = Flask(__name__)

# Configuration via environment variables
APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")
APP_ENV = os.environ.get("APP_ENV", "production")
APP_COLOR = os.environ.get("APP_COLOR", "#1E88E5") # Blue default
DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(tempfile.gettempdir(), "lab4_app.db"))
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "mock-vault-secret-token-xyz")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "db-secure-pass-lab4")
CANARY_FAULT_RATE = float(os.environ.get("CANARY_FAULT_RATE", "0.0"))

START_TIME = time.time()
REQUEST_COUNT = 0
ERROR_COUNT = 0

def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH) if os.path.dirname(DATABASE_PATH) else ".", exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            item_count INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            tax REAL NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    print(f"Database init notice: {e}")

@app.before_request
def count_request():
    global REQUEST_COUNT
    REQUEST_COUNT += 1

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "Enterprise Order Management Service",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "color": APP_COLOR,
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/health", methods=["GET"])
def health():
    global ERROR_COUNT
    # Canary simulation: deliberately fail if fault injection is active
    if CANARY_FAULT_RATE > 0.0:
        import random
        if random.random() < CANARY_FAULT_RATE:
            ERROR_COUNT += 1
            return jsonify({
                "status": "DEGRADED",
                "version": APP_VERSION,
                "error": "Simulated Canary Service Flapping / Crash"
            }), 500

    uptime = time.time() - START_TIME
    return jsonify({
        "status": "UP",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "color": APP_COLOR,
        "uptime_seconds": round(uptime, 2),
        "requests_handled": REQUEST_COUNT,
        "errors_recorded": ERROR_COUNT
    }), 200

@app.route("/version", methods=["GET"])
def version():
    return jsonify({
        "version": APP_VERSION,
        "environment": APP_ENV,
        "release_tag": f"release-{APP_VERSION}",
        "color": APP_COLOR
    })

@app.route("/api/v1/orders", methods=["GET"])
def list_orders():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_id, item_count, subtotal, tax, total, status, created_at FROM orders ORDER BY created_at DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    
    orders = []
    for r in rows:
        orders.append({
            "id": r[0],
            "customer_id": r[1],
            "item_count": r[2],
            "subtotal": r[3],
            "tax": r[4],
            "total": r[5],
            "status": r[6],
            "created_at": r[7]
        })
    return jsonify({"orders": orders, "count": len(orders)})

@app.route("/api/v1/orders", methods=["POST"])
def create_order():
    global ERROR_COUNT
    data = request.get_json(silent=True)
    if not data:
        ERROR_COUNT += 1
        return jsonify({"error": "Invalid JSON body"}), 400
    
    customer_id = data.get("customer_id")
    items = data.get("items", [])
    
    if not customer_id:
        ERROR_COUNT += 1
        return jsonify({"error": "Missing required field: customer_id"}), 422
    
    if not isinstance(items, list) or len(items) == 0:
        ERROR_COUNT += 1
        return jsonify({"error": "Field 'items' must be a non-empty list"}), 422
    
    subtotal = 0.0
    for idx, item in enumerate(items):
        qty = item.get("quantity", 0)
        price = item.get("unit_price", 0.0)
        if qty <= 0 or price < 0:
            ERROR_COUNT += 1
            return jsonify({"error": f"Invalid quantity or price at item index {idx}"}), 422
        subtotal += qty * price
        
    tax_rate = 0.10 # 10% tax
    tax = round(subtotal * tax_rate, 2)
    
    # Version 2.0 feature: Promotional 5% enterprise discount
    discount = 0.0
    if APP_VERSION.startswith("2."):
        discount = round(subtotal * 0.05, 2)
        
    total = round(subtotal + tax - discount, 2)
    order_id = f"ord-{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (id, customer_id, item_count, subtotal, tax, total, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (order_id, customer_id, len(items), subtotal, tax, total, "CONFIRMED", created_at)
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        "order_id": order_id,
        "customer_id": customer_id,
        "item_count": len(items),
        "subtotal": subtotal,
        "tax": tax,
        "discount_applied": discount,
        "total": total,
        "status": "CONFIRMED",
        "created_at": created_at,
        "processed_by_version": APP_VERSION
    }), 201

@app.route("/api/v1/secret-check", methods=["GET"])
def check_secret():
    # Safely verify secret availability without leaking values
    masked_db = f"{DB_PASSWORD[:2]}****{DB_PASSWORD[-2:]}" if len(DB_PASSWORD) > 4 else "configured"
    masked_token = f"{SECRET_TOKEN[:3]}...{SECRET_TOKEN[-3:]}" if len(SECRET_TOKEN) > 6 else "configured"
    return jsonify({
        "status": "SECURE",
        "db_password_configured": bool(DB_PASSWORD),
        "db_password_masked": masked_db,
        "vault_secret_token_configured": bool(SECRET_TOKEN),
        "vault_token_masked": masked_token,
        "secret_source": os.environ.get("SECRET_STORE", "Kubernetes-Secret-or-Vault")
    })

@app.route("/api/v1/metrics", methods=["GET"])
def metrics():
    uptime = time.time() - START_TIME
    error_rate = (ERROR_COUNT / REQUEST_COUNT) if REQUEST_COUNT > 0 else 0.0
    return jsonify({
        "requests_total": REQUEST_COUNT,
        "errors_total": ERROR_COUNT,
        "error_rate": round(error_rate, 4),
        "uptime_seconds": round(uptime, 2),
        "version": APP_VERSION
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
