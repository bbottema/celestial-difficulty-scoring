from sqlalchemy.orm import Session

from app.config.autowire import component
from app.orm.model.entities import Imager
from app.orm.repositories.base_equipment_repository import BaseEquipmentRepository


@component
class ImagerRepository(BaseEquipmentRepository[Imager]):
    def __init__(self):
        super().__init__(Imager)

    def handle_update(self, persisted_imager: Imager, updated_imager: Imager, session: Session) -> None:
        super().handle_update(persisted_imager, updated_imager, session)
        # TODO add specific fields for Imager, when they are added to the model
