from typing import Type

from sqlalchemy.orm import Session

from app.config.autowire import component
from app.orm.entities import Telescope, ObservationSite
from app.orm.repositories.base_repository import BaseRepository


@component
class TelescopeRepository(BaseRepository[Telescope]):
    def __init__(self):
        super().__init__(Telescope)

    def handle_update(self, persisted_telescope: Telescope, updated_telescope: Telescope, session: Session):

        # Convert lists to sets for efficient look-up
        persisted_site_ids = {site.id for site in persisted_telescope.observation_sites}
        updated_site_ids = {site.id for site in updated_telescope.observation_sites}

        # Determine sites to add and remove
        sites_to_add_ids = updated_site_ids - persisted_site_ids
        sites_to_remove_ids = persisted_site_ids - updated_site_ids

        # Remove sites
        for site in persisted_telescope.observation_sites[:]:
            if site.id in sites_to_remove_ids:
                persisted_telescope.observation_sites.remove(site)

        # Add new sites
        for site_id in sites_to_add_ids:
            new_site = session.query(ObservationSite).filter(ObservationSite.id == site_id).one()
            persisted_telescope.observation_sites.append(new_site)
