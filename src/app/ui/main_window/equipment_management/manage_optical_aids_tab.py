from PySide6.QtWidgets import QTableWidget, QVBoxLayout

from app.orm.entities import OpticalAid
from app.orm.services.observation_site_service import ObservationSiteService
from app.orm.services.optical_aid_service import OpticalAidService
from app.ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from app.utils.gui_helper import default_table


class ManageOpticalAidsTab(ManageEquipmentTab):

    def __init__(self, observation_site_service: ObservationSiteService, optical_aid_service: OpticalAidService):
        self.optical_aid_service = optical_aid_service
        super().__init__(OpticalAid, observation_site_service, optical_aid_service.mutation_events)

    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', ''])

    def define_equipment_form_controls(self, form_layout: QVBoxLayout):
        pass
