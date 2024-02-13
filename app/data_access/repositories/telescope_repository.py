import dataclasses

from db.database import get_db_connection
from domain.entities.telescope import Telescope
from domain.light_pollution import LightPollution
from utils.event_bus_config import bus, CelestialEvent


class TelescopeRepository:

    @staticmethod
    def add_telescope(telescope: Telescope):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO telescopes "
                       "(name, observation_site) VALUES "
                       "(?, ?)",
                       (telescope.name, ''))  # FIXME
        conn.commit()
        conn.close()
        updated_telescope = dataclasses.replace(telescope, id=cursor.lastrowid)
        bus.emit(CelestialEvent.EQUIPMENT_TELESCOPE_ADDED, updated_telescope)

    @staticmethod
    def get_telescopes() -> [Telescope]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM telescopes")
        sites = [TelescopeRepository.map_row(row) for row in cursor.fetchall()]
        conn.close()
        return sites

    @staticmethod
    def get_telescope(site_id: int) -> Telescope:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM telescopes WHERE id = ?", (site_id,))
        telescope = TelescopeRepository.map_row(cursor.fetchone())
        conn.close()
        return telescope

    @staticmethod
    def map_row(row):
        return Telescope(
            id=row[0],
            name=row[1],
            observation_site=row[2]
        )

    # Implement update_item and delete_item similarly
    @staticmethod
    def update_telescopes(site_id, telescope: Telescope):
        print(f"Updating site {site_id}")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE telescopes "
                       "SET name = ?, observation_site = ? "
                       "WHERE id = ?",
                       (telescope.name, '', site_id))
        conn.commit()
        conn.close()
        bus.emit(CelestialEvent.EQUIPMENT_TELESCOPE_UPDATED, telescope)

    @staticmethod
    def delete_telescopes(site_id):
        print(f"Deleting site {site_id}")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM telescopes WHERE id = ?", (site_id,))
        conn.commit()
        conn.close()
        bus.emit(CelestialEvent.EQUIPMENT_TELESCOPE_DELETED, site_id)
