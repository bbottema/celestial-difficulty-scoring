from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from injector import inject

from app.config.autowire import component
from app.orm.services.eyepiece_service import EyepieceService
from app.orm.services.filter_service import FilterService
from app.orm.services.imager_service import ImagerService
from app.orm.services.observation_site_service import ObservationSiteService
from app.orm.services.optical_aid_service import OpticalAidService
from app.orm.services.telescope_service import TelescopeService
from app.ui.main_window.equipment_management.manage_eyepieces_tab import ManageEyepiecesTab
from app.ui.main_window.equipment_management.manage_filters_tab import ManageFiltersTab
from app.ui.main_window.equipment_management.manage_imagers_tab import ManageImagersTab
from app.ui.main_window.equipment_management.manage_optical_aids_tab import ManageOpticalAidsTab
from app.ui.main_window.equipment_management.manage_telescopes_tab import ManageTelescopesTab


@component
class EquipmentManagementComponent(QWidget):
    @inject
    def __init__(self,
                 observation_site_service: ObservationSiteService,
                 telescope_service: TelescopeService,
                 eyepiece_service: EyepieceService,
                 filter_service: FilterService,
                 imager_service: ImagerService,
                 optical_aid_service: OpticalAidService):
        super().__init__(None)
        self.observation_site_service = observation_site_service
        self.telescope_service = telescope_service
        self.eyepiece_service = eyepiece_service
        self.filter_service = filter_service
        self.imager_service = imager_service
        self.optical_aid_service = optical_aid_service
        self.init_ui()

    # noinspection PyAttributeOutsideInit
    def init_ui(self):
        self.layout = QVBoxLayout(self)

        equipment_tabs = QTabWidget(self)
        equipment_tabs.addTab(ManageTelescopesTab(self.observation_site_service, self.telescope_service), "Telescopes")
        equipment_tabs.addTab(ManageEyepiecesTab(self.observation_site_service, self.eyepiece_service), "Eyepieces")
        equipment_tabs.addTab(ManageFiltersTab(self.observation_site_service, self.filter_service), "Filters")
        equipment_tabs.addTab(ManageImagersTab(self.observation_site_service, self.imager_service), "Imagers")
        equipment_tabs.addTab(ManageOpticalAidsTab(self.observation_site_service, self.telescope_service), "Optical Aids")

        self.layout.addWidget(equipment_tabs)
