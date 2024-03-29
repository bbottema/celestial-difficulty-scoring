from abc import abstractmethod
from typing import Generic, TypeVar, Type, cast

from sqlalchemy import type_coerce, TypeCoerce, Integer, Column
from sqlalchemy.orm import Session

from app.orm.model.entities import NamedEntity
from app.utils.orm_util import eager_load_all_relationships

T = TypeVar('T', bound=NamedEntity)


# noinspection PyMethodMayBeStatic
class BaseRepository(Generic[T]):
    def __init__(self, entity: Type[T]):
        self.entity = entity

    def add(self, session: Session, instance: T) -> T:
        session.add(instance)
        session.flush()  # obtain the ID of the new instance
        return instance

    def get_all(self, session: Session) -> list[T]:
        load_options = eager_load_all_relationships(self.entity)
        return session.query(self.entity).options(*load_options).all()

    def get_for_names(self, session: Session, names: list[str]) -> list[T]:
        load_options = eager_load_all_relationships(self.entity)
        return session.query(self.entity).filter(cast(Column, self.entity.name).in_(names)).options(*load_options).all()

    def get_by_id(self, session: Session, instance_id: int) -> T | None:
        a: TypeCoerce = type_coerce(self.entity.id, Integer)
        b: TypeCoerce = type_coerce(instance_id, Integer)
        load_options = eager_load_all_relationships(self.entity)
        return session.query(self.entity).filter(a == b).options(*load_options).first()

    def update(self, session: Session, instance_id: int, updated_object: T) -> T:
        persisted_object: T | None = self.get_by_id(session, instance_id)
        if not persisted_object:
            raise Exception(f"{self.entity.__class__.__name__} with ID {instance_id} not found.")
        self.handle_update(persisted_object, updated_object, session)
        return persisted_object

    def delete(self, session: Session, instance: T) -> None:
        session.delete(instance)

    @abstractmethod
    def handle_update(self, persisted_object: T, updated_object: T, session: Session) -> None:
        pass
