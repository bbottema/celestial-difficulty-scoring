import logging

from injector import inject

from app.config.autowire import component
from app.config.event_bus_config import NightGuideEvent
from app.orm.model.entities import ObservationSite
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
                added=NightGuideEvent.OBSERVATION_SITE_ADDED,
                updated=NightGuideEvent.OBSERVATION_SITE_UPDATED,
                deleted=NightGuideEvent.OBSERVATION_SITE_DELETED
            )
        )

    def _handle_observation_site_relations(self, instance: ObservationSite, session, operation):
        if operation in ['add', 'update']:
            if instance.telescopes is not None:
                instance.telescopes = [session.merge(telescope) for telescope in instance.telescopes]
            if instance.eyepieces is not None:
                instance.eyepieces = [session.merge(eyepiece) for eyepiece in instance.eyepieces]
            if instance.imagers is not None:
                instance.imagers = [session.merge(imager) for imager in instance.imagers]
            if instance.filters is not None:
                instance.filters = [session.merge(filter_item) for filter_item in instance.filters]
            if instance.optical_aids is not None:
                instance.optical_aids = [session.merge(optical_aid) for optical_aid in instance.optical_aids]
