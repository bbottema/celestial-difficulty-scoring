import logging

from data_access.repositories.observation_site_repository import ObservationSiteRepository
from db.session_manager import session_scope
from domain.entities.entities import ObservationSite
from utils.event_bus_config import bus, CelestialEvent

logger = logging.getLogger(__name__)


class ObservationSiteService:
    def __init__(self):
        self.observation_site_repository = ObservationSiteRepository()

    def add_observation_site(self, observation_site: ObservationSite) -> ObservationSite:
        try:
            with session_scope() as session:
                if observation_site.telescopes is not None:
                    for telescope in observation_site.telescopes:
                        session.merge(telescope)

                new_observation_site = self.observation_site_repository.add_observation_site(session, observation_site)
                session.commit()
                bus.emit(CelestialEvent.OBSERVATION_SITE_ADDED, observation_site)
                return new_observation_site
        except Exception as e:
            logger.error(f"Failed to add observation_site {observation_site}: ERROR: {e}")
            raise e

    def get_observation_sites(self) -> [ObservationSite]:
        try:
            with session_scope() as session:
                return self.observation_site_repository.get_observation_sites(session)
        except Exception as e:
            logger.error(f"Failed to get observation_sites: ERROR: {e}")
            raise e

    def get_observation_site(self, observation_site_id: int) -> ObservationSite:
        try:
            with session_scope() as session:
                return self.observation_site_repository.get_observation_site(session, observation_site_id)
        except Exception as e:
            logger.error(f"Failed to get observation_site {observation_site_id}: ERROR: {e}")
            raise e

    def update_observation_site(self, updated_observation_site: ObservationSite):
        try:
            with session_scope() as session:
                for telescope in updated_observation_site.telescopes:
                    session.merge(telescope)

                observation_site = self.observation_site_repository.update_observation_site(session, updated_observation_site)
                session.commit()
                bus.emit(CelestialEvent.OBSERVATION_SITE_UPDATED, observation_site)
                return observation_site
        except Exception as e:
            logger.error(f"Failed to update observation_site {updated_observation_site}: ERROR: {e}")
            raise e

    def delete_observation_site(self, observation_site: ObservationSite):
        try:
            with session_scope() as session:
                self.observation_site_repository.delete_observation_site(session, observation_site)
                session.commit()
                bus.emit(CelestialEvent.OBSERVATION_SITE_DELETED, observation_site)
        except Exception as e:
            logger.error(f"Failed to delete observation_site {observation_site.id}: ERROR: {e}")
            raise e


observation_site_service = ObservationSiteService()
