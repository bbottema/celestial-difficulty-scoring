import logging

from sqlalchemy.orm import Session, joinedload

from domain.entities.entities import Telescope

logger = logging.getLogger(__name__)


class TelescopeRepository:

    @staticmethod
    def add_telescope(session: Session, telescope: Telescope) -> Telescope:
        session.add(telescope)
        session.refresh(telescope)
        return telescope

    @staticmethod
    def get_telescopes(session: Session) -> [Telescope]:
        return session.query(Telescope).options(joinedload(Telescope.observation_sites)).all()

    @staticmethod
    def get_telescope(session: Session, telescope_id: int) -> Telescope:
        return session.query(Telescope).options(joinedload(Telescope.observation_sites)).filter(Telescope.id == telescope_id).first()

    @staticmethod
    def update_telescope(session: Session, updated_telescope: Telescope):
        telescope = session.query(Telescope).filter(Telescope.id == updated_telescope.id).first()
        if telescope:
            telescope.name = updated_telescope.name
            telescope.observation_sites.clear()

            for observation_site in updated_telescope.observation_sites:
                telescope.observation_sites.append(observation_site)

            return telescope
        else:
            logger.warning(f"Telescope with ID {updated_telescope.id} not found.")

    @staticmethod
    def delete_telescope(session: Session, telescope_id: int):
        telescope = session.query(Telescope).filter(Telescope.id == telescope_id).first()
        if telescope:
            session.delete(telescope)
        else:
            logger.warning(f"Telescope {telescope_id} not found.")
