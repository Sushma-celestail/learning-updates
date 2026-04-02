"""
tests/test_users.py
-------------------
Tests for user endpoints using SQLAlchemy in-memory SQLite database.

DAY 3 CHANGES:
  - Uses SQLite in-memory DB instead of temp JSON files
  - Overrides get_db() dependency to use test database
  - Creates and drops tables per test for full isolation
  - All test cases are IDENTICAL to Day 2

WHY SQLITE FOR TESTS?
  We don't want tests hitting the real Supabase database because:
    1. Tests would be slow (network round trips)
    2. Tests would pollute real data
    3. Tests need to run offline (CI/CD)

  SQLite in-memory is:
    - Fast (no disk, no network)
    - Isolated (destroyed after each test)
    - Compatible (SQLAlchemy works with both PostgreSQL and SQLite)
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from models.db_models import UserModel, TaskModel
from main import app


# ── Test Database Setup ───────────────────────────────────────────────────────

from sqlalchemy.pool import StaticPool

def get_test_engine():
    """Create a fresh SQLite in-memory engine for each test."""
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def client():
    """
    Create a TestClient with a clean in-memory database per test.

    Steps:
      1. Create SQLite in-memory engine
      2. Create all tables (users, tasks)
      3. Override get_db() to use test session
      4. Yield the TestClient
      5. Drop all tables (cleanup)
    """
    test_engine = get_test_engine()
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Create tables in test DB
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        """Replace production DB session with test DB session."""
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    # Cleanup after test
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


# ── Registration Tests ────────────────────────────────────────────────────────

def test_register_success(client):
    """Happy path: valid data returns 201 with user info."""
    response = client.post("/users/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "securepass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data  # CRITICAL: never expose password


def test_register_duplicate_username(client):
    """Registering with existing username returns 409."""
    payload = {"username": "alice", "email": "alice@example.com", "password": "pass1234"}
    client.post("/users/register", json=payload)
    response = client.post("/users/register", json={
        "username": "alice",
        "email": "alice2@example.com",
        "password": "pass5678"
    })
    assert response.status_code == 409
    assert response.json()["error"] == "DuplicateUserError"


def test_register_short_username(client):
    """Username under 3 chars fails validation — 422."""
    response = client.post("/users/register", json={
        "username": "ab",
        "email": "ab@example.com",
        "password": "password123"
    })
    assert response.status_code == 422


def test_register_invalid_email(client):
    """Non-email string fails EmailStr validation — 422."""
    response = client.post("/users/register", json={
        "username": "bob",
        "email": "not-an-email",
        "password": "password123"
    })
    assert response.status_code == 422


def test_register_short_password(client):
    """Password under 8 chars fails — 422."""
    response = client.post("/users/register", json={
        "username": "carol",
        "email": "carol@example.com",
        "password": "short"
    })
    assert response.status_code == 422


def test_register_whitespace_username(client):
    """Whitespace-only username rejected by field_validator."""
    response = client.post("/users/register", json={
        "username": "   ",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 422


# ── Login Tests ───────────────────────────────────────────────────────────────

def test_login_success(client):
    """Valid credentials return 200 with user info."""
    client.post("/users/register", json={
        "username": "dave",
        "email": "dave@example.com",
        "password": "mypassword1"
    })
    response = client.post("/users/login", json={
        "username": "dave",
        "password": "mypassword1"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "dave"


def test_login_wrong_password(client):
    """Wrong password returns 401."""
    client.post("/users/register", json={
        "username": "eve",
        "email": "eve@example.com",
        "password": "correctpass"
    })
    response = client.post("/users/login", json={
        "username": "eve",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert response.json()["error"] == "InvalidCredentialsError"


def test_login_unknown_user(client):
    """Login for non-existent user returns 401."""
    response = client.post("/users/login", json={
        "username": "ghost",
        "password": "anything"
    })
    assert response.status_code == 401


# ── List Users Tests ──────────────────────────────────────────────────────────

def test_list_users_empty(client):
    """Empty database returns empty list."""
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == []


def test_list_users_returns_multiple(client):
    """All registered users appear in the list."""
    r1 = client.post("/users/register", json={"username": "user1", "email": "u1@x.com", "password": "password1"})
    assert r1.status_code == 201
    r2 = client.post("/users/register", json={"username": "user2", "email": "u2@x.com", "password": "password2"})
    assert r2.status_code == 201
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_users_no_passwords(client):
    """Passwords must never appear in the user list."""
    client.post("/users/register", json={"username": "frank", "email": "f@x.com", "password": "secret123"})
    users = client.get("/users").json()
    for user in users:
        assert "password" not in user


# ── Delete User Tests ─────────────────────────────────────────────────────────

def test_delete_user_success(client):
    """Deleting an existing user returns 200."""
    reg = client.post("/users/register", json={
        "username": "todelete",
        "email": "del@x.com",
        "password": "deletepass"
    })
    user_id = reg.json()["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    users = client.get("/users").json()
    assert not any(u["id"] == user_id for u in users)


def test_delete_user_not_found(client):
    """Deleting non-existent user returns 404."""
    response = client.delete("/users/9999")
    assert response.status_code == 404
    assert response.json()["error"] == "UserNotFoundError"
