import dataclasses

from app.domain.entities.entities import ObservationSite
from db.database import get_db_connection
from domain.light_pollution import LightPollution
from utils.event_bus_config import bus, CelestialEvent


class ObservationSiteRepository:

    @staticmethod
    def add_observation_site(observation_site: ObservationSite):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO observation_sites "
                       "(name, latitude, longitude, light_pollution) VALUES "
                       "(?, ?, ?, ?)",
                       (observation_site.name, observation_site.latitude, observation_site.longitude,
                        observation_site.light_pollution.name))
        conn.commit()
        conn.close()
        updated_observation_site = dataclasses.replace(observation_site, id=cursor.lastrowid)
        bus.emit(CelestialEvent.OBSERVATION_SITE_ADDED, updated_observation_site)

    @staticmethod
    def get_observation_sites() -> [ObservationSite]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM observation_sites")
        sites = [ObservationSiteRepository.map_row(row) for row in cursor.fetchall()]
        conn.close()
        return sites

    @staticmethod
    def get_observation_site(site_id: int) -> ObservationSite:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM observation_sites WHERE id = ?", (site_id,))
        observation_site = ObservationSiteRepository.map_row(cursor.fetchone())
        conn.close()
        return observation_site

    @staticmethod
    def map_row(row):
        return ObservationSite(
            id=row[0],
            name=row[1],
            latitude=row[2],
            longitude=row[3],
            light_pollution=LightPollution[row[4]]
        )

    # Implement update_item and delete_item similarly
    @staticmethod
    def update_observation_sites(site_id, observation_site: ObservationSite):
        print(f"Updating site {site_id}")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE observation_sites "
                       "SET name = ?, latitude = ?, longitude = ?, light_pollution = ? "
                       "WHERE id = ?",
                       (observation_site.name, observation_site.latitude, observation_site.longitude,
                        observation_site.light_pollution.name, site_id))
        conn.commit()
        conn.close()
        bus.emit(CelestialEvent.OBSERVATION_SITE_UPDATED, observation_site)

    @staticmethod
    def delete_observation_sites(site_id):
        print(f"Deleting site {site_id}")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM observation_sites WHERE id = ?", (site_id,))
        conn.commit()
        conn.close()
        bus.emit(CelestialEvent.OBSERVATION_SITE_DELETED, site_id)
