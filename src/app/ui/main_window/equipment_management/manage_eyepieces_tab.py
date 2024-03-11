from PySide6.QtWidgets import QTableWidget, QVBoxLayout

from app.orm.model.entities import Eyepiece
from app.orm.services.eyepiece_service import EyepieceService
from app.orm.services.observation_site_service import ObservationSiteService
from app.ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from app.utils.gui_helper import default_table


class ManageEyepiecesTab(ManageEquipmentTab):

    def __init__(self, eyepiece_service: EyepieceService, observation_site_service: ObservationSiteService):
        super().__init__(Eyepiece, eyepiece_service, observation_site_service, eyepiece_service.mutation_events)

    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', ''])

    def define_equipment_form_controls(self, form_layout: QVBoxLayout):
        pass
