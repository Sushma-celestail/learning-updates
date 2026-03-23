"""
tests/test_users.py
-------------------
Tests for all user endpoints using pytest + FastAPI TestClient.

HOW TESTING WORKS:
  FastAPI provides a TestClient (built on httpx) that lets you send HTTP
  requests to your app WITHOUT starting a real server. Perfect for CI/CD.

ISOLATION STRATEGY:
  Each test uses tmp_path (a pytest built-in fixture that gives a fresh
  temporary directory per test). We override the settings so the app
  reads/writes to TEMP files instead of the real data/ directory.
  This means tests never pollute real data and always start from a clean slate.

TEST NAMING CONVENTION:
  test_<what>_<scenario>
  e.g. test_register_success, test_register_duplicate_username

WHY TEST EDGE CASES?
  Happy-path tests only verify things work when input is perfect.
  Edge case tests catch the bugs that actually happen in production:
  duplicates, missing fields, invalid formats, wrong IDs, etc.
"""

import pytest
import json
import os
from fastapi.testclient import TestClient

# We must patch settings BEFORE importing main, so the app uses temp files
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client(tmp_path):
    """
    Creates a fresh TestClient for each test with isolated temp data files.

    tmp_path is a pytest built-in fixture: a unique temporary directory
    that is created fresh for every test function and deleted afterward.

    We override settings values directly so the app writes to tmp files.
    """
    from config import settings

    # Point storage to temp files so tests are isolated
    settings.tasks_file = str(tmp_path / "tasks.json")
    settings.users_file = str(tmp_path / "users.json")

    # Import main AFTER patching settings
    from main import app
    return TestClient(app)


# ── Registration Tests ────────────────────────────────────────────────────────

def test_register_success(client):
    """Happy path: valid data should return 201 with user info."""
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
    # CRITICAL: password must never appear in the response
    assert "password" not in data


def test_register_duplicate_username(client):
    """Registering with an existing username should return 409 Conflict."""
    payload = {"username": "alice", "email": "alice@example.com", "password": "pass1234"}
    client.post("/users/register", json=payload)  # first registration
    response = client.post("/users/register", json={
        "username": "alice",
        "email": "alice2@example.com",
        "password": "pass5678"
    })
    assert response.status_code == 409
    assert response.json()["error"] == "DuplicateUserError"


def test_register_short_username(client):
    """Username under 3 chars should fail Pydantic validation → 422."""
    response = client.post("/users/register", json={
        "username": "ab",
        "email": "ab@example.com",
        "password": "password123"
    })
    assert response.status_code == 422
    assert response.json()["error"] == "ValidationError"


def test_register_invalid_email(client):
    """Non-email string should fail EmailStr validation → 422."""
    response = client.post("/users/register", json={
        "username": "bob",
        "email": "not-an-email",
        "password": "password123"
    })
    assert response.status_code == 422


def test_register_short_password(client):
    """Password under 8 chars should fail → 422."""
    response = client.post("/users/register", json={
        "username": "carol",
        "email": "carol@example.com",
        "password": "short"
    })
    assert response.status_code == 422


def test_register_whitespace_username(client):
    """Whitespace-only username should be rejected by field_validator."""
    response = client.post("/users/register", json={
        "username": "   ",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 422


# ── Login Tests ───────────────────────────────────────────────────────────────

def test_login_success(client):
    """Valid credentials should return 200 with user info."""
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
    """Wrong password should return 401 Unauthorized."""
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
    """Login for non-existent user should return 401 (not 404 — don't reveal user existence)."""
    response = client.post("/users/login", json={
        "username": "ghost",
        "password": "anything"
    })
    assert response.status_code == 401


# ── List Users Tests ──────────────────────────────────────────────────────────

def test_list_users_empty(client):
    """GET /users on empty database should return empty list, not error."""
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == []


def test_list_users_returns_multiple(client):
    """All registered users should appear in the list."""
    client.post("/users/register", json={"username": "user1", "email": "u1@x.com", "password": "password1"})
    client.post("/users/register", json={"username": "user2", "email": "u2@x.com", "password": "password2"})
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_users_no_passwords(client):
    """Passwords must never appear in the user list response."""
    client.post("/users/register", json={"username": "frank", "email": "f@x.com", "password": "secret123"})
    users = client.get("/users").json()
    for user in users:
        assert "password" not in user


# ── Delete User Tests ─────────────────────────────────────────────────────────

def test_delete_user_success(client):
    """Deleting an existing user should return 200."""
    reg = client.post("/users/register", json={
        "username": "todelete",
        "email": "del@x.com",
        "password": "deletepass"
    })
    user_id = reg.json()["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    # Verify they're actually gone
    users = client.get("/users").json()
    assert not any(u["id"] == user_id for u in users)


def test_delete_user_not_found(client):
    """Deleting a non-existent user ID should return 404."""
    response = client.delete("/users/9999")
    assert response.status_code == 404
    assert response.json()["error"] == "UserNotFoundError"
