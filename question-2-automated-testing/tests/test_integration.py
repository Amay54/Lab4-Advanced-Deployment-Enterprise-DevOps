import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
from app import app, init_db

@pytest.fixture
def client():
    # Use temporary DB for clean integration tests
    test_db = os.path.join(tempfile.gettempdir(), "test_integration.db")
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except Exception:
            pass
    os.environ["DATABASE_PATH"] = test_db
    app.config["TESTING"] = True
    init_db()
    with app.test_client() as client:
        yield client

def test_full_order_lifecycle_integration(client):
    """Integration Test 1: Create an order, calculate taxes, verify persistence"""
    order_payload = {
        "customer_id": "CLIENT-ENTERPRISE-01",
        "items": [
            {"item_id": "PROD-A", "quantity": 2, "unit_price": 100.0},
            {"item_id": "PROD-B", "quantity": 1, "unit_price": 50.0}
        ]
    }
    # 1. Post new order
    create_res = client.post("/api/v1/orders", json=order_payload)
    assert create_res.status_code == 201
    created_order = create_res.get_json()
    assert created_order["subtotal"] == 250.0
    assert created_order["tax"] == 25.0
    assert created_order["total"] == 275.0
    assert created_order["status"] == "CONFIRMED"
    order_id = created_order["order_id"]

    # 2. Query orders list and assert order is stored
    list_res = client.get("/api/v1/orders")
    assert list_res.status_code == 200
    orders_data = list_res.get_json()
    assert orders_data["count"] >= 1
    found = any(o["id"] == order_id for o in orders_data["orders"])
    assert found is True

def test_metrics_telemetry_integration(client):
    """Integration Test 2: Verify request telemetry increments on interactions"""
    metrics_before = client.get("/api/v1/metrics").get_json()
    initial_requests = metrics_before["requests_total"]

    # Trigger multiple endpoints
    client.get("/health")
    client.get("/version")

    metrics_after = client.get("/api/v1/metrics").get_json()
    assert metrics_after["requests_total"] >= initial_requests + 2
