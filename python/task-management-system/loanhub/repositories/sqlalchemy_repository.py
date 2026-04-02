from sqlalchemy.orm import Session
from .base_repository import BaseRepository
from typing import TypeVar, List, Optional, Type, Any

T = TypeVar("T")

class SQLAlchemyRepository(BaseRepository[T]):
    """
    Concrete implementation of BaseRepository using SQLAlchemy.
    Following LSP (Liskov Substitution Principle).
    """
    def __init__(self, db: Session):
        self.db = db

    def save(self, obj: T) -> T:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def find_by_id(self, model_class: Type[T], id: Any) -> Optional[T]:
        return self.db.query(model_class).filter(model_class.id == id).first()

    def find_all(self, model_class: Type[T], **filters) -> List[T]:
        query = self.db.query(model_class)
        for attr, value in filters.items():
            if value is not None:
                query = query.filter(getattr(model_class, attr) == value)
        return query.all()

    def update(self, obj: T) -> T:
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: T) -> bool:
        try:
            self.db.delete(obj)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
