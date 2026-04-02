from sqlalchemy.orm import Session
from typing import List, Optional, Any, Type, TypeVar
from repositories.base_repository import BaseRepository
from database import Base

T = TypeVar("T", bound=Base)

class SQLAlchemyRepository(BaseRepository[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def add(self, entity: T) -> T:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get_by_id(self, id: Any) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, **filters) -> List[T]:
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.all()

    def update(self, id: Any, **updates) -> Optional[T]:
        entity = self.get_by_id(id)
        if entity:
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            self.db.commit()
            self.db.refresh(entity)
        return entity

    def delete(self, id: Any) -> bool:
        entity = self.get_by_id(id)
        if entity:
            self.db.delete(entity)
            self.db.commit()
            return True
        return False
