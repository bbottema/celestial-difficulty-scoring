from PySide6.QtWidgets import QTableWidget, QVBoxLayout

from app.orm.entities import Filter
from app.orm.services.filter_service import FilterService
from app.orm.services.observation_site_service import ObservationSiteService
from app.ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from app.utils.gui_helper import default_table


class ManageFiltersTab(ManageEquipmentTab):

    def __init__(self, observation_site_service: ObservationSiteService, filter_service: FilterService):
        self.filter_service = filter_service
        super().__init__(Filter, observation_site_service, filter_service.mutation_events)

    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', ''])

    def define_equipment_form_controls(self, form_layout: QVBoxLayout):
        pass
