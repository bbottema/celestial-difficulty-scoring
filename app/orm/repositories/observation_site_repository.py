from orm.repositories.base_repository import BaseRepository
from orm.entities import ObservationSite


class ObservationSiteRepository(BaseRepository):
    def __init__(self):
        super().__init__(ObservationSite)

    def handle_update(self, persisted_observation_site: ObservationSite, updated_observation_site: ObservationSite):
        persisted_observation_site.name = updated_observation_site.name
        persisted_observation_site.latitude = updated_observation_site.latitude
        persisted_observation_site.longitude = updated_observation_site.longitude
        persisted_observation_site.light_pollution = updated_observation_site.light_pollution
        persisted_observation_site.telescopes.clear()

        for telescope in updated_observation_site.telescopes:
            persisted_observation_site.telescopes.append(telescope)
