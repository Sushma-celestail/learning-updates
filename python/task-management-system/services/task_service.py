"""
services/task_service.py
------------------------
Business logic for task operations.

DAY 3 CHANGES:
  - _validate_owner() uses find_by_field() for SQLAlchemy
  - get_all_tasks() filtering still works (Python-level filtering on dicts)
  - Everything else identical to Day 2
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository
from models.schemas import TaskCreate, TaskUpdate, TaskPatch, TaskResponse
from models.enums import TaskStatus, TaskPriority
from exceptions.custom_exceptions import TaskNotFoundError, UserNotFoundError

logger = logging.getLogger(__name__)


class TaskService:
    """Encapsulates all task business logic."""

    def __init__(self, task_repo: BaseRepository, user_repo: BaseRepository):
        self.task_repo = task_repo
        self.user_repo = user_repo

    def create_task(self, task_data: TaskCreate) -> TaskResponse:
        """Create a new task. Owner must exist."""
        self._validate_owner(task_data.owner)

        now = datetime.now()
        record = {
            "title": task_data.title,
            "description": task_data.description,
            "status": task_data.status.value,
            "priority": task_data.priority.value,
            "owner_username": task_data.owner,  # DB column name
            "created_at": now,
            "updated_at": now,
        }

        saved = self.task_repo.save(record)
        logger.info(f"Task '{task_data.title}' created with id={saved['id']} by '{task_data.owner}'")
        return self._to_response(saved)

    def get_all_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        owner: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> List[TaskResponse]:
        """Return filtered, paginated list of tasks."""
        tasks = self.task_repo.find_all()

        if status:
            tasks = [t for t in tasks if t["status"] == status.value]
        if priority:
            tasks = [t for t in tasks if t["priority"] == priority.value]
        if owner:
            tasks = [t for t in tasks if t.get("owner") == owner]

        start = (page - 1) * limit
        end = start + limit
        return [self._to_response(t) for t in tasks[start:end]]

    def get_task_by_id(self, task_id: int) -> TaskResponse:
        """Fetch a single task."""
        task = self.task_repo.find_by_id(task_id)
        if task is None:
            logger.error(f"Task id={task_id} not found")
            raise TaskNotFoundError(task_id)
        return self._to_response(task)

    def update_task(self, task_id: int, task_data: TaskUpdate) -> TaskResponse:
        """Full replacement (PUT)."""
        existing = self.task_repo.find_by_id(task_id)
        if existing is None:
            logger.error(f"Update failed: task id={task_id} not found")
            raise TaskNotFoundError(task_id)

        self._validate_owner(task_data.owner)

        updated_record = {
            "title": task_data.title,
            "description": task_data.description,
            "status": task_data.status.value,
            "priority": task_data.priority.value,
            "owner_username": task_data.owner,
            "created_at": existing["created_at"],
            "updated_at": datetime.now(),
        }

        result = self.task_repo.update(task_id, updated_record)
        logger.info(f"Task id={task_id} fully updated")
        return self._to_response(result)

    def patch_task(self, task_id: int, patch_data: TaskPatch) -> TaskResponse:
        """Partial update (PATCH)."""
        existing = self.task_repo.find_by_id(task_id)
        if existing is None:
            logger.error(f"Patch failed: task id={task_id} not found")
            raise TaskNotFoundError(task_id)

        changes = patch_data.model_dump(exclude_unset=True)

        if "status" in changes and changes["status"] is not None:
            changes["status"] = changes["status"].value
        if "priority" in changes and changes["priority"] is not None:
            changes["priority"] = changes["priority"].value
        if "owner" in changes:
            self._validate_owner(changes["owner"])
            changes["owner_username"] = changes.pop("owner")

        merged = {**existing, **changes, "updated_at": datetime.now()}
        result = self.task_repo.update(task_id, merged)
        logger.info(f"Task id={task_id} partially updated: {list(changes.keys())}")
        return self._to_response(result)

    def delete_task(self, task_id: int) -> None:
        """Delete a task by ID."""
        success = self.task_repo.delete(task_id)
        if not success:
            logger.error(f"Delete failed: task id={task_id} not found")
            raise TaskNotFoundError(task_id)
        logger.info(f"Task id={task_id} deleted")

    def _validate_owner(self, username: str) -> None:
        """Verify username exists in users table."""
        if hasattr(self.user_repo, 'find_by_field'):
            user = self.user_repo.find_by_field("username", username)
        else:
            users = self.user_repo.find_all()
            user = next((u for u in users if u["username"] == username), None)

        if not user:
            raise UserNotFoundError(username)

    def _to_response(self, record: Dict[str, Any]) -> TaskResponse:
        return TaskResponse(
            id=record["id"],
            title=record["title"],
            description=record.get("description"),
            status=TaskStatus(record["status"]),
            priority=TaskPriority(record["priority"]),
            owner=record.get("owner", record.get("owner_username", "")),
            created_at=record["created_at"],
            updated_at=record["updated_at"],
        )
