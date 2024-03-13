from sqlalchemy.orm import Session

from app.config.autowire import component
from app.orm.model.entities import Eyepiece
from app.orm.repositories.base_equipment_repository import BaseEquipmentRepository


@component
class EyepieceRepository(BaseEquipmentRepository[Eyepiece]):
    def __init__(self):
        super().__init__(Eyepiece)

    def handle_update(self, persisted_eyepiece: Eyepiece, updated_eyepiece: Eyepiece, session: Session) -> None:
        super().handle_update(persisted_eyepiece, updated_eyepiece, session)
        # TODO add specific fields for Eyepiece, when they are added to the model
