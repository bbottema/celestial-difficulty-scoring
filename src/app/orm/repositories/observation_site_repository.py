from sqlalchemy.orm import Session

from app.config.autowire import component
from app.orm.model.entities import ObservationSite
from app.orm.repositories.base_repository import BaseRepository


@component
class ObservationSiteRepository(BaseRepository[ObservationSite]):
    def __init__(self):
        super().__init__(ObservationSite)

    def handle_update(self, persisted_observation_site: ObservationSite, updated_observation_site: ObservationSite, session: Session):
        persisted_observation_site.name = updated_observation_site.name
        persisted_observation_site.latitude = updated_observation_site.latitude
        persisted_observation_site.longitude = updated_observation_site.longitude
        persisted_observation_site.light_pollution = updated_observation_site.light_pollution

        persisted_observation_site.telescopes.clear()
        for telescope in updated_observation_site.telescopes:
            persisted_observation_site.telescopes.append(telescope)

        persisted_observation_site.filters.clear()
        for filter in updated_observation_site.filters:
            persisted_observation_site.filters.append(filter)

        persisted_observation_site.optical_aids.clear()
        for optical_aid in updated_observation_site.optical_aids:
            persisted_observation_site.optical_aids.append(optical_aid)

        persisted_observation_site.eyepieces.clear()
        for eyepiece in updated_observation_site.eyepieces:
            persisted_observation_site.eyepieces.append(eyepiece)

        persisted_observation_site.imagers.clear()
        for imager in updated_observation_site.imagers:
            persisted_observation_site.imagers.append(imager)
