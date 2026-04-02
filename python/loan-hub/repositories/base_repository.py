from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def add(self, entity: T) -> T:
        pass

    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[T]:
        pass

    @abstractmethod
    def get_all(self, **filters) -> List[T]:
        pass

    @abstractmethod
    def update(self, id: Any, **updates) -> Optional[T]:
        pass

    @abstractmethod
    def delete(self, id: Any) -> bool:
        pass
