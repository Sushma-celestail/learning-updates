import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base

# Reuse setup logic or use a shared conftest if needed. 
# For now, local client.
client = TestClient(app)

def test_apply_loan_success():
    # Assume user 1 is registered (from previous tests or setup)
    response = client.post(
        "/loans/",
        json={
            "amount": 500000,
            "purpose": "home",
            "tenure_months": 120,
            "employment_status": "employed"
        }
    )
    assert response.status_code == 201
    assert response.json()["status"] == "pending"

def test_apply_loan_amount_limit():
    response = client.post(
        "/loans/",
        json={
            "amount": 2000000, # Exceeds 10,00,000
            "purpose": "home",
            "tenure_months": 120,
            "employment_status": "employed"
        }
    )
    assert response.status_code == 422

def test_apply_max_pending_loans():
    # Apply 3 times
    for _ in range(3):
        client.post(
            "/loans/",
            json={"amount": 1000, "purpose": "personal", "tenure_months": 12, "employment_status": "student"}
        )
    # 4th one should fail
    response = client.post(
        "/loans/",
        json={"amount": 1000, "purpose": "personal", "tenure_months": 12, "employment_status": "student"}
    )
    assert response.status_code == 422
    assert response.json()["error"] == "MaxPendingLoansError"

def test_get_my_loans():
    response = client.get("/loans/my")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_loan_detail():
    # Create one
    res = client.post(
        "/loans/",
        json={"amount": 5000, "purpose": "personal", "tenure_months": 12, "employment_status": "student"}
    )
    loan_id = res.json()["id"]
    response = client.get(f"/loans/my/{loan_id}")
    assert response.status_code == 200
    assert response.json()["id"] == loan_id
