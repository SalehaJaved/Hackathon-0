"""
Basic API tests
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Expense Policy Enforcer" in response.json()["message"]


def test_health():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_submit_expense():
    """Test expense submission"""
    expense_data = {
        "vendor": "Test Vendor",
        "amount": 50.00,
        "date": "2026-02-19",
        "category": "general",
    }
    response = client.post("/api/v1/expenses/", data=expense_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] in ["pending", "approved", "needs_review"]


def test_list_expenses():
    """Test listing expenses"""
    response = client.get("/api/v1/expenses/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dashboard_stats():
    """Test dashboard statistics"""
    response = client.get("/api/v1/expenses/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "pending_count" in data
    assert "approved_count" in data
    assert "total_amount" in data


def test_policies_list():
    """Test policy listing"""
    response = client.get("/api/v1/policies/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
