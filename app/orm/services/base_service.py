import logging
from typing import Generic, TypeVar, Type

from orm.repositories.base_repository import BaseRepository
from database import session_scope
from utils.event_bus_config import bus

logger = logging.getLogger(__name__)
T = TypeVar('T')


class BaseService(Generic[T]):
    def __init__(self, repository: BaseRepository, events):
        self.repository = repository
        self.events = events

    def add(self, instance: Type[T]) -> Type[T]:
        try:
            with session_scope() as session:
                self.handle_relations(instance, session, 'add')
                new_instance: Type[T] = self.repository.add(session, instance)
                session.commit()
                bus.emit(self.events['added'], new_instance)
                return new_instance
        except Exception as e:
            logger.error(f"Failed to add {instance}: ERROR: {e}")
            raise e

    def get_all(self) -> list[T]:
        try:
            with session_scope() as session:
                return self.repository.get_all(session)
        except Exception as e:
            logger.error("Failed to get instances: ERROR: {e}")
            raise e

    def get_by_id(self, instance_id) -> Type[T]:
        try:
            with session_scope() as session:
                return self.repository.get_by_id(session, instance_id)
        except Exception as e:
            logger.error(f"Failed to get instance {instance_id}: ERROR: {e}")
            raise e

    def update(self, instance: Type[T]) -> Type[T]:
        try:
            with session_scope() as session:
                self.handle_relations(instance, session, 'update')
                updated_instance: Type[T] = self.repository.update(session, instance.id, instance)
                session.commit()
                bus.emit(self.events['updated'], updated_instance)
                return updated_instance
        except Exception as e:
            logger.error(f"Failed to update {instance}: ERROR: {e}")
            raise e

    def delete(self, instance: Type[T]) -> None:
        try:
            with session_scope() as session:
                self.repository.delete(session, instance)
                session.commit()
                bus.emit(self.events['deleted'], instance)
        except Exception as e:
            logger.error(f"Failed to delete {instance.id}: ERROR: {e}")
            raise e

    def handle_relations(self, instance, session, operation) -> None:
        pass