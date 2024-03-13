from sqlalchemy.orm import Session

from app.config.autowire import component
from app.orm.model.entities import Telescope
from app.orm.repositories.base_equipment_repository import BaseEquipmentRepository


@component
class TelescopeRepository(BaseEquipmentRepository[Telescope]):
    def __init__(self):
        super().__init__(Telescope)

    def handle_update(self, persisted_telescope: Telescope, updated_telescope: Telescope, session: Session) -> None:
        super().handle_update(persisted_telescope, updated_telescope, session)

        persisted_telescope.type = updated_telescope.type
        persisted_telescope.aperture = updated_telescope.aperture
        persisted_telescope.focal_length = updated_telescope.focal_length
        persisted_telescope.focal_ratio = updated_telescope.focal_ratio
