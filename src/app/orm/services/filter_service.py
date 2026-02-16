import logging

from injector import inject

from app.config.autowire import component
from app.config.event_bus_config import NightGuideEvent
from app.orm.model.entities import Filter
from app.orm.repositories.filter_repository import FilterRepository
from app.orm.services.base_service import BaseService, MutationEvents

logger = logging.getLogger(__name__)


@component
class FilterService(BaseService[Filter]):

    @inject
    def __init__(self, filter_repository: FilterRepository):
        super().__init__(
            filter_repository,
            MutationEvents(
                added=NightGuideEvent.EQUIPMENT_FILTER_ADDED,
                updated=NightGuideEvent.EQUIPMENT_FILTER_UPDATED,
                deleted=NightGuideEvent.EQUIPMENT_FILTER_DELETED
            )
        )
