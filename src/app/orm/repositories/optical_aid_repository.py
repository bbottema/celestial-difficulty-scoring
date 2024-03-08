from app.config.autowire import component
from app.orm.entities import OpticalAid
from app.orm.repositories.base_equipment_repository import BaseEquipmentRepository


@component
class OpticalAidRepository(BaseEquipmentRepository[OpticalAid]):
    def __init__(self):
        super().__init__(OpticalAid)
