import logging

from injector import inject

from app.config.autowire import component
from app.config.event_bus_config import CelestialEvent
from app.orm.entities import Filter
from app.orm.repositories.filter_repository import FilterRepository
from app.orm.services.base_service import BaseService, MutationEvents

logger = logging.getLogger(__name__)


@component
class FilterService(BaseService[Filter]):

    @inject
    def __init__(self, filter_repository: FilterRepository):
        super().__init__(
            filter_repository,
            MutationEvents(
                added=CelestialEvent.EQUIPMENT_FILTER_ADDED,
                updated=CelestialEvent.EQUIPMENT_FILTER_UPDATED,
                deleted=CelestialEvent.EQUIPMENT_FILTER_DELETED
            )
        )

    def handle_relations(self, instance: Filter, session, operation):
        if operation in ['add', 'update'] and instance.observation_sites is not None:
            for observation_site in instance.observation_sites:
                session.merge(observation_site)
