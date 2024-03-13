from sqlalchemy.orm import Session

from app.config.autowire import component
from app.orm.model.entities import OpticalAid
from app.orm.repositories.base_equipment_repository import BaseEquipmentRepository


@component
class OpticalAidRepository(BaseEquipmentRepository[OpticalAid]):
    def __init__(self):
        super().__init__(OpticalAid)

    def handle_update(self, persisted_optical_aid: OpticalAid, updated_optical_aid: OpticalAid, session: Session) -> None:
        super().handle_update(persisted_optical_aid, updated_optical_aid, session)
        # TODO add specific fields for OpticalAid, when they are added to the model
