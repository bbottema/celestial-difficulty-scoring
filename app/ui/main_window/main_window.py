from PySide6.QtCore import QSettings, QByteArray, QRect
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QFileDialog, QHeaderView
)

from app.data_access.importers.astroplanner_excel_importer import AstroPlannerExcelImporter
from app.domain.celestial_object import CelestialsList


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

        # Button to import data
        self.import_button = QPushButton("Import from Excel")
        self.import_button.clicked.connect(self.import_data)

        # Table to display celestial objects
        self.table = QTableWidget(0, 7)  # Start with zero rows and four columns
        self.table.setHorizontalHeaderLabels([
            'Name',
            'Type',
            'Magnitude',
            'Size in arcminutes',
            'Altitude',
            'Observability Index',
            'Observability Index (normalized)'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Buttons for adding equipment
        self.add_telescope_button = QPushButton("Add Telescope")
        self.add_eyepiece_button = QPushButton("Add Eyepiece")
        self.add_barlow_lens_button = QPushButton("Add Barlow Lens")

        # Connect equipment buttons to methods
        self.add_telescope_button.clicked.connect(self.add_telescope)
        self.add_eyepiece_button.clicked.connect(self.add_eyepiece)
        self.add_barlow_lens_button.clicked.connect(self.add_barlow_lens)

        # Layout and central widget
        layout = QVBoxLayout()
        layout.addWidget(self.import_button)
        layout.addWidget(self.table)
        layout.addWidget(self.add_telescope_button)
        layout.addWidget(self.add_eyepiece_button)
        layout.addWidget(self.add_barlow_lens_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def import_data(self):
        # Open a dialog to select an Excel file and import data
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx)")
        if file_path:
            data: CelestialsList = AstroPlannerExcelImporter(file_path).import_data()
            self.populate_table(data)

    def populate_table(self, data: CelestialsList):
        # Here you would open the Excel file and read the data
        # For now, let's populate the table with dummy data
        print(data)

        self.table.insertRow(0)
        # self.table.setItem(0, 0, QTableWidgetItem("Dummy Star"))
        # self.table.setItem(0, 1, QTableWidgetItem("Star"))
        # self.table.setItem(0, 2, QTableWidgetItem("5.5"))
        # self.table.setItem(0, 3, QTableWidgetItem("Not Calculated"))

        for i, celestial_object in enumerate(data):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(celestial_object.name))
            self.table.setItem(i, 1, QTableWidgetItem(celestial_object.object_type))
            self.table.setItem(i, 2, QTableWidgetItem(str(celestial_object.magnitude)))
            self.table.setItem(i, 3, QTableWidgetItem(str(celestial_object.size)))
            self.table.setItem(i, 4, QTableWidgetItem(str(celestial_object.altitude)))
            self.table.setItem(i, 5, QTableWidgetItem(str(celestial_object.observability_score.score)))
            self.table.setItem(i, 6, QTableWidgetItem(str(celestial_object.observability_score.normalized_score)))


    def add_telescope(self):
        # Open dialog to input telescope details
        # Update observability index accordingly
        pass

    def add_eyepiece(self):
        # Open dialog to input eyepiece details
        # Update observability index accordingly
        pass

    def add_barlow_lens(self):
        # Open dialog to input Barlow lens details
        # Update observability index accordingly
        pass

    # More methods would be defined here for processing equipment and updating observability index

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
