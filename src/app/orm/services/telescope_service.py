import logging

from injector import inject

from app.config.autowire import component
from app.config.event_bus_config import CelestialEvent
from app.orm.entities import Telescope
from app.orm.repositories.telescope_repository import TelescopeRepository
from app.orm.services.base_service import BaseService, MutationEvents

logger = logging.getLogger(__name__)


@component
class TelescopeService(BaseService[Telescope]):

    @inject
    def __init__(self, telescope_repository: TelescopeRepository):
        super().__init__(
            telescope_repository,
            MutationEvents(
                added=CelestialEvent.EQUIPMENT_TELESCOPE_ADDED,
                updated=CelestialEvent.EQUIPMENT_TELESCOPE_UPDATED,
                deleted=CelestialEvent.EQUIPMENT_TELESCOPE_DELETED
            )
        )

    def handle_relations(self, instance: Telescope, session, operation):
        if operation in ['add', 'update'] and instance.observation_sites is not None:
            for observation_site in instance.observation_sites:
                session.merge(observation_site)
