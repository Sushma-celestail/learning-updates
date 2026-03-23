from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

tasks = [
    {"id": 1, "title": "Learn FastAPI"},
    {"id": 2, "title": "Build project"}
]

class TaskNotFoundError(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "TaskNotFoundError",
            "message": str(exc),
            "status_code": 404
        }
    )


def get_task_or_404(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise TaskNotFoundError(task_id)
    return task


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    return get_task_or_404(task_id)