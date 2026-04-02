import pytest
from fastapi.testclient import TestClient
from main import app

# Using global client from conftest.py. Setup specifically for this module:
@pytest.fixture(scope="module", autouse=True)
def setup_loans(client):
    # Create a user for loan tests
    client.post("/auth/register", json={
        "username": "loanuser",
        "email": "loan@example.com",
        "password": "password123",
        "phone": "1234567890",
        "monthly_income": 60000
    })

def test_apply_loan_success(client):
    response = client.post("/loans", json={
        "amount": 500000,
        "purpose": "home",
        "tenure_months": 240,
        "employment_status": "employed"
    }, headers={"X-User": "loanuser"})
    assert response.status_code == 201
    assert response.json()["amount"] == 500000

def test_apply_loan_amount_limit(client):
    response = client.post("/loans", json={
        "amount": 1000001,
        "purpose": "home",
        "tenure_months": 240,
        "employment_status": "employed"
    }, headers={"X-User": "loanuser"})
    assert response.status_code == 422

def test_max_pending_loans(client):
    # Already has 1 from previous test. Add 2 more.
    for _ in range(2):
        client.post("/loans", json={
            "amount": 100000,
            "purpose": "personal",
            "tenure_months": 12,
            "employment_status": "employed"
        }, headers={"X-User": "loanuser"})
    
    # 4th one should fail
    response = client.post("/loans", json={
        "amount": 100000,
        "purpose": "personal",
        "tenure_months": 12,
        "employment_status": "employed"
    }, headers={"X-User": "loanuser"})
    assert response.status_code == 422

def test_get_my_loans(client):
    response = client.get("/loans/my", headers={"X-User": "loanuser"})
    assert response.status_code == 200
    assert len(response.json()) >= 3

def test_get_single_loan_detail(client):
    loans = client.get("/loans/my", headers={"X-User": "loanuser"}).json()
    loan_id = loans[0]["id"]
    response = client.get(f"/loans/my/{loan_id}", headers={"X-User": "loanuser"})
    assert response.status_code == 200
    assert response.json()["id"] == loan_id
