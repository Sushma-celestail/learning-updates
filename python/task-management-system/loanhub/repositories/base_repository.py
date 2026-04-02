from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Type, Any

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    """
    Abstract Base Repository following ISP (Interface Segregation Principle).
    Only defines essential CRUD operations.
    """
    @abstractmethod
    def save(self, obj: T) -> T:
        pass

    @abstractmethod
    def find_by_id(self, model_class: Type[T], id: Any) -> Optional[T]:
        pass

    @abstractmethod
    def find_all(self, model_class: Type[T], **filters) -> List[T]:
        pass

    @abstractmethod
    def update(self, obj: T) -> T:
        pass

    @abstractmethod
    def delete(self, obj: T) -> bool:
        pass
