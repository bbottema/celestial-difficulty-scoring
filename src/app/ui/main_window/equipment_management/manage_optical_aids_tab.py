from PySide6.QtWidgets import QTableWidget, QVBoxLayout

from app.orm.entities import OpticalAid
from app.ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from app.utils.gui_helper import default_table


class ManageOpticalAidsTab(ManageEquipmentTab):

    def __init__(self, observation_site_service):
        super().__init__(OpticalAid, observation_site_service)
        # self.optical_aid_service = optical_aid_service

    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', ''])

    def define_equipment_form_controls(self, form_layout: QVBoxLayout):
        pass
