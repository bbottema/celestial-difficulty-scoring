import logging
from typing import Generic, TypeVar, Protocol

from app.config.database import session_scope
from app.config.event_bus_config import bus
from app.orm.repositories.base_repository import BaseRepository
from app.utils.assume import verify_not_none

logger = logging.getLogger(__name__)


class MutationEvents:
    def __init__(self, added: str, updated: str, deleted: str) -> None:
        self.added = added
        self.updated = updated
        self.deleted = deleted


class SupportsID(Protocol):
    id: int


T = TypeVar('T', bound=SupportsID)


class BaseService(Generic[T]):
    def __init__(self, repository: BaseRepository, mutation_events: MutationEvents):
        self.repository = repository
        self.mutation_events = mutation_events
        self.entity_type = self.repository.entity.__class__.__name__

    def add(self, instance: T) -> T:
        try:
            with session_scope() as session:
                self.handle_relations(instance, session, 'add')
                new_instance: T = self.repository.add(session, instance)
                session.commit()
                bus.emit(self.mutation_events.added, new_instance)
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

    def get_for_names(self, names: list[str]) -> list[T]:
        try:
            with session_scope() as session:
                return self.repository.get_for_names(session, names)
        except Exception as e:
            logger.error(f"Failed to get instances for name {names}: ERROR: {e}")
            raise e

    def get_by_id(self, instance_id) -> T:
        try:
            with session_scope() as session:
                return verify_not_none(self.repository.get_by_id(session, instance_id), self.entity_type)
        except Exception as e:
            logger.error(f"Failed to get instance {instance_id}: ERROR: {e}")
            raise e

    def update(self, instance: T) -> T:
        try:
            with session_scope() as session:
                self.handle_relations(instance, session, 'update')
                updated_instance: T = self.repository.update(session, instance.id, instance)
                session.commit()
                bus.emit(self.mutation_events.updated, updated_instance)
                return updated_instance
        except Exception as e:
            logger.error(f"Failed to update {instance}: ERROR: {e}")
            raise e

    def delete_by_id(self, entity_id: int) -> None:
        try:
            with session_scope() as session:
                instance: T = self.get_by_id(entity_id)
                self.delete(instance)
                session.commit()
                bus.emit(self.mutation_events.deleted, instance)
        except Exception as e:
            logger.error(f"Failed to delete {entity_id}: ERROR: {e}")
            raise e

    def delete(self, instance: T) -> None:
        try:
            with session_scope() as session:
                self.repository.delete(session, instance)
                session.commit()
                bus.emit(self.mutation_events.deleted, instance)
        except Exception as e:
            logger.error(f"Failed to delete {instance.id}: ERROR: {e}")
            raise e

    def handle_relations(self, instance, session, operation) -> None:
        pass
