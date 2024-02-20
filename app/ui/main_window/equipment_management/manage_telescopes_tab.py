from PySide6.QtWidgets import QPushButton

from orm.entities import Telescope
from ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from utils.gui_helper import centered_table_widget_item


class ManageTelescopesTab(ManageEquipmentTab):

    def __init__(self, telescope_service, observation_site_service):
        super().__init__('Telescope', observation_site_service)
        self.telescope_service = telescope_service

    def populate_equipment_table(self, *args):
        self.equipment_table.setRowCount(0)
        data: [Telescope] = self.telescope_service.get_all()
        for i, telescope in enumerate(data):
            self.equipment_table.insertRow(i)
            self.equipment_table.setItem(i, 0, centered_table_widget_item(telescope.name))
            self.equipment_table.setItem(i, 1, centered_table_widget_item(telescope.observation_site.name))

            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda *args, site_id=telescope.id: self.delete_telescope(site_id))

            self.equipment_table.setCellWidget(i, 4, delete_button)
