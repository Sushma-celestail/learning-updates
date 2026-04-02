from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum

app = FastAPI()

#  Enum for status
class StatusEnum(str, Enum):
    pending = "pending"
    completed = "completed"

#  Request model
class Task(BaseModel):
    title: str
    status: StatusEnum

#  In-memory DB
tasks = []
task_id_counter = 1

#  Health check
@app.get("/")
def health():
    return {"message": "API is running"}

# Create task
@app.post("/tasks")
def create_task(task: Task):
    global task_id_counter
    new_task = {"id": task_id_counter, **task.dict()}
    tasks.append(new_task)
    task_id_counter += 1
    return new_task

#  Get all tasks
@app.get("/tasks")
def get_tasks():
    return tasks

#  Get task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

#  Update task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated: Task):
    for t in tasks:
        if t["id"] == task_id:
            t.update(updated.dict())
            return t
    raise HTTPException(status_code=404, detail="Task not found")

#  Delete task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks
    for t in tasks:
        if t["id"] == task_id:
            tasks = [task for task in tasks if task["id"] != task_id]
            return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Task not found")