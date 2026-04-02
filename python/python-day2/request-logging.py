from fastapi import FastAPI, Request
import time
from datetime import datetime

app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)

    log_line = (
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"{request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Time: {duration_ms}ms\n"
    )

    with open("api_logs.txt", "a") as f:
        f.write(log_line)

    print(log_line, end="")
    return response



@app.get("/")
def home():
    return {"message": "API working"}

@app.get("/tasks")
def get_tasks():
    return [
        {"id": 1, "title": "Task 1"},
        {"id": 2, "title": "Task 2"}
    ]
