import logging

from injector import inject

from app.config.autowire import component
from app.config.event_bus_config import CelestialEvent
from app.orm.model.entities import Telescope
from app.orm.repositories.telescope_repository import TelescopeRepository
from app.orm.services.base_service import BaseService, MutationEvents

logger = logging.getLogger(__name__)


@component
class TelescopeService(BaseService[Telescope]):

    @inject
    def __init__(self, telescope_repository: TelescopeRepository):
        super().__init__(
            telescope_repository,
            MutationEvents(
                added=CelestialEvent.EQUIPMENT_TELESCOPE_ADDED,
                updated=CelestialEvent.EQUIPMENT_TELESCOPE_UPDATED,
                deleted=CelestialEvent.EQUIPMENT_TELESCOPE_DELETED
            )
        )
