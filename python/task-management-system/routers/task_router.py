"""
routers/task_router.py
----------------------
HTTP layer for task endpoints.

DAY 3 CHANGES:
  - Dependency now injects SQLAlchemy session + SQLAlchemyRepository
  - POST /tasks adds BackgroundTasks to log notifications
  - All endpoint logic is IDENTICAL to Day 2
"""

import os
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, Query, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Optional

from models.schemas import TaskCreate, TaskUpdate, TaskPatch, TaskResponse, MessageResponse
from models.enums import TaskStatus, TaskPriority
from models.db_models import TaskModel, UserModel
from services.task_service import TaskService
from repositories.sqlalchemy_repository import SQLAlchemyRepository
from database import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])

logger = logging.getLogger(__name__)


# ── Background Task ───────────────────────────────────────────────────────────

def log_task_notification(title: str, owner: str):
    """
    Background task: writes to notifications.log after task creation.

    This runs AFTER the HTTP response is sent — the user doesn't wait for it.
    FastAPI runs it in a thread pool automatically.
    """
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] Task '{title}' created by {owner} — notification sent\n"

    with open("logs/notifications.log", "a", encoding="utf-8") as f:
        f.write(message)

    logger.info(f"Background notification logged for task '{title}'")


# ── Dependency Provider ───────────────────────────────────────────────────────

def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """
    DAY 3: Inject SQLAlchemy session and build repositories.
    The db session comes from FastAPI's Depends(get_db).
    """
    task_repo = SQLAlchemyRepository(db=db, model=TaskModel)
    user_repo = SQLAlchemyRepository(db=db, model=UserModel)
    return TaskService(task_repo=task_repo, user_repo=user_repo)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,          # DAY 3: background task injection
    service: TaskService = Depends(get_task_service),
):
    """
    Create a task. After responding to the client, logs a notification
    to notifications.log in the background.
    """
    result = service.create_task(task_data)

    # Add background task — runs AFTER response is sent
    background_tasks.add_task(log_task_notification, task_data.title, task_data.owner)

    return result


@router.get(
    "",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List tasks with optional filters and pagination",
)
def list_tasks(
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    owner: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    service: TaskService = Depends(get_task_service),
):
    return service.get_all_tasks(status=status, priority=priority, owner=owner, page=page, limit=limit)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a task by ID",
)
def get_task(task_id: int, service: TaskService = Depends(get_task_service)):
    return service.get_task_by_id(task_id)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Full update (replace all fields)",
)
def update_task(task_id: int, task_data: TaskUpdate, service: TaskService = Depends(get_task_service)):
    return service.update_task(task_id, task_data)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Partial update (send only changed fields)",
)
def patch_task(task_id: int, patch_data: TaskPatch, service: TaskService = Depends(get_task_service)):
    return service.patch_task(task_id, patch_data)


@router.delete(
    "/{task_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a task",
)
def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    service.delete_task(task_id)
    return MessageResponse(message=f"Task {task_id} deleted successfully")
