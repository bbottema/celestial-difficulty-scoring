import logging

from injector import inject

from app.config.autowire import component
from app.orm.entities import ObservationSite
from app.orm.repositories.observation_site_repository import ObservationSiteRepository
from app.orm.services.base_service import BaseService
from app.config.event_bus_config import CelestialEvent

logger = logging.getLogger(__name__)


@component
class ObservationSiteService(BaseService):
    @inject
    def __init__(self, observation_site_repository: ObservationSiteRepository):
        super().__init__(
            observation_site_repository,
            {
                'added': CelestialEvent.OBSERVATION_SITE_ADDED,
                'updated': CelestialEvent.OBSERVATION_SITE_UPDATED,
                'deleted': CelestialEvent.OBSERVATION_SITE_DELETED
            }
        )

    def handle_relations(self, instance: ObservationSite, session, operation):
        if operation in ['add', 'update'] and instance.telescopes is not None:
            for telescope in instance.telescopes:
                session.merge(telescope)
