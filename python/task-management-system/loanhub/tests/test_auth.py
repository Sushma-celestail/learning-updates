import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..database import Base, get_db

# Setup test database (SQLite for simplicity in tests)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_register_user_success():
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "phone": "9876543210",
            "monthly_income": 50000
        }
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

def test_register_duplicate_username():
    client.post(
        "/auth/register",
        json={
            "username": "dupuser",
            "email": "dup1@example.com",
            "password": "password123",
            "phone": "9876543210",
            "monthly_income": 50000
        }
    )
    response = client.post(
        "/auth/register",
        json={
            "username": "dupuser",
            "email": "dup2@example.com",
            "password": "password123",
            "phone": "9876543210",
            "monthly_income": 50000
        }
    )
    assert response.status_code == 409
    assert response.json()["error"] == "DuplicateUserError"

def test_register_invalid_email():
    response = client.post(
        "/auth/register",
        json={
            "username": "useremail",
            "email": "invalid-email",
            "password": "password123",
            "phone": "9876543210",
            "monthly_income": 50000
        }
    )
    assert response.status_code == 422

def test_login_success():
    # Register first
    client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "securepassword",
            "phone": "9876543210",
            "monthly_income": 50000
        }
    )
    response = client.post(
        "/auth/login",
        json={"username": "loginuser", "password": "securepassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password():
    response = client.post(
        "/auth/login",
        json={"username": "loginuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
