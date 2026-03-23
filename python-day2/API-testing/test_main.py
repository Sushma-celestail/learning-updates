"""
### Q17. API Testing with pytest 

Topics: Testing, pytest, TestClient 

Problem Statement: 

Write automated tests for the Task API using pytest and FastAPI's TestClient. Cover: successful creation, listing, fetching by ID, updating, deleting, 404 for missing task, and validation error for bad payload. 

Input: 

# Test functions: 

test_health_check() 

test_create_task() 

test_create_task_invalid_status() 

test_get_tasks() 

test_get_task_not_found() 

test_update_task() 

test_delete_task() 

Output: 

# Terminal output: 

7 passed in 0.45s 

Constraints: 

Use from fastapi.testclient import TestClient 

Test both success (2xx) and failure (4xx) cases 

Assert response status codes AND response body content 

Minimum 7 test cases 
"""


from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

#  1. Health check
def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}

#  2. Create task
def test_create_task():
    response = client.post("/tasks", json={
        "title": "Test Task",
        "status": "pending"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"

#  3. Invalid status (validation error)
def test_create_task_invalid_status():
    response = client.post("/tasks", json={
        "title": "Bad Task",
        "status": "wrong"
    })
    assert response.status_code == 422  # validation error

#  4. Get all tasks
def test_get_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

#  5. Get task not found
def test_get_task_not_found():
    response = client.get("/tasks/999")
    assert response.status_code == 404

#  6. Update task
def test_update_task():
    # create first
    create = client.post("/tasks", json={
        "title": "Update Me",
        "status": "pending"
    })
    task_id = create.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={
        "title": "Updated",
        "status": "completed"
    })

    assert response.status_code == 200
    assert response.json()["title"] == "Updated"

#  7. Delete task
def test_delete_task():
    # create first
    create = client.post("/tasks", json={
        "title": "Delete Me",
        "status": "pending"
    })
    task_id = create.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Deleted"