from PySide6.QtWidgets import QTableWidget

from app.orm.entities import Imager
from app.orm.services.imager_service import ImagerService
from app.orm.services.observation_site_service import ObservationSiteService
from app.ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from app.utils.gui_helper import default_table


class ManageImagersTab(ManageEquipmentTab):

    def __init__(self, observation_site_service: ObservationSiteService, imager_service: ImagerService):
        self.imager_service = imager_service
        super().__init__(Imager, observation_site_service, imager_service.mutation_events)

    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', ''])

    def define_equipment_form_controls(self, layout):
        pass
