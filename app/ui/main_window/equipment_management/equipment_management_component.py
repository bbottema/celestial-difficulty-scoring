from PySide6.QtWidgets import (QWidget, QTabWidget, QHBoxLayout, QVBoxLayout, QTableWidget, QLabel, QLineEdit, QComboBox, QPushButton, QSizePolicy, QSpacerItem)
from injector import inject

from config.auto_wire import component
from orm.entities import Telescope
from orm.services.telescope_service import TelescopeService
from utils.event_bus_config import CelestialEvent, bus, database_ready_bus
from utils.gui_helper import centered_table_widget_item
from utils.ui_debug_clipboard_watch import CUSTOM_NAME_PROPERTY


@component
class EquipmentManagementComponent(QWidget):
    @inject
    def __init__(self, telescope_service: TelescopeService):
        super().__init__(None)
        self.telescope_service = telescope_service
        self.init_ui()

    # noinspection PyAttributeOutsideInit
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.equipmentTabs = QTabWidget(self)

        # Initialize tabs for each type of equipment
        self.init_telescope_tab()
        self.init_eyepiece_tab()
        self.init_optical_aids_tab()
        self.init_filters_tab()
        self.init_imagers_tab()

        self.layout.addWidget(self.equipmentTabs)

    # noinspection PyAttributeOutsideInit
    def init_telescope_tab(self):
        tab, table, form_layout = self.setup_equipment_tab("Telescope")
        self.equipmentTabs.addTab(tab, "Telescopes")
        self.telescope_table = table
        bus.on(CelestialEvent.EQUIPMENT_TELESCOPE_ADDED, self.populate_telescope_table)
        bus.on(CelestialEvent.EQUIPMENT_TELESCOPE_UPDATED, self.populate_telescope_table)
        bus.on(CelestialEvent.EQUIPMENT_TELESCOPE_DELETED, self.populate_telescope_table)
        database_ready_bus.subscribe(self.populate_telescope_table)

    def init_eyepiece_tab(self):
        tab, table, form_layout = self.setup_equipment_tab("Eyepiece")
        self.equipmentTabs.addTab(tab, "Eyepieces")

    def init_optical_aids_tab(self):
        tab, table, form_layout = self.setup_equipment_tab("Optical Aid")
        self.equipmentTabs.addTab(tab, "Optical Aids")

    def init_filters_tab(self):
        tab, table, form_layout = self.setup_equipment_tab("Filter")
        self.equipmentTabs.addTab(tab, "Filters")

    def init_imagers_tab(self):
        tab, table, form_layout = self.setup_equipment_tab("Imager")
        self.equipmentTabs.addTab(tab, "Imagers")

    @staticmethod
    def setup_equipment_tab(equipment_type):
        tab = QWidget()
        tab_layout = QHBoxLayout(tab)

        # Table for displaying equipment items
        table = QTableWidget()
        # Configure the table as necessary...
        tab_layout.addWidget(table, 2)

        # Form for editing equipment items
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel(f"{equipment_type} Name:"))
        name_edit = QLineEdit()
        form_layout.addWidget(name_edit)

        # Assuming observation site is common across all equipment types
        form_layout.addWidget(QLabel("Observation Site:"))
        observation_site_dropdown = QComboBox()
        observation_site_dropdown.setProperty(CUSTOM_NAME_PROPERTY, "Equipment_ObservationSiteCombo")
        # Populate observationSiteDropdown with Observation Sites (not shown here)
        form_layout.addWidget(observation_site_dropdown)

        # Add spacer item here to push remaining items to the bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        form_layout.addItem(spacer)

        # Save button at the bottom
        save_button = QPushButton("Save")
        form_layout.addWidget(save_button)

        # Add the formLayout to a widget to control its width
        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        tab_layout.addWidget(form_widget, 1)

        return tab, table, form_layout

    def populate_telescope_table(self, *args):
        self.telescope_table.setRowCount(0)
        data: [Telescope] = self.telescope_service.get_all()
        for i, telescope in enumerate(data):
            self.telescope_table.insertRow(i)
            self.telescope_table.setItem(i, 0, centered_table_widget_item(telescope.name))
            self.telescope_table.setItem(i, 1, centered_table_widget_item(telescope.observation_site.name))

            # Create a QWidget to hold the buttons
            button_widget = QWidget()
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda *args, site_id=telescope.id: self.delete_telescope(site_id))

            self.table.setCellWidget(i, 4, button_widget)
