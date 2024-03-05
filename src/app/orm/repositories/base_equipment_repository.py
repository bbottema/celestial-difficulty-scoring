from typing import TypeVar, Type

from sqlalchemy.orm import Session

from app.config.autowire import component
from app.orm.entities import ObservationSite, EquipmentEntity
from app.orm.repositories.base_repository import BaseRepository

T = TypeVar('T', bound=EquipmentEntity)


@component
class BaseEquipmentRepository(BaseRepository[T]):
    def __init__(self, entity: Type[T]):
        super().__init__(entity)

    def handle_update(self, persisted_telescope: T, updated_telescope: T, session: Session):

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
