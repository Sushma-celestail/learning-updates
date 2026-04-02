"""
repositories/base_repository.py
--------------------------------
Abstract base class (interface) for all repositories.

SOLID PRINCIPLES APPLIED HERE:
─────────────────────────────
ISP (Interface Segregation Principle):
  BaseRepository only defines data-access methods (save, find, update,
  delete). It does NOT include logging, validation, or business logic.
  Each method does exactly ONE thing.

DIP (Dependency Inversion Principle):
  Service classes depend on BaseRepository (the abstraction), not on
  JSONRepository (the concrete implementation). This means we could
  swap JSONRepository for a SQLiteRepository or a RedisRepository
  without changing a single line in the service layer.

LSP (Liskov Substitution Principle):
  Any class that inherits from BaseRepository and implements all its
  abstract methods can be used wherever BaseRepository is expected.
  JSONRepository is one such implementation.

WHY ABC?
Python's abc.ABC + @abstractmethod forces subclasses to implement
every abstract method. If you forget to implement find_by_id(), Python
raises a TypeError at import time — catching the bug early.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseRepository(ABC):
    """
    Abstract interface for a generic key-value style repository.
    T represents the entity type (user dict or task dict).
    """

    @abstractmethod
    def find_all(self) -> List[Dict[str, Any]]:
        """Return every record in the collection."""
        pass

    @abstractmethod
    def find_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Return a single record by its integer ID, or None if not found.
        Returning None (instead of raising) keeps the repository "pure":
        the service layer decides whether None is an error.
        """
        pass

    @abstractmethod
    def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Persist a new record and return it with its assigned ID.
        The repository is responsible for auto-incrementing the ID.
        """
        pass

    @abstractmethod
    def update(self, record_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Replace the fields of an existing record.
        Returns the updated record, or None if record_id doesn't exist.
        """
        pass

    @abstractmethod
    def delete(self, record_id: int) -> bool:
        """
        Remove a record by ID.
        Returns True if deletion succeeded, False if record not found.
        """
        pass
