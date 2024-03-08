from app.config.autowire import component
from app.orm.entities import Eyepiece
from app.orm.repositories.base_equipment_repository import BaseEquipmentRepository


@component
class EyepieceRepository(BaseEquipmentRepository[Eyepiece]):
    def __init__(self):
        super().__init__(Eyepiece)
