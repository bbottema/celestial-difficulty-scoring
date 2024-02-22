from abc import abstractmethod
from typing import Generic, TypeVar, Type, Protocol

from sqlalchemy import and_
from sqlalchemy.orm import Session


class SupportsID(Protocol):
    id: int


T = TypeVar('T', bound=SupportsID)


class BaseRepository(Generic[T]):
    def __init__(self, entity: Type[T]):
        self.entity = entity

    def add(self, session: Session, instance: Type[T]) -> Type[T]:
        session.add(instance)
        session.flush()  # obtain the ID of the new instance
        return instance

    def get_all(self, session: Session) -> list[T]:
        return session.query(self.entity).all()

    def get_by_id(self, session: Session, instance_id: int) -> Type[T]:
        condition = and_(self.entity.id == instance_id)
        return session.query(self.entity).filter(condition).first()

    def update(self, session: Session, instance_id: int, updated_object: Type[T]) -> Type[T]:
        persisted_object: Type[T] = self.get_by_id(session, instance_id)
        if not persisted_object:
            raise Exception(f"{self.entity.__name__} with ID {instance_id} not found.")
        self.handle_update(persisted_object, updated_object);
        return persisted_object

    def delete(self, session: Session, instance: Type[T]) -> None:
        session.delete(instance)

    @abstractmethod
    def handle_update(self, persisted_object, updated_object: Type[T]) -> None:
        pass
