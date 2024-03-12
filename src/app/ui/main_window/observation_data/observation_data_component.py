from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QWidget, QFileDialog, QComboBox, QLabel, QHBoxLayout
)

from app.config.autowire import component
from app.domain.model.celestial_object import CelestialsList
from app.domain.model.weather_conditions import WeatherConditions
from app.utils.astroplanner_excel_importer import AstroPlannerExcelImporter
from app.utils.gui_helper import default_table, centered_table_widget_item
from app.utils.ui_debug_clipboard_watch import CUSTOM_NAME_PROPERTY


@component
class ObservationDataComponent(QWidget):
    def __init__(self):
        super().__init__(None)
        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)

    # noinspection PyAttributeOutsideInit
    def init_ui(self):
        self.import_button = QPushButton("Import AstroPlanner's Excel export")
        self.import_button.clicked.connect(self.import_data)

        # Widgets for weather and date/time
        weather_widget = QWidget()
        weather_layout = QHBoxLayout(weather_widget)
        weather_layout.addWidget(QLabel("Weather Conditions:"))
        weather_conditions_combo = QComboBox()
        weather_conditions_combo.setProperty(CUSTOM_NAME_PROPERTY, "ObservationData_WeatherCombo")
        weather_layout.addWidget(weather_conditions_combo)

        for wc in WeatherConditions:
            weather_conditions_combo.addItem(wc.value, wc.name)
        weather_conditions_combo.setCurrentText(WeatherConditions.CLEAR.value)

        date_time_widget = QWidget()
        date_time_layout = QHBoxLayout(date_time_widget)
        date_time_layout.addWidget(QLabel("Date/time:"))
        date_picker = QLabel("localized date picker here")  # ??
        date_time_layout.addWidget(date_picker)
        time_input = QLabel("localized time editor here")  # ??
        date_time_layout.addWidget(time_input)

        # Table to display celestial objects
        self.table = default_table([
            'Name',
            'Type',
            'Magnitude',
            'Size in arcminutes',
            'Altitude',
            'Observability Index',
            '(normalized)'])

        # Add components to the layout
        self.layout.addWidget(self.import_button)
        self.layout.addWidget(weather_widget)
        self.layout.addWidget(date_time_widget)
        self.layout.addWidget(self.table)

    def import_data(self) -> None:
        # Open a dialog to select an Excel file and import data
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx)")
        if file_path:
            data: CelestialsList = AstroPlannerExcelImporter(file_path).import_data()
            self.populate_table(data)

    def populate_table(self, data: CelestialsList):
        for i, celestial_object in enumerate(data):
            self.table.insertRow(i)
            self.table.setItem(i, 0, centered_table_widget_item(celestial_object.name))
            self.table.setItem(i, 1, centered_table_widget_item(celestial_object.object_type))
            self.table.setItem(i, 2, centered_table_widget_item(str(celestial_object.magnitude)))
            self.table.setItem(i, 3, centered_table_widget_item(str(celestial_object.size)))
            self.table.setItem(i, 4, centered_table_widget_item(str(celestial_object.altitude)))
            self.table.setItem(i, 5, centered_table_widget_item(str(celestial_object.observability_score.score)))
            self.table.setItem(i, 6, centered_table_widget_item(str(celestial_object.observability_score.normalized_score)))
