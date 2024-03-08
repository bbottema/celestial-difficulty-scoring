from app.config.autowire import component
from app.orm.entities import Imager
from app.orm.repositories.base_equipment_repository import BaseEquipmentRepository


@component
class ImagerRepository(BaseEquipmentRepository[Imager]):
    def __init__(self):
        super().__init__(Imager)
