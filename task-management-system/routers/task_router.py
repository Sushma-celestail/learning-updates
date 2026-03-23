"""
routers/task_router.py
----------------------
HTTP layer for task endpoints.

DB RESPONSIBILITIES:
  - PostgreSQL → users (owner validation)
  - MongoDB    → tasks + subtasks (CRUD)
  - Logging    → handled by middleware (no DB calls here)

QUERY PARAMETERS FOR GET /tasks:
  ?status=pending&priority=high&page=2&limit=5
  maps to: status=TaskStatus.PENDING, priority=TaskPriority.HIGH, page=2, limit=5

NOTE ON PUT vs PATCH:
  PUT   /tasks/{id} → full replacement, all fields required (TaskUpdate schema)
  PATCH /tasks/{id} → partial update, only send what changed (TaskPatch schema)
"""

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from bson import ObjectId

from models.schemas import TaskCreate, TaskUpdate, TaskPatch, TaskResponse, MessageResponse
from models.enums import TaskStatus, TaskPriority
from database.mongodb import get_mongo_db
from database.postgresql import get_postgres_db
from config import settings

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def serialize_task(task: dict) -> dict:
    """
    MongoDB returns _id as ObjectId — convert to string so
    it can be serialized to JSON and returned to the client.
    """
    task["id"] = str(task.pop("_id"))
    return task


async def validate_owner(owner: str, pg_db: AsyncSession) -> None:
    """
    Check PostgreSQL users table to confirm the task owner exists.
    Raises 404 if not found — keeps validation in one place.
    """
    result = await pg_db.execute(
        "SELECT id FROM users WHERE username = :username",
        {"username": owner}
    )
    user = result.fetchone()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner '{owner}' not found in users"
        )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task with optional subtasks",
)
async def create_task(
    task_data: TaskCreate,
    pg_db: AsyncSession = Depends(get_postgres_db),   # validate owner
    mongo_db=Depends(get_mongo_db),                   # store task
):
    """
    1. Validate owner exists in PostgreSQL
    2. Save task + subtasks into MongoDB
    Middleware auto-logs this request — no manual log call needed.
    """
    # Step 1 — confirm owner exists in PostgreSQL
    await validate_owner(task_data.owner, pg_db)

    # Step 2 — build task document for MongoDB
    task_doc = {
        "title": task_data.title,
        "description": getattr(task_data, "description", ""),
        "status": task_data.status.value if task_data.status else TaskStatus.PENDING.value,
        "priority": task_data.priority.value if task_data.priority else TaskPriority.MEDIUM.value,
        "owner": task_data.owner,
        "subtasks": [
            {"title": sub.title, "done": False}
            for sub in (task_data.subtasks or [])
        ],
    }

    # Step 3 — insert into MongoDB
    result = await mongo_db["tasks"].insert_one(task_doc)
    task_doc["id"] = str(result.inserted_id)
    task_doc.pop("_id", None)

    return task_doc


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="List tasks with optional filters and pagination",
)
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    owner: Optional[str] = Query(None, description="Filter by owner username"),
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    limit: int = Query(10, ge=1, le=100, description="Results per page (max 100)"),
    mongo_db=Depends(get_mongo_db),
):
    """
    List tasks from MongoDB with optional filters.
    Combine freely: ?status=pending&priority=high&owner=alice&page=2&limit=5
    """
    # Build MongoDB filter from query params
    filters = {}
    if status:
        filters["status"] = status.value
    if priority:
        filters["priority"] = priority.value
    if owner:
        filters["owner"] = owner

    skip = (page - 1) * limit

    cursor = mongo_db["tasks"].find(filters).skip(skip).limit(limit)
    tasks = await cursor.to_list(length=limit)

    return [serialize_task(task) for task in tasks]


@router.get(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a task by ID",
)
async def get_task(
    task_id: str,
    mongo_db=Depends(get_mongo_db),
):
    """Fetch a single task by its MongoDB ObjectId. Returns 404 if not found."""
    task = await mongo_db["tasks"].find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return serialize_task(task)


@router.put(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Full update (replace all fields)",
)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    pg_db: AsyncSession = Depends(get_postgres_db),   # re-validate owner
    mongo_db=Depends(get_mongo_db),
):
    """
    Full update: ALL fields must be provided.
    Re-validates owner in PostgreSQL before updating MongoDB.
    """
    await validate_owner(task_data.owner, pg_db)

    update_doc = {
        "title": task_data.title,
        "description": getattr(task_data, "description", ""),
        "status": task_data.status.value,
        "priority": task_data.priority.value,
        "owner": task_data.owner,
        "subtasks": [
            {"title": sub.title, "done": sub.done}
            for sub in (task_data.subtasks or [])
        ],
    }

    result = await mongo_db["tasks"].find_one_and_replace(
        {"_id": ObjectId(task_id)},
        update_doc,
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return serialize_task(result)


@router.patch(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Partial update (send only changed fields)",
)
async def patch_task(
    task_id: str,
    patch_data: TaskPatch,
    mongo_db=Depends(get_mongo_db),
):
    """
    Partial update: only fields you include will change.
    Example: {"status": "completed"} updates only the status.
    """
    # Only include fields that were actually sent
    patch_doc = {
        k: v.value if hasattr(v, "value") else v
        for k, v in patch_data.model_dump(exclude_unset=True).items()
    }

    if not patch_doc:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    result = await mongo_db["tasks"].find_one_and_update(
        {"_id": ObjectId(task_id)},
        {"$set": patch_doc},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return serialize_task(result)


@router.patch(
    "/{task_id}/subtasks/{subtask_index}",
    status_code=status.HTTP_200_OK,
    summary="Mark a subtask as done or not done",
)
async def update_subtask(
    task_id: str,
    subtask_index: int,
    done: bool = Query(..., description="True to mark done, False to unmark"),
    mongo_db=Depends(get_mongo_db),
):
    """
    Update a single subtask's done status by its index.
    Example: PATCH /tasks/abc123/subtasks/0?done=true
    """
    result = await mongo_db["tasks"].find_one_and_update(
        {"_id": ObjectId(task_id)},
        {"$set": {f"subtasks.{subtask_index}.done": done}},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return serialize_task(result)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a task",
)
async def delete_task(
    task_id: str,
    mongo_db=Depends(get_mongo_db),
):
    """Delete a task and all its subtasks by ID. Returns 404 if not found."""
    result = await mongo_db["tasks"].find_one_and_delete({"_id": ObjectId(task_id)})
    if not result:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return MessageResponse(message=f"Task {task_id} deleted successfully")