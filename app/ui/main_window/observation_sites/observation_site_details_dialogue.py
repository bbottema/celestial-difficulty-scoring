from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QWidget
from PySide6.QtWidgets import QMessageBox
from domain.entities.observation_site import ObservationSite
from domain.light_pollution import LightPollution
from domain.weather_conditions import WeatherConditions
from utils.input_value_helper import parse_str_float, parse_float_str


class ObservationSiteDetailsDialog(QDialog):

    def __init__(self, parent=QWidget | None, observation_site: ObservationSite | None = None):
        super().__init__(parent)
        self.setWindowTitle("Observation Site Details")
        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.init_ui(observation_site)
        self.setLayout(self.layout)

    # noinspection PyAttributeOutsideInit
    def init_ui(self, observation_site: ObservationSite | None = None):
        self.name_edit = QLineEdit()
        self.name_edit.setText(parse_float_str(observation_site.name) if observation_site else "")
        self.latitude_edit = QLineEdit()
        self.latitude_edit.setText(parse_float_str(observation_site.latitude) if observation_site else "")
        self.longitude_edit = QLineEdit()
        self.longitude_edit.setText(parse_float_str(observation_site.longitude) if observation_site else "")

        self.weather_conditions_combo = QComboBox()
        for wc in WeatherConditions:
            self.weather_conditions_combo.addItem(wc.value, wc.name)
        self.weather_conditions_combo.setCurrentText(observation_site.weather_conditions.value if observation_site else "")

        self.light_pollution_combo = QComboBox()
        for lp in LightPollution:
            self.light_pollution_combo.addItem(lp.value, lp.name)
        self.light_pollution_combo.setCurrentText(observation_site.light_pollution.value if observation_site else "")

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        # Add widgets to the form layout
        self.form_layout.addRow("Name:", self.name_edit)
        self.form_layout.addRow("Latitude:", self.latitude_edit)
        self.form_layout.addRow("Longitude:", self.longitude_edit)
        self.form_layout.addRow("Weather Conditions:", self.weather_conditions_combo)
        self.form_layout.addRow("Light Pollution:", self.light_pollution_combo)

        # Add buttons to the layout
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.cancel_button)

        # Connect buttons to actions
        self.save_button.clicked.connect(self.on_save_clicked)
        self.cancel_button.clicked.connect(self.reject)

    def populate_form(self, observation_site: ObservationSite):
        self.name_edit.setText(observation_site.name)
        self.latitude_edit.setText(str(observation_site.latitude) if observation_site.latitude else "")
        self.longitude_edit.setText(str(observation_site.longitude) if observation_site.longitude else "")
        self.weather_conditions_combo.setCurrentText(self.determine_weather_condition_selection(observation_site))
        self.light_pollution_combo.setCurrentText(self.determine_light_pollution_selection(observation_site))

    @staticmethod
    def determine_weather_condition_selection(observation_site):
        if observation_site.weather_conditions:
            return observation_site.weather_conditions.value
        else:
            return WeatherConditions.CLEAR.value

    @staticmethod
    def determine_light_pollution_selection(observation_site):
        if observation_site.light_pollution:
            return observation_site.light_pollution.value
        else:
            return LightPollution.BORTLE_5.value

    def on_save_clicked(self):
        if not self.name_edit.text().strip():
            # Name field is empty, show an error message and do not close the dialog
            QMessageBox.warning(self, "Mandatory Field", "The name field is required. Please enter a name for the observation site.")
            return
        self.accept()  # Close the dialog only if validation passes

    def to_observation_site(self):
        return ObservationSite(
            name=self.name_edit.text(),
            latitude=parse_str_float(self.latitude_edit.text()),
            longitude=parse_str_float(self.longitude_edit.text()),
            weather_conditions=WeatherConditions[self.weather_conditions_combo.currentData()],
            light_pollution=LightPollution[self.light_pollution_combo.currentData()]
        )
