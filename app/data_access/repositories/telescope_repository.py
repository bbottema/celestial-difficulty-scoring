import logging

from db.database import session_local
from domain.entities.entities import Telescope
from utils.event_bus_config import bus, CelestialEvent

logger = logging.getLogger(__name__)


class TelescopeRepository:

    @staticmethod
    def add_telescope(telescope: Telescope) -> Telescope:
        with session_local() as db:
            db.add(telescope)
            db.commit()
            db.refresh(telescope)
            bus.emit(CelestialEvent.EQUIPMENT_TELESCOPE_ADDED, telescope)
            return telescope

    @staticmethod
    def get_telescopes() -> [Telescope]:
        with session_local() as db:
            return db.query(Telescope).all()

    @staticmethod
    def get_telescope(telescope_id: int) -> Telescope:
        with session_local() as db:
            return db.query(Telescope).filter(Telescope.id == telescope_id).first()

    @staticmethod
    def update_telescope(updated_telescope: Telescope):
        with session_local() as db:
            telescope = db.query(Telescope).filter(Telescope.id == updated_telescope.id).first()
            if telescope:
                telescope.name = updated_telescope.name
                telescope.observation_sites.clear()
                for observation_site in updated_telescope.observation_sites:
                    managed_observation_site = db.merge(observation_site)
                    telescope.observation_sites.append(managed_observation_site)

                db.commit()
                bus.emit(CelestialEvent.EQUIPMENT_TELESCOPE_UPDATED, telescope)
                return telescope
            else:
                logger.warning(f"Telescope with ID {updated_telescope.id} not found.")

    @staticmethod
    def delete_telescope(telescope_id: int):
        with session_local() as db:
            telescope = db.query(Telescope).filter(Telescope.id == telescope_id).first()
            if telescope:
                db.delete(telescope)
                db.commit()
                bus.emit(CelestialEvent.EQUIPMENT_TELESCOPE_DELETED, telescope_id)
            else:
                logger.warning(f"Telescope {telescope_id} not found.")
