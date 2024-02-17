import logging

from orm.repositories.observation_site_repository import ObservationSiteRepository
from orm.services.base_service import BaseService
from utils.event_bus_config import CelestialEvent

logger = logging.getLogger(__name__)


class ObservationSiteService(BaseService):
    def __init__(self):
        super().__init__(
            ObservationSiteRepository(),
            {
                'added': CelestialEvent.OBSERVATION_SITE_ADDED,
                'updated': CelestialEvent.OBSERVATION_SITE_UPDATED,
                'deleted': CelestialEvent.OBSERVATION_SITE_DELETED
            }
        )

    # FIXME: instance should be strong-typed in the super class via generics
    def handle_relations(self, instance, session, operation):
        if operation in ['add', 'update'] and instance.telescopes is not None:
            for telescope in instance.telescopes:
                session.merge(telescope)


observation_site_service = ObservationSiteService()
