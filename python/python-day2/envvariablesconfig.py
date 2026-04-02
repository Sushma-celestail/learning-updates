
"""
### Q16. Environment Variables and Config 

Topics: Config, Environment Variables, Pydantic 

Problem Statement: 

Create a Settings class using Pydantic's BaseSettings that loads APP_NAME, DEBUG, JSON_DB_PATH, and LOG_LEVEL from a .env file. Use these settings in your FastAPI app startup. 

Input: 

# .env file content: 

APP_NAME=TaskAPI 

DEBUG=true 

JSON_DB_PATH=./data/tasks.json 

LOG_LEVEL=INFO 

Output: 

# On app startup: 

App: TaskAPI | Debug: True | DB: ./data/tasks.json 

Constraints: 

Use pydantic-settings package 

Do NOT hardcode any config values in the source code 

Load settings using model_config = SettingsConfigDict(env_file=".env") 

Settings must be a singleton used across the app 

 
"""
from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

#  Settings Class
class Settings(BaseSettings):
    app_name: str
    debug: bool
    json_db_path: str
    log_level: str

    model_config = SettingsConfigDict(env_file=".env")


#  Singleton Settings (important)
@lru_cache
def get_settings() -> Settings:
    return Settings()


#  FastAPI App
app = FastAPI()


#  Startup Event
@app.on_event("startup")
def startup():
    s = get_settings()
    print(f"App: {s.app_name} | Debug: {s.debug} | DB: {s.json_db_path}")


#  Sample data
tasks = [
    {"id": 1, "title": "Task 1"},
    {"id": 2, "title": "Task 2"}
]

#  Get all tasks
@app.get("/tasks")
def get_tasks():
    return tasks

#  Get task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return {"error": "Task not found"}
    return task