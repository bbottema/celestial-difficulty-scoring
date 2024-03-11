import logging

from injector import inject

from app.config.autowire import component
from app.config.event_bus_config import CelestialEvent
from app.orm.model.entities import Imager
from app.orm.repositories.imager_repository import ImagerRepository
from app.orm.services.base_service import BaseService, MutationEvents

logger = logging.getLogger(__name__)


@component
class ImagerService(BaseService[Imager]):

    @inject
    def __init__(self, imager_repository: ImagerRepository):
        super().__init__(
            imager_repository,
            MutationEvents(
                added=CelestialEvent.EQUIPMENT_IMAGER_ADDED,
                updated=CelestialEvent.EQUIPMENT_IMAGER_UPDATED,
                deleted=CelestialEvent.EQUIPMENT_IMAGER_DELETED
            )
        )
