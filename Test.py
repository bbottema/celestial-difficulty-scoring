import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window title and initial size
        self.setWindowTitle('Celestial Object Observability')
        self.setGeometry(100, 100, 800, 600)

        # Layout and central widget
        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Button to import data
        self.import_button = QPushButton("Import from Excel")
        self.import_button.clicked.connect(self.import_data)

        # Table to display celestial objects
        self.table = QTableWidget(0, 4)  # Start with zero rows and four columns
        self.table.setHorizontalHeaderLabels(['Name', 'Type', 'Magnitude', 'Observability Index'])

        # Buttons for adding equipment
        self.add_telescope_button = QPushButton("Add Telescope")
        self.add_eyepiece_button = QPushButton("Add Eyepiece")
        self.add_barlow_lens_button = QPushButton("Add Barlow Lens")

        # Connect equipment buttons to methods
        self.add_telescope_button.clicked.connect(self.add_telescope)
        self.add_eyepiece_button.clicked.connect(self.add_eyepiece)
        self.add_barlow_lens_button.clicked.connect(self.add_barlow_lens)

        # Add components to layout
        layout.addWidget(self.import_button)
        layout.addWidget(self.table)
        layout.addWidget(self.add_telescope_button)
        layout.addWidget(self.add_eyepiece_button)
        layout.addWidget(self.add_barlow_lens_button)

    def import_data(self):
        # Open a dialog to select an Excel file and import data
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx)")
        if file_path:
            self.process_import(file_path)

    def process_import(self, file_path):
        # Here you would open the Excel file and read the data
        # For now, let's populate the table with dummy data
        self.table.insertRow(0)
        self.table.setItem(0, 0, QTableWidgetItem("Dummy Star"))
        self.table.setItem(0, 1, QTableWidgetItem("Star"))
        self.table.setItem(0, 2, QTableWidgetItem("5.5"))
        self.table.setItem(0, 3, QTableWidgetItem("Not Calculated"))

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


# Entry point of the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
