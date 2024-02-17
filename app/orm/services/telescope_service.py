import logging

from orm.repositories.telescope_repository import TelescopeRepository
from orm.services.base_service import BaseService
from utils.event_bus_config import CelestialEvent

logger = logging.getLogger(__name__)


class TelescopeService(BaseService):
    def __init__(self):
        super().__init__(
            TelescopeRepository(),
            {
                'added': CelestialEvent.EQUIPMENT_TELESCOPE_ADDED,
                'updated': CelestialEvent.EQUIPMENT_TELESCOPE_UPDATED,
                'deleted': CelestialEvent.EQUIPMENT_TELESCOPE_DELETED
            }
        )

    # FIXME: instance should be strong-typed in the super class via generics
    def handle_relations(self, instance, session, operation):
        if operation in ['add', 'update'] and instance.observation_sites is not None:
            for observation_site in instance.observation_sites:
                session.merge(observation_site)


telescope_service = TelescopeService()
