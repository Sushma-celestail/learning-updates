"""
tests/test_tasks.py
-------------------
Tests for task endpoints using SQLAlchemy in-memory SQLite database.

DAY 3 CHANGES:
  - Uses SQLite in-memory DB instead of temp JSON files
  - Fixtures create real DB records via API calls
  - Background task logging is NOT tested here (it writes to disk)
  - All test cases are IDENTICAL to Day 2
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

@pytest.fixture
def client():
    """Fresh in-memory SQLite database per test."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def registered_user(client):
    """Register alice and return her response dict."""
    response = client.post("/users/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "alicepass123"
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def sample_task(client, registered_user):
    """Create a task owned by alice."""
    response = client.post("/tasks", json={
        "title": "Write unit tests",
        "description": "Cover all edge cases",
        "priority": "high",
        "owner": "alice"
    })
    assert response.status_code == 201
    return response.json()


# ── Create Task Tests ─────────────────────────────────────────────────────────

def test_create_task_success(client, registered_user):
    """Happy path: valid task returns 201 with all fields."""
    response = client.post("/tasks", json={
        "title": "My first task",
        "priority": "medium",
        "owner": "alice"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My first task"
    assert data["status"] == "pending"
    assert data["priority"] == "medium"
    assert data["owner"] == "alice"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_invalid_owner(client):
    """Task for non-existent user returns 404."""
    response = client.post("/tasks", json={
        "title": "Orphan task",
        "priority": "low",
        "owner": "nobody"
    })
    assert response.status_code == 404
    assert response.json()["error"] == "UserNotFoundError"


def test_create_task_short_title(client, registered_user):
    """Title under 3 chars fails — 422."""
    response = client.post("/tasks", json={
        "title": "Hi",
        "priority": "low",
        "owner": "alice"
    })
    assert response.status_code == 422


def test_create_task_invalid_priority(client, registered_user):
    """Invalid priority enum fails — 422."""
    response = client.post("/tasks", json={
        "title": "Valid title",
        "priority": "urgent",
        "owner": "alice"
    })
    assert response.status_code == 422


def test_create_task_no_description(client, registered_user):
    """Description is optional."""
    response = client.post("/tasks", json={
        "title": "Task without description",
        "priority": "low",
        "owner": "alice"
    })
    assert response.status_code == 201
    assert response.json()["description"] is None


# ── List / Filter / Paginate Tests ────────────────────────────────────────────

def test_list_tasks_empty(client):
    """Empty database returns empty list."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status(client, registered_user):
    """?status=pending returns only pending tasks."""
    client.post("/tasks", json={"title": "Task A", "priority": "low", "owner": "alice", "status": "pending"})
    client.post("/tasks", json={"title": "Task B", "priority": "low", "owner": "alice", "status": "completed"})
    response = client.get("/tasks?status=pending")
    tasks = response.json()
    assert all(t["status"] == "pending" for t in tasks)
    assert len(tasks) == 1


def test_list_tasks_filter_by_priority(client, registered_user):
    """?priority=high returns only high tasks."""
    client.post("/tasks", json={"title": "High task", "priority": "high", "owner": "alice"})
    client.post("/tasks", json={"title": "Low task", "priority": "low", "owner": "alice"})
    tasks = client.get("/tasks?priority=high").json()
    assert all(t["priority"] == "high" for t in tasks)


def test_list_tasks_filter_by_owner(client, registered_user):
    """?owner=alice returns only alice's tasks."""
    client.post("/users/register", json={"username": "bob", "email": "bob@x.com", "password": "bobpass123"})
    client.post("/tasks", json={"title": "Alice task", "priority": "low", "owner": "alice"})
    client.post("/tasks", json={"title": "Bob task", "priority": "low", "owner": "bob"})
    tasks = client.get("/tasks?owner=alice").json()
    assert all(t["owner"] == "alice" for t in tasks)
    assert len(tasks) == 1


def test_list_tasks_pagination(client, registered_user):
    """Pagination slices results correctly."""
    for i in range(1, 6):
        client.post("/tasks", json={"title": f"Task {i}", "priority": "low", "owner": "alice"})

    assert len(client.get("/tasks?page=1&limit=2").json()) == 2
    assert len(client.get("/tasks?page=2&limit=2").json()) == 2
    assert len(client.get("/tasks?page=3&limit=2").json()) == 1
    assert client.get("/tasks?page=10&limit=2").json() == []


# ── Get By ID Tests ───────────────────────────────────────────────────────────

def test_get_task_by_id_success(client, sample_task):
    """Fetching existing task by ID returns 200."""
    task_id = sample_task["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_get_task_not_found(client):
    """Fetching non-existent task returns 404."""
    response = client.get("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["error"] == "TaskNotFoundError"


# ── PUT Tests ─────────────────────────────────────────────────────────────────

def test_put_task_success(client, sample_task, registered_user):
    """PUT replaces all fields and refreshes updated_at."""
    task_id = sample_task["id"]
    response = client.put(f"/tasks/{task_id}", json={
        "title": "Completely new title",
        "description": "New description",
        "priority": "low",
        "status": "in_progress",
        "owner": "alice"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Completely new title"
    assert data["status"] == "in_progress"
    assert data["created_at"] == sample_task["created_at"]


def test_put_task_not_found(client, registered_user):
    """PUT on non-existent task returns 404."""
    response = client.put("/tasks/9999", json={
        "title": "Ghost task",
        "priority": "low",
        "status": "pending",
        "owner": "alice"
    })
    assert response.status_code == 404


# ── PATCH Tests ───────────────────────────────────────────────────────────────

def test_patch_task_status_only(client, sample_task):
    """PATCH with only status changes status, nothing else."""
    task_id = sample_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "completed"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["title"] == sample_task["title"]
    assert data["priority"] == sample_task["priority"]


def test_patch_task_not_found(client):
    """PATCH on non-existent task returns 404."""
    response = client.patch("/tasks/9999", json={"status": "completed"})
    assert response.status_code == 404
    assert response.json()["error"] == "TaskNotFoundError"


# ── Delete Tests ──────────────────────────────────────────────────────────────

def test_delete_task_success(client, sample_task):
    """Deleting existing task returns 200 and removes it."""
    task_id = sample_task["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_delete_task_not_found(client):
    """Deleting non-existent task returns 404."""
    response = client.delete("/tasks/9999")
    assert response.status_code == 404


# ── Error Format Tests ────────────────────────────────────────────────────────

def test_error_response_format(client):
    """All errors include error, message, status_code fields."""
    data = client.get("/tasks/9999").json()
    assert "error" in data
    assert "message" in data
    assert "status_code" in data
    assert data["status_code"] == 404
