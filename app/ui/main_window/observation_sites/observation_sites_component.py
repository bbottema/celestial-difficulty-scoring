from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout

from orm.entities import ObservationSite
from ui.main_window.observation_sites.observation_site_details_dialog import ObservationSiteDetailsDialog
from utils.event_bus_config import CelestialEvent, database_ready_bus, bus
from utils.gui_helper import default_table, centered_table_widget_item
from config.auto_wire import component
from orm.services.observation_site_service import ObservationSiteService


@component
class ObservationSitesComponent(QWidget):
    def __init__(self, observation_site_service: ObservationSiteService):
        super().__init__(None)
        self.observation_site_service = observation_site_service
        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)

    # noinspection PyAttributeOutsideInit
    def init_ui(self):
        # Table to display observation sites
        self.table = default_table(['Name', 'Latitude', 'Longitude', 'Light Pollution', ''])

        # Button to define a new observation site
        self.define_new_button = QPushButton("Define new observation site")
        self.define_new_button.clicked.connect(self.define_new_site)

        # Add table and button to the layout
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.define_new_button)

        bus.on(CelestialEvent.OBSERVATION_SITE_ADDED, self.populate_table)
        bus.on(CelestialEvent.OBSERVATION_SITE_UPDATED, self.populate_table)
        bus.on(CelestialEvent.OBSERVATION_SITE_DELETED, self.populate_table)

        database_ready_bus.subscribe(self.populate_table)

    # noinspection PyUnusedLocal
    def populate_table(self, *args):
        self.table.setRowCount(0)
        data: [ObservationSite] = self.observation_site_service.get_all()
        for i, observation_site in enumerate(data):
            self.table.insertRow(i)
            self.table.setItem(i, 0, centered_table_widget_item(observation_site.name))
            self.table.setItem(i, 1, centered_table_widget_item(str(observation_site.latitude)))
            self.table.setItem(i, 2, centered_table_widget_item(str(observation_site.longitude)))
            self.table.setItem(i, 3, centered_table_widget_item(observation_site.light_pollution.value))

            # Create a QWidget to hold the buttons
            button_widget = QWidget()
            layout = QHBoxLayout(button_widget)
            layout.setContentsMargins(10, 0, 10, 0)

            modify_button = QPushButton("Modify")
            modify_button.clicked.connect(lambda *args, site=observation_site: self.modify_site(site))
            layout.addWidget(modify_button)

            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda *args, site=observation_site: self.delete_site(site))
            layout.addWidget(delete_button)

            self.table.setCellWidget(i, 4, button_widget)

    def define_new_site(self):
        dialog = ObservationSiteDetailsDialog(self)
        if dialog.exec():
            new_site = dialog.to_observation_site()
            self.observation_site_service.add(new_site)

    def modify_site(self, observation_site):
        dialog = ObservationSiteDetailsDialog(self, observation_site)
        if dialog.exec():
            self.observation_site_service.update(dialog.to_observation_site())

    def delete_site(self, observation_site):
        self.observation_site_service.delete(observation_site)
