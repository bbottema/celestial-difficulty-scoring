from PySide6.QtWidgets import QTableWidget

from ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from utils.gui_helper import default_table


class ManageImagersTab(ManageEquipmentTab):

    def __init__(self, observation_site_service):
        super().__init__('Imager', observation_site_service)
        # self.imager_service = imager_service

    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', ''])

    def define_equipment_form_controls(self, layout):
        pass
