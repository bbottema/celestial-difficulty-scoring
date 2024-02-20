from abc import abstractmethod

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QLineEdit, QLabel, QPushButton, QSpacerItem, QListWidget, QListWidgetItem, QSizePolicy, \
    QTabWidget, QHBoxLayout
from PySide6.QtCore import Qt
from injector import inject

from config.autowire import component
from orm.entities import Telescope
from orm.services.observation_site_service import ObservationSiteService
from orm.services.telescope_service import TelescopeService
from ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from ui.main_window.equipment_management.manage_eyepieces_tab import ManageEyepiecesTab
from ui.main_window.equipment_management.manage_filters_tab import ManageFiltersTab
from ui.main_window.equipment_management.manage_imagers_tab import ManageImagersTab
from ui.main_window.equipment_management.manage_optical_aids_tab import ManageOpticalAidsTab
from ui.main_window.equipment_management.manage_telescopes_tab import ManageTelescopesTab
from utils.gui_helper import centered_table_widget_item


@component
class EquipmentManagementComponent(QWidget):
    @inject
    def __init__(self, telescope_service: TelescopeService, observation_site_service: ObservationSiteService):
        super().__init__(None)
        self.telescope_service = telescope_service
        self.observation_site_service = observation_site_service
        self.init_ui()

    # noinspection PyAttributeOutsideInit
    def init_ui(self):
        self.layout = QVBoxLayout(self)

        equipment_tabs = QTabWidget(self)
        equipment_tabs.addTab(ManageTelescopesTab(self.telescope_service, self.observation_site_service), "Telescopes")
        equipment_tabs.addTab(ManageEyepiecesTab(self.observation_site_service), "Eyepieces")
        equipment_tabs.addTab(ManageOpticalAidsTab(self.observation_site_service), "Optical Aids")
        equipment_tabs.addTab(ManageFiltersTab(self.observation_site_service), "Filters")
        equipment_tabs.addTab(ManageImagersTab(self.observation_site_service), "Imagers")

        self.layout.addWidget(equipment_tabs)
