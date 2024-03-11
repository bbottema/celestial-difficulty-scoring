import logging

from injector import inject

from app.config.autowire import component
from app.config.event_bus_config import CelestialEvent
from app.orm.model.entities import OpticalAid
from app.orm.repositories.optical_aid_repository import OpticalAidRepository
from app.orm.services.base_service import BaseService, MutationEvents

logger = logging.getLogger(__name__)


@component
class OpticalAidService(BaseService[OpticalAid]):

    @inject
    def __init__(self, optical_aid_repository: OpticalAidRepository):
        super().__init__(
            optical_aid_repository,
            MutationEvents(
                added=CelestialEvent.EQUIPMENT_OPTICAL_AID_ADDED,
                updated=CelestialEvent.EQUIPMENT_OPTICAL_AID_UPDATED,
                deleted=CelestialEvent.EQUIPMENT_OPTICAL_AID_DELETED
            )
        )
