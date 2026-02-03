from typing import cast

from PySide6.QtCore import QSettings, QByteArray
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import *
from injector import inject

from app.ui.main_window.equipment_management.equipment_management_component import EquipmentManagementComponent
from app.ui.main_window.observation_data.observation_data_component import ObservationDataComponent
from app.ui.main_window.observation_preferences.observation_preferences_component import ObservationPreferencesComponent
from app.ui.main_window.observation_sites.observation_sites_component import ObservationSitesComponent


class MainWindow(QMainWindow):
    settings: QSettings = QSettings('BennyBottema', 'CelestialObjectObservability')

    @inject
    def __init__(self,
                 observation_data_component: ObservationDataComponent,
                 observation_sites_component: ObservationSitesComponent,
                 equipment_management_component: EquipmentManagementComponent,
                 observation_preferences_component: ObservationPreferencesComponent) -> None:
        super().__init__(None)

        self.observation_data_component = observation_data_component
        self.observation_sites_component = observation_sites_component
        self.equipment_management_component = equipment_management_component
        self.observation_preferences_component = observation_preferences_component

        # Restore the window's last geometry or center it
        geometry: QByteArray = cast(QByteArray, self.settings.value("geometry", QByteArray()))
        if not geometry:
            self.position_window_to_default()
        else:
            self.restoreGeometry(geometry)

        self.setWindowTitle('Celestial Object Observability')
        self.init_ui()

    def cleanup_event_filter(self):
        QApplication.instance().removeEventFilter(self.eventFilter)

    # noinspection PyAttributeOutsideInit
    def init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(self.observation_data_component, "Plan Tonight's Session")
        self.tabs.addTab(self.observation_sites_component, "Setup: Observation Sites")
        self.tabs.addTab(self.equipment_management_component, "Setup: Equipment")
        self.tabs.addTab(self.observation_preferences_component, "Setup: Preferences")

    def closeEvent(self, event):
        # Save the current geometry of the window before closing
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def position_window_to_default(self):
        self.setGeometry(100, 100, 800, 600)
        # Center the window on the screen
        center_point = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
