from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QWidget
from PySide6.QtWidgets import QMessageBox

from app.domain.model.light_pollution import LightPollution
from app.orm.model.entities import ObservationSite
from app.utils.input_value_helper import parse_float_str, parse_str_float


class ObservationSiteDetailsDialog(QDialog):

    def __init__(self, parent=QWidget | None, observation_site: ObservationSite | None = None):
        super().__init__(parent)
        self.setWindowTitle("Observation Site Details")
        self.setMinimumWidth(500)
        self.observation_site_id: int | None = observation_site.id if observation_site else None
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.init_ui(layout, observation_site)

    # noinspection PyAttributeOutsideInit
    def init_ui(self, layout: QVBoxLayout, observation_site: ObservationSite | None = None):
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Home Garden, Out in the woods, Local Observatory club")
        self.name_edit.setText(observation_site.name if observation_site else "")
        self.latitude_edit = QLineEdit()
        self.latitude_edit.setPlaceholderText("e.g. 52.5200, optional")
        self.latitude_edit.setText(parse_float_str(observation_site.latitude) if observation_site else "")
        self.longitude_edit = QLineEdit()
        self.longitude_edit.setPlaceholderText("e.g. 13.4050, optional")
        self.longitude_edit.setText(parse_float_str(observation_site.longitude) if observation_site else "")

        self.light_pollution_combo = QComboBox()
        for lp in LightPollution:
            self.light_pollution_combo.addItem(lp.value, lp.name)
        self.light_pollution_combo.setCurrentText(observation_site.light_pollution.value if observation_site else "")

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        # Add widgets to the form layout
        form_layout = QFormLayout()
        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Latitude:", self.latitude_edit)
        form_layout.addRow("Longitude:", self.longitude_edit)
        form_layout.addRow("Light Pollution:", self.light_pollution_combo)

        # Add buttons to the layout
        layout.addLayout(form_layout)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)

        # Connect buttons to actions
        self.save_button.clicked.connect(self.on_save_clicked)
        self.cancel_button.clicked.connect(self.reject)

    def populate_form(self, observation_site: ObservationSite):
        self.name_edit.setText(observation_site.name)
        self.latitude_edit.setText(str(observation_site.latitude) if observation_site.latitude else "")
        self.longitude_edit.setText(str(observation_site.longitude) if observation_site.longitude else "")
        self.light_pollution_combo.setCurrentText(self.determine_light_pollution_selection(observation_site))

    @staticmethod
    def determine_light_pollution_selection(observation_site):
        if observation_site.light_pollution:
            return observation_site.light_pollution.value
        else:
            return LightPollution.BORTLE_6.value

    def on_save_clicked(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Mandatory Field", "The name field is required. Please enter a name for the observation site.")
            return
        self.accept()  # Close the dialog only if validation passes

    def to_observation_site(self):
        return ObservationSite(
            id=self.observation_site_id,
            name=self.name_edit.text(),
            latitude=parse_str_float(self.latitude_edit.text()),
            longitude=parse_str_float(self.longitude_edit.text()),
            light_pollution=LightPollution[self.light_pollution_combo.currentData()]
        )
