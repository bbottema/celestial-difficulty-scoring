import dataclasses

from sqlalchemy.orm import Session

from db.database import session_local
from domain.entities.entities import Telescope
from domain.light_pollution import LightPollution
from utils.event_bus_config import bus, CelestialEvent


class TelescopeRepository:

    @staticmethod
    def add_telescope(telescope: Telescope):
        db: Session = session_local()
        try:
            db.add(telescope)
            db.commit()
            db.refresh(telescope)

            bus.emit(CelestialEvent.EQUIPMENT_TELESCOPE_ADDED, telescope)

            return telescope
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def get_telescopes() -> [Telescope]:
        db: Session = session_local()
        try:
            telescopes = db.query(Telescope).all()
            return telescopes
        finally:
            db.close()

    @staticmethod
    def get_telescope(telescope_id: int) -> Telescope:
        db: Session = session_local()
        try:
            telescope = db.query(Telescope).filter(Telescope.id == telescope_id).first()
            return telescope
        finally:
            db.close()

    @staticmethod
    def update_telescope(site_id: int, updated_telescope: Telescope):
        print(f"Updating site {site_id}")
        db: Session = session_local()
        try:
            telescope = db.query(Telescope).filter(Telescope.id == updated_telescope.id).first()
            if telescope:
                telescope.name = updated_telescope.name
                telescope.observation_site_id = site_id  # Assuming you're updating to link the telescope to a new site
                db.commit()

                bus.emit(CelestialEvent.EQUIPMENT_TELESCOPE_UPDATED, telescope)
            else:
                print(f"Telescope with ID {updated_telescope.id} not found.")
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def delete_telescopes(site_id):
        print(f"Deleting site {site_id}")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM telescopes WHERE id = ?", (site_id,))
        conn.commit()
        conn.close()
        bus.emit(CelestialEvent.EQUIPMENT_TELESCOPE_DELETED, site_id)
