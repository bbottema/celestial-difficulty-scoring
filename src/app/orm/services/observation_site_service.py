import logging

from injector import inject

from app.config.autowire import component
from app.config.event_bus_config import CelestialEvent
from app.orm.entities import ObservationSite
from app.orm.repositories.observation_site_repository import ObservationSiteRepository
from app.orm.services.base_service import BaseService, MutationEvents

logger = logging.getLogger(__name__)


@component
class ObservationSiteService(BaseService[ObservationSite]):
    @inject
    def __init__(self, observation_site_repository: ObservationSiteRepository):
        super().__init__(
            observation_site_repository,
            MutationEvents(
                added=CelestialEvent.OBSERVATION_SITE_ADDED,
                updated=CelestialEvent.OBSERVATION_SITE_UPDATED,
                deleted=CelestialEvent.OBSERVATION_SITE_DELETED
            )
        )

    def _handle_observation_site_relations(self, instance: ObservationSite, session, operation):
        if operation in ['add', 'update']:
            if instance.telescopes is not None:
                for telescope in instance.telescopes:
                    session.merge(telescope)
            if instance.eyepieces is not None:
                for eyepiece in instance.eyepieces:
                    session.merge(eyepiece)
            if instance.imagers is not None:
                for imager in instance.imagers:
                    session.merge(imager)
            if instance.filters is not None:
                for filter in instance.filters:
                    session.merge(filter)
            if instance.optical_aids is not None:
                for optical_aid in instance.optical_aids:
                    session.merge(optical_aid)
