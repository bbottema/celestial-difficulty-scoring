from db.database import get_db_connection

from app.domain.entities.observation_site import ObservationSite
from domain.light_pollution import LightPollution
from domain.weather_conditions import WeatherConditions


class ObservationSiteRepository:

    @staticmethod
    def add_observation_site(observation_site: ObservationSite):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO observation_sites "
                       "(name, latitude, longitude, weather_conditions, light_pollution) VALUES "
                       "(?, ?, ?, ?, ?)",
                       (observation_site.name, observation_site.latitude, observation_site.longitude,
                        observation_site.weather_conditions.name, observation_site.light_pollution.name))
        conn.commit()
        conn.close()

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
            weather_conditions=WeatherConditions[row[4]],
            light_pollution=LightPollution[row[5]]
        )

    # Implement update_item and delete_item similarly
    @staticmethod
    def update_observation_sites(site_id, observation_site: ObservationSite):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE observation_sites SET "
                       "name = ?, latitude = ?, longitude = ?, weather_conditions = ?, light_pollution = ? "
                       "WHERE id = ?",
                       (observation_site.name, observation_site.latitude, observation_site.longitude,
                        observation_site.weather_conditions.name, observation_site.light_pollution.name, site_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_observation_sites(item_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM observation_sites WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
