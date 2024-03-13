from sqlalchemy.orm import Session

from app.config.autowire import component
from app.orm.model.entities import Filter
from app.orm.repositories.base_equipment_repository import BaseEquipmentRepository


@component
class FilterRepository(BaseEquipmentRepository[Filter]):
    def __init__(self):
        super().__init__(Filter)

    def handle_update(self, persisted_filter: Filter, updated_filter: Filter, session: Session) -> None:
        super().handle_update(persisted_filter, updated_filter, session)

        persisted_filter.minimum_exit_pupil = updated_filter.minimum_exit_pupil
        persisted_filter.wavelengths = updated_filter.wavelengths
