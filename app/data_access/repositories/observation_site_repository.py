import logging

from sqlalchemy.orm import Session

from domain.entities.entities import ObservationSite

logger = logging.getLogger(__name__)


class ObservationSiteRepository:

    @staticmethod
    def add_observation_site(session: Session, observation_site: ObservationSite) -> ObservationSite:
        session.add(observation_site)
        session.flush()  # obtain the ID of the new observation site
        return observation_site

    @staticmethod
    def get_observation_sites(session: Session) -> [ObservationSite]:
        return session.query(ObservationSite).all()

    @staticmethod
    def get_observation_site(session: Session, observation_site_id: int) -> ObservationSite:
        return session.query(ObservationSite).filter(ObservationSite.id == observation_site_id).first()

    @staticmethod
    def update_observation_site(session: Session, updated_observation_site: ObservationSite):
        observation_site: ObservationSite = session.query(ObservationSite).filter(ObservationSite.id == updated_observation_site.id).first()
        if not observation_site:
            raise Exception(f"ObservationSite with ID {updated_observation_site.id} not found.")
        else:
            observation_site.name = updated_observation_site.name
            observation_site.telescopes.clear()

            for telescope in updated_observation_site.telescopes:
                observation_site.telescopes.append(telescope)

            return observation_site

    @staticmethod
    def delete_observation_site(session: Session, observation_site: ObservationSite):
        session.delete(observation_site)
