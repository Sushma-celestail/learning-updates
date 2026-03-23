"""
services/task_service.py
------------------------
Business logic layer for task operations.

KEY BUSINESS RULES IMPLEMENTED HERE:
  - Tasks must be owned by an existing user (UserNotFoundError if not)
  - created_at and updated_at are managed by the service, not the client
  - PATCH (partial update) only changes fields explicitly sent by the client
  - Filtering and pagination are pure Python operations on the list

DESIGN NOTES:
  The service receives and returns Pydantic models / plain dicts.
  It never builds HTTP responses — that's the router's job.
  It never touches files directly — that's the repository's job.
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
    """
    Encapsulates all task business logic.

    Two repositories are injected:
      - task_repo  : for task CRUD
      - user_repo  : to validate that the task owner exists
    """

    def __init__(self, task_repo: BaseRepository, user_repo: BaseRepository):
        self.task_repo = task_repo
        self.user_repo = user_repo

    def create_task(self, task_data: TaskCreate) -> TaskResponse:
        """
        Create a new task.
        Rules:
          1. Owner (username) must exist in the user database
          2. created_at and updated_at are set to the current time
        """
        # Rule 1: Validate owner exists
        self._validate_owner(task_data.owner)

        now = datetime.now().isoformat()
        record = {
            "title": task_data.title,
            "description": task_data.description,
            "status": task_data.status.value,      # store the string "pending", not the enum
            "priority": task_data.priority.value,
            "owner": task_data.owner,
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
        """
        Return a filtered, paginated list of tasks.

        Filtering: done with Python list comprehensions (no SQL needed).
        Pagination: slice the filtered list based on page and limit.

        WHY page-based instead of cursor-based?
        Page-based is simpler to test with Postman and meets the project spec.
        Cursor-based would be better for large datasets in production.
        """
        tasks = self.task_repo.find_all()

        # Apply filters (each is optional — skip if not provided)
        if status:
            tasks = [t for t in tasks if t["status"] == status.value]
        if priority:
            tasks = [t for t in tasks if t["priority"] == priority.value]
        if owner:
            tasks = [t for t in tasks if t["owner"] == owner]

        # Pagination: calculate slice indices
        # page=1, limit=5 → tasks[0:5]
        # page=2, limit=5 → tasks[5:10]
        start = (page - 1) * limit
        end = start + limit
        paginated = tasks[start:end]

        # If page is beyond data range, return empty list (not an error)
        return [self._to_response(t) for t in paginated]

    def get_task_by_id(self, task_id: int) -> TaskResponse:
        """Fetch a single task. Raises TaskNotFoundError if missing."""
        task = self.task_repo.find_by_id(task_id)
        if task is None:
            logger.error(f"Task id={task_id} not found")
            raise TaskNotFoundError(task_id)
        return self._to_response(task)

    def update_task(self, task_id: int, task_data: TaskUpdate) -> TaskResponse:
        """
        Full replacement (PUT): replace all mutable fields.
        updated_at is refreshed; created_at is preserved from original.
        """
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
            "owner": task_data.owner,
            "created_at": existing["created_at"],    # preserve original creation time
            "updated_at": datetime.now().isoformat(),
        }

        result = self.task_repo.update(task_id, updated_record)
        logger.info(f"Task id={task_id} fully updated")
        return self._to_response(result)

    def patch_task(self, task_id: int, patch_data: TaskPatch) -> TaskResponse:
        """
        Partial update (PATCH): only change the fields that were sent.

        How it works:
          1. Fetch the existing record
          2. Call model_dump(exclude_unset=True) to get only fields the client sent
          3. Merge those fields into the existing record dict
          4. Save the merged result
        """
        existing = self.task_repo.find_by_id(task_id)
        if existing is None:
            logger.error(f"Patch failed: task id={task_id} not found")
            raise TaskNotFoundError(task_id)

        # exclude_unset=True: only includes fields explicitly set in the request body
        # If client sends {"status": "completed"}, this gives {"status": "completed"}
        # NOT {"status": "completed", "title": None, "priority": None, ...}
        changes = patch_data.model_dump(exclude_unset=True)

        # Convert enum objects to their string values for JSON storage
        if "status" in changes and changes["status"] is not None:
            changes["status"] = changes["status"].value
        if "priority" in changes and changes["priority"] is not None:
            changes["priority"] = changes["priority"].value

        if "owner" in changes:
            self._validate_owner(changes["owner"])

        # Merge: start with existing, overwrite only changed fields
        merged = {**existing, **changes, "updated_at": datetime.now().isoformat()}

        result = self.task_repo.update(task_id, merged)
        logger.info(f"Task id={task_id} partially updated: {list(changes.keys())}")
        return self._to_response(result)

    def delete_task(self, task_id: int) -> None:
        """Delete a task by ID. Raises TaskNotFoundError if not found."""
        success = self.task_repo.delete(task_id)
        if not success:
            logger.error(f"Delete failed: task id={task_id} not found")
            raise TaskNotFoundError(task_id)
        logger.info(f"Task id={task_id} deleted")

    # ── Private helpers ───────────────────────────────────────────────

    def _validate_owner(self, username: str) -> None:
        """
        Verify the given username exists in the user repository.
        Raises UserNotFoundError if not found.
        This cross-entity validation is business logic — it belongs here.
        """
        users = self.user_repo.find_all()
        if not any(u["username"] == username for u in users):
            raise UserNotFoundError(username)

    def _to_response(self, record: Dict[str, Any]) -> TaskResponse:
        """Convert a raw storage dict to a TaskResponse Pydantic model."""
        return TaskResponse(
            id=record["id"],
            title=record["title"],
            description=record.get("description"),
            status=TaskStatus(record["status"]),
            priority=TaskPriority(record["priority"]),
            owner=record["owner"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
        )
