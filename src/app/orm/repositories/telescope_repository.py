from app.config.autowire import component
from app.orm.entities import Telescope
from app.orm.repositories.base_equipment_repository import BaseEquipmentRepository


@component
class TelescopeRepository(BaseEquipmentRepository[Telescope]):
    def __init__(self):
        super().__init__(Telescope)
