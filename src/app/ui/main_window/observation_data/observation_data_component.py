from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QWidget, QFileDialog, QComboBox, QLabel, QHBoxLayout, QFrame,
    QDateEdit, QTimeEdit
)
from PySide6.QtCore import Qt, QDate, QTime
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
        self.tab_widget = None  # Will be set by MainWindow
        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)
        self._subscribe_to_events()

    def set_tab_widget(self, tab_widget):
        """Set reference to the parent tab widget for navigation"""
        self.tab_widget = tab_widget

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
        self.import_button.setToolTip(
            "Import an Excel file (.xlsx) exported from AstroPlanner.\n\n"
            "Required columns:\n"
            "• ID - Object name\n"
            "• Type - Object type (Planet, DeepSky, etc.)\n"
            "• Mag - Magnitude (brightness)\n"
            "• Size - Size in arcminutes or arcseconds\n"
            "• Altitude - Current altitude in degrees"
        )
        self.import_button.clicked.connect(self.import_data)
        button_layout.addWidget(self.import_button)

        self.sample_data_button = QPushButton("Try with Sample Data")
        self.sample_data_button.setToolTip(
            "Load sample celestial objects to see how the app works.\n"
            "Includes popular targets like M31, M42, Jupiter, and Saturn."
        )
        self.sample_data_button.clicked.connect(self.load_sample_data)
        button_layout.addWidget(self.sample_data_button)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        self.layout.addWidget(button_widget)

        # Create unified Observation Planning panel
        planning_panel = self._create_observation_planning_panel()
        self.layout.addWidget(planning_panel)

        # Table to display celestial objects
        self.table = default_table([
            'Object Name',
            'Type',
            'Magnitude',
            'Size (arcmin)',
            'Altitude (°)',
            'Observability Score',
            'Normalized Score (0-25)'])

        # Add tooltips to column headers
        self.table.horizontalHeaderItem(0).setToolTip("Name of the celestial object")
        self.table.horizontalHeaderItem(1).setToolTip("Object type (Planet, DeepSky, Moon, etc.)")
        self.table.horizontalHeaderItem(2).setToolTip("Apparent magnitude - lower numbers are brighter")
        self.table.horizontalHeaderItem(3).setToolTip("Angular size in arcminutes")
        self.table.horizontalHeaderItem(4).setToolTip("Current altitude above horizon in degrees")
        self.table.horizontalHeaderItem(5).setToolTip("Raw observability score based on brightness and size")
        self.table.horizontalHeaderItem(6).setToolTip("Normalized difficulty score - higher is easier to observe")

        # Enable sorting by clicking column headers
        self.table.setSortingEnabled(True)

        # Adjust column widths for better readability
        from PySide6.QtWidgets import QHeaderView
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Object Name - stretch to fill
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Magnitude
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Altitude
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Observability Score
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Normalized Score

        # Empty state placeholder
        self.empty_state_label = QLabel(
            "📊 No observation data loaded yet.\n\n"
            "Import your AstroPlanner data or try the sample data above to see "
            "which celestial objects are easiest to observe."
        )
        self.empty_state_label.setAlignment(Qt.AlignCenter)
        self.empty_state_label.setStyleSheet("color: #888; font-size: 13px; padding: 40px;")
        self.empty_state_label.setWordWrap(True)

        # Data source indicator
        self.data_source_label = QLabel()
        self.data_source_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        self.data_source_label.hide()  # Hidden until data is loaded

        # Add components to the layout
        self.layout.addWidget(self.data_source_label)
        self.layout.addWidget(self.empty_state_label)
        self.layout.addWidget(self.table)

        # Initially hide the table and show the empty state
        self.table.hide()
        self.empty_state_label.show()

    def import_data(self) -> None:
        # Open a dialog to select an Excel file and import data
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx)")
        if file_path:
            celestial_objects: CelestialsList = AstroPlannerExcelImporter(file_path).import_data()

            # Get selected equipment
            telescope, eyepiece, site = self._get_selected_equipment()

            # Score with equipment
            scored_celestial_objects: ScoredCelestialsList = self.observability_calculation_service.score_celestial_objects(
                celestial_objects, telescope, eyepiece, site)

            # Extract filename from path
            import os
            filename = os.path.basename(file_path)
            self.populate_table(scored_celestial_objects, data_source=f"Imported from: {filename}")

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

        # Get selected equipment
        telescope, eyepiece, site = self._get_selected_equipment()

        # Score with equipment
        scored_celestial_objects: ScoredCelestialsList = self.observability_calculation_service.score_celestial_objects(
            sample_objects, telescope, eyepiece, site)
        self.populate_table(scored_celestial_objects, data_source="Sample Data (10 popular celestial objects)")

    def _create_observation_planning_panel(self) -> QFrame:
        """Create the unified Observation Planning panel with When/Where/Equipment sections"""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setFrameShadow(QFrame.Raised)
        panel_layout = QVBoxLayout(panel)

        # Panel title
        title = QLabel("📋 Observation Planning")
        title.setStyleSheet("font-weight: bold; font-size: 13px; padding: 5px;")
        panel_layout.addWidget(title)

        # WHEN section
        when_layout = QHBoxLayout()
        when_layout.addWidget(QLabel("📅 When:"))

        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setDisplayFormat("yyyy-MM-dd")
        self.date_picker.dateChanged.connect(self._on_datetime_changed)
        when_layout.addWidget(self.date_picker)

        self.time_picker = QTimeEdit()
        self.time_picker.setTime(QTime.currentTime())
        self.time_picker.setDisplayFormat("HH:mm")
        self.time_picker.timeChanged.connect(self._on_datetime_changed)
        when_layout.addWidget(self.time_picker)

        when_layout.addStretch()
        panel_layout.addLayout(when_layout)

        # Weather sub-section (indented under WHEN)
        weather_layout = QHBoxLayout()
        weather_layout.addSpacing(20)  # Indent
        weather_layout.addWidget(QLabel("☁️  Weather:"))

        self.weather_status_label = QLabel("Checking...")
        self.weather_status_label.setStyleSheet("color: #888; font-style: italic;")
        weather_layout.addWidget(self.weather_status_label)

        weather_layout.addWidget(QLabel("→"))

        self.weather_combo = QComboBox()
        for wc in WeatherConditions:
            self.weather_combo.addItem(wc.value, wc.name)
        self.weather_combo.setCurrentText(WeatherConditions.CLEAR.value)
        weather_layout.addWidget(self.weather_combo)

        weather_layout.addStretch()
        panel_layout.addLayout(weather_layout)

        # WHERE section
        where_layout = QHBoxLayout()
        where_layout.addWidget(QLabel("📍 Where:"))

        self.site_combo = QComboBox()
        self.site_combo.addItem("(None)", None)
        self.site_combo.currentIndexChanged.connect(self._on_site_changed)
        where_layout.addWidget(self.site_combo)

        where_layout.addStretch()
        panel_layout.addLayout(where_layout)

        # Light pollution sub-section (indented under WHERE)
        light_poll_layout = QHBoxLayout()
        light_poll_layout.addSpacing(20)  # Indent
        light_poll_layout.addWidget(QLabel("🌃 Light Pollution:"))

        self.light_pollution_status_label = QLabel("From site")
        self.light_pollution_status_label.setStyleSheet("color: #888; font-style: italic;")
        light_poll_layout.addWidget(self.light_pollution_status_label)

        light_poll_layout.addWidget(QLabel("→"))

        self.light_pollution_combo = QComboBox()
        from app.domain.model.light_pollution import LightPollution
        for lp in LightPollution:
            if lp != LightPollution.UNKNOWN:
                self.light_pollution_combo.addItem(lp.value, lp)
        light_poll_layout.addWidget(self.light_pollution_combo)

        light_poll_layout.addStretch()
        panel_layout.addLayout(light_poll_layout)

        # EQUIPMENT section
        equipment_layout = QHBoxLayout()
        equipment_layout.addWidget(QLabel("🔭 Equipment:"))

        self.telescope_combo = QComboBox()
        self.telescope_combo.addItem("(None)", None)
        equipment_layout.addWidget(self.telescope_combo)

        self.eyepiece_combo = QComboBox()
        self.eyepiece_combo.addItem("(None)", None)
        equipment_layout.addWidget(self.eyepiece_combo)

        equipment_layout.addStretch()
        panel_layout.addLayout(equipment_layout)

        # Populate equipment dropdowns
        self._populate_equipment_dropdowns()

        # Initial weather status
        self._update_weather_status()
        self._update_light_pollution_status()

        return panel

    def _on_datetime_changed(self):
        """Called when date or time changes - trigger weather API"""
        self._update_weather_status()

    def _update_weather_status(self):
        """Update weather status label (will call API in future)"""
        # TODO: Call weather API
        # For now, show placeholder
        date = self.date_picker.date()
        time = self.time_picker.time()
        days_ahead = QDate.currentDate().daysTo(date)

        if days_ahead > 10:
            self.weather_status_label.setText("Unknown (too far ahead)")
            self.weather_status_label.setStyleSheet("color: #ff9800; font-style: italic;")
        elif days_ahead < 0:
            self.weather_status_label.setText("Historical data unavailable")
            self.weather_status_label.setStyleSheet("color: #888; font-style: italic;")
        else:
            # Placeholder for API call
            self.weather_status_label.setText(f"Forecast: {days_ahead}d ahead")
            self.weather_status_label.setStyleSheet("color: #4caf50; font-style: italic;")

    def _update_light_pollution_status(self):
        """Update light pollution status based on selected site"""
        site = self.site_combo.currentData()
        if site and hasattr(site, 'light_pollution'):
            # Extract Bortle number
            bortle_name = site.light_pollution.value
            self.light_pollution_status_label.setText(f"From site ({bortle_name})")
            self.light_pollution_status_label.setStyleSheet("color: #4caf50; font-style: italic;")

            # Pre-select in dropdown
            for i in range(self.light_pollution_combo.count()):
                if self.light_pollution_combo.itemData(i) == site.light_pollution:
                    self.light_pollution_combo.setCurrentIndex(i)
                    break
        else:
            self.light_pollution_status_label.setText("No site selected")
            self.light_pollution_status_label.setStyleSheet("color: #888; font-style: italic;")

    def _populate_equipment_dropdowns(self):
        """Populate dropdowns with available equipment"""
        # Populate observation sites
        sites = self.observation_site_service.get_all()
        for site in sites:
            self.site_combo.addItem(site.name, site)

        # Populate telescopes
        telescopes = self.telescope_service.get_all()
        for telescope in telescopes:
            self.telescope_combo.addItem(telescope.name, telescope)

        # Populate eyepieces
        eyepieces = self.eyepiece_service.get_all()
        for eyepiece in eyepieces:
            self.eyepiece_combo.addItem(f"{eyepiece.name} ({eyepiece.focal_length}mm)", eyepiece)

    def _on_site_changed(self, index):
        """When observation site changes, load its default equipment and update light pollution"""
        site = self.site_combo.itemData(index)
        if site and hasattr(site, 'telescopes') and hasattr(site, 'eyepieces'):
            # If site has equipment, select the first telescope and eyepiece
            if site.telescopes:
                # Find this telescope in the combo
                for i in range(self.telescope_combo.count()):
                    if self.telescope_combo.itemData(i) == site.telescopes[0]:
                        self.telescope_combo.setCurrentIndex(i)
                        break

            if site.eyepieces:
                # Find this eyepiece in the combo
                for i in range(self.eyepiece_combo.count()):
                    if self.eyepiece_combo.itemData(i) == site.eyepieces[0]:
                        self.eyepiece_combo.setCurrentIndex(i)
                        break

        # Update light pollution status when site changes
        self._update_light_pollution_status()

    def _get_selected_equipment(self):
        """Get currently selected equipment from dropdowns"""
        telescope = self.telescope_combo.currentData()
        eyepiece = self.eyepiece_combo.currentData()
        site = self.site_combo.currentData()
        return telescope, eyepiece, site

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

        # Configuration status container
        self.status_container = QWidget()
        self.status_layout = QVBoxLayout(self.status_container)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        self._update_configuration_status()
        layout.addWidget(self.status_container)

        return frame

    def _update_configuration_status(self):
        """Check and display configuration status"""
        # Clear existing widgets
        while self.status_layout.count():
            child = self.status_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        sites = self.observation_site_service.get_all()
        telescopes = self.telescope_service.get_all()
        eyepieces = self.eyepiece_service.get_all()

        has_warnings = False

        # Check and add warning buttons for missing configuration
        if not sites:
            warning_widget = self._create_warning_widget(
                "⚠️  No observation sites configured",
                "Add Observation Site",
                lambda: self._switch_to_tab(1)  # Tab index 1 = Setup: Observation Sites
            )
            self.status_layout.addWidget(warning_widget)
            has_warnings = True

        if not telescopes:
            warning_widget = self._create_warning_widget(
                "⚠️  No telescopes added",
                "Add Telescope",
                lambda: self._switch_to_tab(2)  # Tab index 2 = Setup: Equipment
            )
            self.status_layout.addWidget(warning_widget)
            has_warnings = True

        if not eyepieces:
            warning_widget = self._create_warning_widget(
                "⚠️  No eyepieces added",
                "Add Eyepiece",
                lambda: self._switch_to_tab(2)  # Tab index 2 = Setup: Equipment
            )
            self.status_layout.addWidget(warning_widget)
            has_warnings = True

        if not has_warnings:
            success_label = QLabel("✓ Setup complete! You can now import observation data.")
            success_label.setStyleSheet("color: #4caf50;")
            self.status_layout.addWidget(success_label)

    def _switch_to_tab(self, tab_index: int):
        """Switch to the specified tab in the parent tab widget"""
        if self.tab_widget:
            self.tab_widget.setCurrentIndex(tab_index)

    def _create_warning_widget(self, message: str, button_text: str, callback) -> QWidget:
        """Creates a warning message with an action button"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 5, 0, 5)

        label = QLabel(message)
        label.setStyleSheet("color: #ff9800;")
        layout.addWidget(label)

        button = QPushButton(button_text)
        button.setMaximumWidth(150)
        button.clicked.connect(callback)
        layout.addWidget(button)

        layout.addStretch()

        return widget

    def populate_table(self, data: ScoredCelestialsList, data_source: str = ""):
        # Sort by normalized score (descending - best targets first)
        sorted_data = sorted(data, key=lambda x: x.observability_score.normalized_score, reverse=True)

        # Clear existing rows
        self.table.setRowCount(0)

        # Show table and hide empty state when we have data
        if sorted_data:
            self.empty_state_label.hide()
            self.table.show()

            # Update and show data source indicator
            if data_source:
                self.data_source_label.setText(f"📂 {data_source}")
                self.data_source_label.show()

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
        """Subscribe to equipment and site events to refresh configuration status and dropdowns"""
        # Observation site events
        bus.on(CelestialEvent.OBSERVATION_SITE_ADDED, lambda _: self._on_equipment_changed())
        bus.on(CelestialEvent.OBSERVATION_SITE_DELETED, lambda _: self._on_equipment_changed())

        # Telescope events
        bus.on(CelestialEvent.EQUIPMENT_TELESCOPE_ADDED, lambda _: self._on_equipment_changed())
        bus.on(CelestialEvent.EQUIPMENT_TELESCOPE_DELETED, lambda _: self._on_equipment_changed())

        # Eyepiece events
        bus.on(CelestialEvent.EQUIPMENT_EYEPIECE_ADDED, lambda _: self._on_equipment_changed())
        bus.on(CelestialEvent.EQUIPMENT_EYEPIECE_DELETED, lambda _: self._on_equipment_changed())

    def _on_equipment_changed(self):
        """Refresh configuration status and equipment dropdowns when equipment changes"""
        self._update_configuration_status()
        self._refresh_equipment_dropdowns()

    def _refresh_equipment_dropdowns(self):
        """Refresh all equipment dropdowns (preserve selections if possible)"""
        # Save current selections
        current_site = self.site_combo.currentData()
        current_telescope = self.telescope_combo.currentData()
        current_eyepiece = self.eyepiece_combo.currentData()

        # Clear and repopulate
        self.site_combo.clear()
        self.site_combo.addItem("(None)", None)
        self.telescope_combo.clear()
        self.telescope_combo.addItem("(None)", None)
        self.eyepiece_combo.clear()
        self.eyepiece_combo.addItem("(None)", None)

        self._populate_equipment_dropdowns()

        # Restore selections if items still exist
        if current_site:
            for i in range(self.site_combo.count()):
                if self.site_combo.itemData(i) == current_site:
                    self.site_combo.setCurrentIndex(i)
                    break

        if current_telescope:
            for i in range(self.telescope_combo.count()):
                if self.telescope_combo.itemData(i) == current_telescope:
                    self.telescope_combo.setCurrentIndex(i)
                    break

        if current_eyepiece:
            for i in range(self.eyepiece_combo.count()):
                if self.eyepiece_combo.itemData(i) == current_eyepiece:
                    self.eyepiece_combo.setCurrentIndex(i)
                    break
