from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton

from app.orm.model.entities import Filter
from app.orm.model.wavelength_type import Wavelength


class FilterWavelengthTable(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Filter Wavelength Editor')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(0)  # No rows initially
        self.tableWidget.setColumnCount(2)  # 'From' and 'To' columns
        self.tableWidget.setHorizontalHeaderLabels(['From', 'To'])
        layout.addWidget(self.tableWidget)

        self.addButton = QPushButton('+')
        self.addButton.clicked.connect(self.add_row)
        layout.addWidget(self.addButton)

        self.centralWidget = QWidget()
        self.centralWidget.setLayout(layout)
        self.setCentralWidget(self.centralWidget)

        # Example initialization, replace with actual data fetching
        self.populate_table(Filter(
            id=1,
            name="Myf",
            wavelengths=[Wavelength(400, 700), Wavelength(100, 200)]
        ))

    def populate_table(self, filter_entity):
        self.tableWidget.setRowCount(0)
        for wavelength in filter_entity.wavelengths:
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            self.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(wavelength.from_wavelength)))
            self.tableWidget.setItem(row_position, 1, QTableWidgetItem(str(wavelength.to_wavelength)))

    def add_row(self):
        # Add row with default values and update database
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)
        self.tableWidget.setItem(row_position, 0, QTableWidgetItem("0"))  # Default or zero value
        self.tableWidget.setItem(row_position, 1, QTableWidgetItem("0"))  # Default or zero value
        # Update database with new entry
        pass

    def update_database_entry(self, row, column):
        new_wavelengths = []
        for row_index in range(self.tableWidget.rowCount()):
            from_wavelength = float(self.tableWidget.item(row_index, 0).text())
            to_wavelength = float(self.tableWidget.item(row_index, 1).text())
            new_wavelengths.append(Wavelength(from_wavelength=from_wavelength, to_wavelength=to_wavelength))
        filter = Filter(
            id=1,
            name="Myf",
            wavelengths=new_wavelengths

        )
        self.populate_table(filter)


if __name__ == "__main__":
    app = QApplication([])
    window = FilterWavelengthTable()
    window.show()
    app.exec()
