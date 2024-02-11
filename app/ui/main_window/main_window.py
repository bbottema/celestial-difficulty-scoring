from PySide6.QtCore import QSettings, QByteArray, QRect
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import (
    QApplication, QMainWindow
)
from PySide6.QtWidgets import (QTabWidget)

from ui.main_window.equipment_management.equipment_management_component import EquipmentManagementComponent
from ui.main_window.observation_data.observation_data_component import ObservationDataComponent
from ui.main_window.observation_preferences.observation_preferences_component import ObservationPreferencesComponent
from ui.main_window.observation_sites.observation_sites_component import ObservationSitesComponent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = QSettings('BennyBottema', 'CelestialObjectObservability')

        # Restore the window's last geometry or center it
        geometry: QByteArray = self.settings.value("geometry", QByteArray())
        if not geometry:
            self.position_window_to_default()
        else:
            self.restoreGeometry(geometry)

        self.setWindowTitle('Celestial Object Observability')
        self.init_ui()

    # noinspection PyAttributeOutsideInit
    def init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(ObservationDataComponent(), "Observation Data")
        self.tabs.addTab(ObservationSitesComponent(), "Manage Observation Sites")
        self.tabs.addTab(EquipmentManagementComponent(), "Manage Equipment")
        self.tabs.addTab(ObservationPreferencesComponent(), "Observation Preferences")

    def closeEvent(self, event):
        # Save the current geometry of the window before closing
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def position_window_to_default(self):
        self.setGeometry(100, 100, 800, 600)
        # Center the window on the screen
        center_point = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        frame_geometry: QRect = self.frameGeometry()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
