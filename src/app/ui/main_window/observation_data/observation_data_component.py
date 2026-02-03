from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QWidget, QFileDialog, QComboBox, QLabel, QHBoxLayout, QFrame
)
from injector import inject

from app.config.autowire import component
from app.config.event_bus_config import bus, CelestialEvent
from app.domain.model.celestial_object import ScoredCelestialsList, CelestialsList
from app.domain.model.weather_conditions import WeatherConditions
from app.domain.services.observability_calculation_service import ObservabilityCalculationService
from app.orm.services.observation_site_service import ObservationSiteService
from app.orm.services.telescope_service import TelescopeService
from app.orm.services.eyepiece_service import EyepieceService
from app.utils.astroplanner_excel_importer import AstroPlannerExcelImporter
from app.utils.gui_helper import default_table, centered_table_widget_item
from app.utils.ui_debug_clipboard_watch import CUSTOM_NAME_PROPERTY


@component
class ObservationDataComponent(QWidget):
    @inject
    def __init__(self,
                 observability_calculation_service: ObservabilityCalculationService,
                 observation_site_service: ObservationSiteService,
                 telescope_service: TelescopeService,
                 eyepiece_service: EyepieceService):
        super().__init__(None)
        self.observability_calculation_service = observability_calculation_service
        self.observation_site_service = observation_site_service
        self.telescope_service = telescope_service
        self.eyepiece_service = eyepiece_service
        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)
        self._subscribe_to_events()

    # noinspection PyAttributeOutsideInit
    def init_ui(self):
        # Add guidance section at the top
        self.guidance_frame = self._create_guidance_section()
        self.layout.addWidget(self.guidance_frame)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)

        # Import buttons
        button_layout = QHBoxLayout()
        self.import_button = QPushButton("Import AstroPlanner's Excel export")
        self.import_button.clicked.connect(self.import_data)
        button_layout.addWidget(self.import_button)

        self.sample_data_button = QPushButton("Try with Sample Data")
        self.sample_data_button.clicked.connect(self.load_sample_data)
        button_layout.addWidget(self.sample_data_button)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        self.layout.addWidget(button_widget)

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
        self.layout.addWidget(weather_widget)
        self.layout.addWidget(date_time_widget)
        self.layout.addWidget(self.table)

    def import_data(self) -> None:
        # Open a dialog to select an Excel file and import data
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx)")
        if file_path:
            celestial_objects: CelestialsList = AstroPlannerExcelImporter(file_path).import_data()
            scored_celestial_objects: ScoredCelestialsList = self.observability_calculation_service.score_celestial_objects(celestial_objects)
            self.populate_table(scored_celestial_objects)

    def load_sample_data(self) -> None:
        """Load sample celestial objects to demonstrate the functionality"""
        from app.domain.model.celestial_object import CelestialObject

        sample_objects: CelestialsList = [
            CelestialObject(name="M31 - Andromeda Galaxy", object_type="DeepSky", magnitude=3.4, size=178.0, altitude=65.0),
            CelestialObject(name="M42 - Orion Nebula", object_type="DeepSky", magnitude=4.0, size=65.0, altitude=45.0),
            CelestialObject(name="M45 - Pleiades", object_type="DeepSky", magnitude=1.6, size=110.0, altitude=70.0),
            CelestialObject(name="Jupiter", object_type="Planet", magnitude=-2.5, size=0.7, altitude=40.0),
            CelestialObject(name="Saturn", object_type="Planet", magnitude=0.5, size=0.3, altitude=35.0),
            CelestialObject(name="M13 - Hercules Cluster", object_type="DeepSky", magnitude=5.8, size=20.0, altitude=55.0),
            CelestialObject(name="M57 - Ring Nebula", object_type="DeepSky", magnitude=8.8, size=1.4, altitude=50.0),
            CelestialObject(name="M27 - Dumbbell Nebula", object_type="DeepSky", magnitude=7.5, size=8.0, altitude=60.0),
            CelestialObject(name="Moon", object_type="Moon", magnitude=-12.6, size=31.0, altitude=42.0),
            CelestialObject(name="M51 - Whirlpool Galaxy", object_type="DeepSky", magnitude=8.4, size=11.0, altitude=68.0),
        ]

        scored_celestial_objects: ScoredCelestialsList = self.observability_calculation_service.score_celestial_objects(sample_objects)
        self.populate_table(scored_celestial_objects)

    def _create_guidance_section(self) -> QFrame:
        """Creates the guidance panel with setup status and instructions"""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)

        # Title
        title = QLabel("Get Started")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Import celestial object data from AstroPlanner to see which targets are "
            "easiest to observe with your equipment and location."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Configuration status
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self._update_configuration_status()
        layout.addWidget(self.status_label)

        return frame

    def _update_configuration_status(self):
        """Check and display configuration status"""
        sites = self.observation_site_service.get_all()
        telescopes = self.telescope_service.get_all()
        eyepieces = self.eyepiece_service.get_all()

        warnings = []
        if not sites:
            warnings.append("⚠️  No observation sites configured")
        if not telescopes:
            warnings.append("⚠️  No telescopes added")
        if not eyepieces:
            warnings.append("⚠️  No eyepieces added")

        if warnings:
            status_text = "\n".join(warnings) + "\n\nVisit the Setup tabs to configure your equipment and sites."
            self.status_label.setStyleSheet("color: #ff9800;")
        else:
            status_text = "✓ Setup complete! You can now import observation data."
            self.status_label.setStyleSheet("color: #4caf50;")

        self.status_label.setText(status_text)

    def populate_table(self, data: ScoredCelestialsList):
        # Sort by normalized score (descending - best targets first)
        sorted_data = sorted(data, key=lambda x: x.observability_score.normalized_score, reverse=True)

        # Clear existing rows
        self.table.setRowCount(0)

        for i, celestial_object in enumerate(sorted_data):
            self.table.insertRow(i)
            self.table.setItem(i, 0, centered_table_widget_item(celestial_object.name))
            self.table.setItem(i, 1, centered_table_widget_item(celestial_object.object_type))
            self.table.setItem(i, 2, centered_table_widget_item(str(celestial_object.magnitude)))
            self.table.setItem(i, 3, centered_table_widget_item(str(celestial_object.size)))
            self.table.setItem(i, 4, centered_table_widget_item(str(celestial_object.altitude)))
            self.table.setItem(i, 5, centered_table_widget_item(str(celestial_object.observability_score.score)))
            self.table.setItem(i, 6, centered_table_widget_item(str(celestial_object.observability_score.normalized_score)))

    def _subscribe_to_events(self):
        """Subscribe to equipment and site events to refresh configuration status"""
        # Observation site events
        bus.on(CelestialEvent.OBSERVATION_SITE_ADDED, lambda _: self._update_configuration_status())
        bus.on(CelestialEvent.OBSERVATION_SITE_DELETED, lambda _: self._update_configuration_status())

        # Telescope events
        bus.on(CelestialEvent.EQUIPMENT_TELESCOPE_ADDED, lambda _: self._update_configuration_status())
        bus.on(CelestialEvent.EQUIPMENT_TELESCOPE_DELETED, lambda _: self._update_configuration_status())

        # Eyepiece events
        bus.on(CelestialEvent.EQUIPMENT_EYEPIECE_ADDED, lambda _: self._update_configuration_status())
        bus.on(CelestialEvent.EQUIPMENT_EYEPIECE_DELETED, lambda _: self._update_configuration_status())
