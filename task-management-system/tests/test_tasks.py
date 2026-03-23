"""
tests/test_tasks.py
-------------------
Tests for all task endpoints, including filters, pagination, and edge cases.

FIXTURE DESIGN:
  'client'       → fresh TestClient with temp files (same as user tests)
  'registered_user' → creates a user first (tasks need an owner)
  'sample_task'  → creates a task, returns its response dict

  Fixtures compose: sample_task depends on registered_user which depends on client.
  pytest resolves the whole chain automatically.
"""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client(tmp_path):
    """Fresh TestClient with isolated temp storage for each test."""
    from config import settings
    settings.tasks_file = str(tmp_path / "tasks.json")
    settings.users_file = str(tmp_path / "users.json")
    from main import app
    return TestClient(app)


from fastapi.testclient import TestClient


@pytest.fixture
def registered_user(client):
    """Register a test user and return the response dict."""
    response = client.post("/users/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "alicepass123"
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def sample_task(client, registered_user):
    """Create a sample task owned by alice and return the response dict."""
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
    assert data["status"] == "pending"       # default status
    assert data["priority"] == "medium"
    assert data["owner"] == "alice"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_invalid_owner(client):
    """Creating a task for a non-existent user should return 404."""
    response = client.post("/tasks", json={
        "title": "Orphan task",
        "priority": "low",
        "owner": "nobody"
    })
    assert response.status_code == 404
    assert response.json()["error"] == "UserNotFoundError"


def test_create_task_short_title(client, registered_user):
    """Title under 3 chars should fail Pydantic validation → 422."""
    response = client.post("/tasks", json={
        "title": "Hi",
        "priority": "low",
        "owner": "alice"
    })
    assert response.status_code == 422


def test_create_task_invalid_priority(client, registered_user):
    """Invalid enum value for priority should fail → 422."""
    response = client.post("/tasks", json={
        "title": "Valid title",
        "priority": "urgent",   # not a valid TaskPriority value
        "owner": "alice"
    })
    assert response.status_code == 422


def test_create_task_invalid_status(client, registered_user):
    """Invalid enum value for status should fail → 422."""
    response = client.post("/tasks", json={
        "title": "Valid title",
        "priority": "high",
        "status": "done",       # not a valid TaskStatus value
        "owner": "alice"
    })
    assert response.status_code == 422


def test_create_task_long_description(client, registered_user):
    """Description over 500 chars should fail → 422."""
    response = client.post("/tasks", json={
        "title": "Valid title",
        "description": "x" * 501,
        "priority": "low",
        "owner": "alice"
    })
    assert response.status_code == 422


def test_create_task_no_description(client, registered_user):
    """Description is optional — omitting it should succeed."""
    response = client.post("/tasks", json={
        "title": "Task without description",
        "priority": "low",
        "owner": "alice"
    })
    assert response.status_code == 201
    assert response.json()["description"] is None


# ── List / Filter / Paginate Tests ────────────────────────────────────────────

def test_list_tasks_empty(client):
    """GET /tasks on empty database should return [] not an error."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status(client, registered_user):
    """?status=pending should return only pending tasks."""
    client.post("/tasks", json={"title": "Task A", "priority": "low", "owner": "alice", "status": "pending"})
    client.post("/tasks", json={"title": "Task B", "priority": "low", "owner": "alice", "status": "completed"})

    response = client.get("/tasks?status=pending")
    tasks = response.json()
    assert all(t["status"] == "pending" for t in tasks)
    assert len(tasks) == 1


def test_list_tasks_filter_by_priority(client, registered_user):
    """?priority=high should return only high-priority tasks."""
    client.post("/tasks", json={"title": "High task", "priority": "high", "owner": "alice"})
    client.post("/tasks", json={"title": "Low task", "priority": "low", "owner": "alice"})

    response = client.get("/tasks?priority=high")
    tasks = response.json()
    assert all(t["priority"] == "high" for t in tasks)


def test_list_tasks_filter_by_owner(client, registered_user):
    """?owner=alice should return only alice's tasks."""
    # Register second user
    client.post("/users/register", json={"username": "bob", "email": "bob@x.com", "password": "bobpass123"})
    client.post("/tasks", json={"title": "Alice task", "priority": "low", "owner": "alice"})
    client.post("/tasks", json={"title": "Bob task", "priority": "low", "owner": "bob"})

    response = client.get("/tasks?owner=alice")
    tasks = response.json()
    assert all(t["owner"] == "alice" for t in tasks)
    assert len(tasks) == 1


def test_list_tasks_pagination(client, registered_user):
    """page and limit should slice results correctly."""
    # Create 5 tasks
    for i in range(1, 6):
        client.post("/tasks", json={"title": f"Task {i}", "priority": "low", "owner": "alice"})

    # Page 1, limit 2 → tasks 1-2
    page1 = client.get("/tasks?page=1&limit=2").json()
    assert len(page1) == 2

    # Page 2, limit 2 → tasks 3-4
    page2 = client.get("/tasks?page=2&limit=2").json()
    assert len(page2) == 2

    # Page 3, limit 2 → task 5
    page3 = client.get("/tasks?page=3&limit=2").json()
    assert len(page3) == 1

    # Page beyond data → empty list, not error
    page4 = client.get("/tasks?page=10&limit=2").json()
    assert page4 == []


# ── Get By ID Tests ───────────────────────────────────────────────────────────

def test_get_task_by_id_success(client, sample_task):
    """Fetching an existing task by ID should return 200 with full data."""
    task_id = sample_task["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "Write unit tests"


def test_get_task_not_found(client):
    """Fetching a non-existent task ID should return 404."""
    response = client.get("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["error"] == "TaskNotFoundError"


# ── Full Update (PUT) Tests ───────────────────────────────────────────────────

def test_put_task_success(client, sample_task, registered_user):
    """PUT should replace all fields and refresh updated_at."""
    task_id = sample_task["id"]
    original_updated_at = sample_task["updated_at"]

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
    assert data["priority"] == "low"
    # updated_at must have changed
    assert data["updated_at"] >= original_updated_at
    # created_at must be preserved
    assert data["created_at"] == sample_task["created_at"]


def test_put_task_not_found(client, registered_user):
    """PUT on non-existent task should return 404."""
    response = client.put("/tasks/9999", json={
        "title": "Ghost task",
        "priority": "low",
        "status": "pending",
        "owner": "alice"
    })
    assert response.status_code == 404


# ── Partial Update (PATCH) Tests ──────────────────────────────────────────────

def test_patch_task_status_only(client, sample_task):
    """PATCH with only status should change status but nothing else."""
    task_id = sample_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "completed"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    # Other fields unchanged
    assert data["title"] == sample_task["title"]
    assert data["priority"] == sample_task["priority"]
    assert data["owner"] == sample_task["owner"]


def test_patch_task_multiple_fields(client, sample_task):
    """PATCH can update multiple fields simultaneously."""
    task_id = sample_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={
        "status": "in_progress",
        "priority": "medium",
        "title": "Updated title"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["priority"] == "medium"
    assert data["title"] == "Updated title"


def test_patch_task_not_found(client):
    """PATCH on non-existent task should return 404."""
    response = client.patch("/tasks/9999", json={"status": "completed"})
    assert response.status_code == 404
    assert response.json()["error"] == "TaskNotFoundError"


# ── Delete Task Tests ─────────────────────────────────────────────────────────

def test_delete_task_success(client, sample_task):
    """Deleting an existing task should return 200 and remove it."""
    task_id = sample_task["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    # Verify it's gone
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_task_not_found(client):
    """Deleting a non-existent task should return 404."""
    response = client.delete("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["error"] == "TaskNotFoundError"


# ── Error Response Format Tests ───────────────────────────────────────────────

def test_error_response_format(client):
    """All errors must include 'error', 'message', and 'status_code' fields."""
    response = client.get("/tasks/9999")
    data = response.json()
    assert "error" in data
    assert "message" in data
    assert "status_code" in data
    assert data["status_code"] == 404
