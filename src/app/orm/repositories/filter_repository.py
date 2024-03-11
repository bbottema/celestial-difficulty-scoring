from app.config.autowire import component
from app.orm.model.entities import Filter
from app.orm.repositories.base_equipment_repository import BaseEquipmentRepository


@component
class FilterRepository(BaseEquipmentRepository[Filter]):
    def __init__(self):
        super().__init__(Filter)
