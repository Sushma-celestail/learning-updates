"""
repositories/sqlalchemy_repository.py
--------------------------------------
SQLAlchemy implementation of BaseRepository.

DAY 3 NEW FILE — replaces json_repository.py.

KEY DESIGN: This class implements the EXACT SAME interface as JSONRepository.
  - Same method names: save, find_by_id, find_all, update, delete
  - Same return types: Dict or List[Dict]
  - Services and routers are COMPLETELY UNCHANGED

This proves DIP (Dependency Inversion Principle):
  The service layer depends on BaseRepository (abstraction).
  Swapping json_repository → sqlalchemy_repository requires ZERO
  changes to any service or router file.

HOW SQLALCHEMY ORM WORKS:
  Instead of writing SQL like:
    SELECT * FROM tasks WHERE id = 1

  We write Python like:
    db.query(TaskModel).filter(TaskModel.id == 1).first()

  SQLAlchemy translates this to SQL automatically.

SESSIONS:
  The db session is injected into this repository from FastAPI's
  Depends(get_db). Each request gets its own session (unit of work).
  We never create sessions here — we receive them from outside (DIP).
"""

import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class SQLAlchemyRepository(BaseRepository):
    """
    Generic SQLAlchemy repository that works for ANY model.

    Args:
        db         : SQLAlchemy session (injected by FastAPI)
        model      : The SQLAlchemy model class (UserModel or TaskModel)
        owner_field: The field name used for 'owner' in tasks ("owner_username")
                     For users this is None.

    WHY GENERIC?
      One class handles both users and tasks — just pass a different model.
      This is the same approach as JSONRepository using collection="tasks"/"users".
    """

    def __init__(self, db: Session, model):
        self.db = db
        self.model = model

    def find_all(self) -> List[Dict[str, Any]]:
        """Return all records as a list of dicts."""
        records = self.db.query(self.model).all()
        return [self._to_dict(r) for r in records]

    def find_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Return a single record by ID, or None if not found."""
        record = self.db.query(self.model).filter(
            self.model.id == record_id
        ).first()
        return self._to_dict(record) if record else None

    def find_by_field(self, field_name: str, value: Any) -> Optional[Dict[str, Any]]:
        """
        Find a record by any field value.
        Used for username lookups in user service.
        Example: find_by_field("username", "alice")
        """
        column = getattr(self.model, field_name, None)
        if column is None:
            return None
        record = self.db.query(self.model).filter(column == value).first()
        return self._to_dict(record) if record else None

    def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a new record into the database.

        Steps:
          1. Create a model instance from the dict
          2. Add it to the session (staged for insert)
          3. Commit the transaction (actually writes to DB)
          4. Refresh to get the auto-generated ID back
          5. Return as dict
        """
        # Remove 'id' if present — DB auto-generates it
        data.pop("id", None)

        record = self.model(**data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)   # reload from DB to get auto-generated id
        logger.info(f"Saved new {self.model.__tablename__} record with id={record.id}")
        return self._to_dict(record)

    def update(self, record_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing record.

        Steps:
          1. Find the record (returns None if not found)
          2. Update each field from the data dict
          3. Commit
          4. Refresh and return
        """
        record = self.db.query(self.model).filter(
            self.model.id == record_id
        ).first()

        if not record:
            return None

        data.pop("id", None)  # never update the primary key
        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        self.db.commit()
        self.db.refresh(record)
        logger.info(f"Updated {self.model.__tablename__} record id={record_id}")
        return self._to_dict(record)

    def delete(self, record_id: int) -> bool:
        """
        Delete a record by ID.
        Returns True if deleted, False if not found.
        """
        record = self.db.query(self.model).filter(
            self.model.id == record_id
        ).first()

        if not record:
            return False

        self.db.delete(record)
        self.db.commit()
        logger.info(f"Deleted {self.model.__tablename__} record id={record_id}")
        return True

    # ── Private helper ────────────────────────────────────────────────

    def _to_dict(self, record) -> Dict[str, Any]:
        """
        Convert a SQLAlchemy model instance to a plain dict.

        WHY? Services and schemas work with plain dicts and Pydantic models.
        They should never import SQLAlchemy — that would break the layer separation.

        We use __table__.columns to get all column names dynamically,
        so this works for both UserModel and TaskModel without changes.
        """
        if record is None:
            return None
        result = {}
        for column in record.__table__.columns:
            result[column.name] = getattr(record, column.name)

        # Map owner_username → owner for task service compatibility
        if "owner_username" in result:
            result["owner"] = result.pop("owner_username")

        return result
