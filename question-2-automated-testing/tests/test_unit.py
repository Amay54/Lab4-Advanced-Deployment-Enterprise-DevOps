import pytest
import os
import sys

# Add app directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
from app import app, init_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Unit Test 1: Verify health check returns 200 UP"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "UP"
    assert "version" in data
    assert "uptime_seconds" in data

def test_index_endpoint(client):
    """Unit Test 2: Verify service root endpoint information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "operational"
    assert data["service"] == "Enterprise Order Management Service"

def test_version_endpoint(client):
    """Unit Test 3: Verify release version metadata"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.get_json()
    assert "version" in data
    assert "release_tag" in data

def test_order_validation_missing_body(client):
    """Unit Test 4: Verify rejection of invalid or empty body"""
    response = client.post("/api/v1/orders", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_order_validation_missing_customer(client):
    """Unit Test 5: Verify customer_id is strictly required"""
    payload = {"items": [{"item_id": "SKU-1", "quantity": 2, "unit_price": 50.0}]}
    response = client.post("/api/v1/orders", json=payload)
    assert response.status_code == 422
    assert "Missing required field: customer_id" in response.get_json()["error"]

def test_order_validation_invalid_pricing(client):
    """Unit Test 6: Verify validation of quantity and price values"""
    payload = {
        "customer_id": "CUST-999",
        "items": [{"item_id": "SKU-1", "quantity": -5, "unit_price": 20.0}]
    }
    response = client.post("/api/v1/orders", json=payload)
    assert response.status_code == 422
    assert "Invalid quantity or price" in response.get_json()["error"]

def test_secret_masking(client):
    """Unit Test 7: Verify secret check never exposes raw credential values"""
    response = client.get("/api/v1/secret-check")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "SECURE"
    assert data["db_password_configured"] is True
    # Verify masking
    assert "****" in data["db_password_masked"]
    assert "..." in data["vault_token_masked"]
