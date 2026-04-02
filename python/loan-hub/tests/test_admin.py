import pytest
from fastapi.testclient import TestClient
from main import app
from config import settings

# Using global client from conftest.py. Setup specifically for this module:
@pytest.fixture(scope="module", autouse=True)
def setup_admin_test(client):
    # User for admin tests
    client.post("/auth/register", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "password123",
        "phone": "9876543210",
        "monthly_income": 50000
    })

def test_admin_view_all_loans(client):
    # Use admin username for header
    response = client.get("/admin/loans", headers={"X-User": settings.ADMIN_USERNAME})
    assert response.status_code == 200

def test_admin_approve_loan(client):
    # Apply for a loan first
    l_res = client.post("/loans", json={
        "amount": 100000,
        "purpose": "personal",
        "tenure_months": 12,
        "employment_status": "employed"
    }, headers={"X-User": "testuser2"})
    loan_id = l_res.json()["id"]

    response = client.patch(f"/admin/loans/{loan_id}/review", json={
        "status": "approved",
        "admin_remarks": "Approved with good income"
    }, headers={"X-User": settings.ADMIN_USERNAME})
    assert response.status_code == 200
    assert response.json()["status"] == "approved"

def test_admin_reject_loan(client):
    l_res = client.post("/loans", json={
        "amount": 100000,
        "purpose": "personal",
        "tenure_months": 12,
        "employment_status": "unemployed"
    }, headers={"X-User": "testuser2"})
    loan_id = l_res.json()["id"]

    response = client.patch(f"/admin/loans/{loan_id}/review", json={
        "status": "rejected",
        "admin_remarks": "Rejected due to unemployment"
    }, headers={"X-User": settings.ADMIN_USERNAME})
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"

def test_admin_re_review_fail(client):
    loans = client.get("/admin/loans", headers={"X-User": settings.ADMIN_USERNAME}).json()
    # Find one that is approved or rejected
    processed = [l for l in loans if l["status"] != "pending"][0]
    
    response = client.patch(f"/admin/loans/{processed['id']}/review", json={
        "status": "approved",
        "admin_remarks": "Trying again"
    }, headers={"X-User": settings.ADMIN_USERNAME})
    assert response.status_code == 422

def test_non_admin_forbidden(client):
    response = client.get("/admin/loans", headers={"X-User": "testuser2"})
    assert response.status_code == 403
