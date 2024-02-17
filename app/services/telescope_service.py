import logging

from data_access.repositories.telescope_repository import TelescopeRepository
from db.session_manager import session_scope
from domain.entities.entities import Telescope
from utils.event_bus_config import bus, CelestialEvent

logger = logging.getLogger(__name__)


class TelescopeService:
    def __init__(self):
        self.telescope_repository = TelescopeRepository()

    def add_telescope(self, telescope: Telescope) -> Telescope:
        try:
            with session_scope() as session:
                if telescope.observation_sites is not None:
                    for observation_site in telescope.observation_sites:
                        session.merge(observation_site)

                new_telescope = self.telescope_repository.add_telescope(session, telescope)
                session.commit()
                bus.emit(CelestialEvent.EQUIPMENT_TELESCOPE_ADDED, telescope)
                return new_telescope
        except Exception as e:
            logger.error(f"Failed to add telescope {telescope}: ERROR: {e}")
            raise e

    def get_telescopes(self) -> [Telescope]:
        try:
            with session_scope() as session:
                return self.telescope_repository.get_telescopes(session)
        except Exception as e:
            logger.error(f"Failed to get telescopes: ERROR: {e}")
            raise e

    def get_telescope(self, telescope_id: int) -> Telescope:
        try:
            with session_scope() as session:
                return self.telescope_repository.get_telescope(session, telescope_id)
        except Exception as e:
            logger.error(f"Failed to get telescope {telescope_id}: ERROR: {e}")
            raise e

    def update_telescope(self, updated_telescope: Telescope):
        try:
            with session_scope() as session:
                for observation_site in updated_telescope.observation_sites:
                    session.merge(observation_site)

                telescope = self.telescope_repository.update_telescope(session, updated_telescope)
                session.commit()
                bus.emit(CelestialEvent.EQUIPMENT_TELESCOPE_UPDATED, telescope)
                return telescope
        except Exception as e:
            logger.error(f"Failed to update telescope {updated_telescope}: ERROR: {e}")
            raise e

    def delete_telescope(self, telescope_id: int):
        try:
            with session_scope() as session:
                self.telescope_repository.delete_telescope(session, telescope_id)
                session.commit()
                bus.emit(CelestialEvent.EQUIPMENT_TELESCOPE_DELETED, telescope_id)
        except Exception as e:
            logger.error(f"Failed to delete telescope {telescope_id}: ERROR: {e}")
            raise e


telescope_service = TelescopeService()
