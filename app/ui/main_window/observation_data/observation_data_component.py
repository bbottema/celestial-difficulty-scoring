from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QFileDialog, QHeaderView
)

from app.data_access.importers.astroplanner_excel_importer import AstroPlannerExcelImporter
from app.domain.celestial_object import CelestialsList


class ObservationDataComponent(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)

    # noinspection PyAttributeOutsideInit
    def init_ui(self):
        # Button to import data
        self.import_button = QPushButton("Import from Excel")
        self.import_button.clicked.connect(self.import_data)

        # Table to display celestial objects
        self.table = QTableWidget(0, 7)  # Start with zero rows and seven columns
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

        # Add components to the layout
        self.layout.addWidget(self.import_button)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.add_telescope_button)
        self.layout.addWidget(self.add_eyepiece_button)
        self.layout.addWidget(self.add_barlow_lens_button)

    def import_data(self):
        # Open a dialog to select an Excel file and import data
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx)")
        if file_path:
            data: CelestialsList = AstroPlannerExcelImporter(file_path).import_data()
            self.populate_table(data)

    def populate_table(self, data: CelestialsList):
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
