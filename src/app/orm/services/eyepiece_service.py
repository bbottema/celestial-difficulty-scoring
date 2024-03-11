import logging

from injector import inject

from app.config.autowire import component
from app.config.event_bus_config import CelestialEvent
from app.orm.entities import Eyepiece
from app.orm.repositories.eyepiece_repository import EyepieceRepository
from app.orm.services.base_service import BaseService, MutationEvents

logger = logging.getLogger(__name__)


@component
class EyepieceService(BaseService[Eyepiece]):

    @inject
    def __init__(self, eyepiecetelescope_repository: EyepieceRepository):
        super().__init__(
            eyepiecetelescope_repository,
            MutationEvents(
                added=CelestialEvent.EQUIPMENT_EYEPIECE_ADDED,
                updated=CelestialEvent.EQUIPMENT_EYEPIECE_UPDATED,
                deleted=CelestialEvent.EQUIPMENT_EYEPIECE_DELETED
            )
        )
