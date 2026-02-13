from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QWidget, QFileDialog, QComboBox, QLabel, QHBoxLayout, QFrame,
    QDateEdit, QTimeEdit, QProgressDialog, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, QDate, QTime
from injector import inject

from app.config.autowire import component
from app.config.event_bus_config import bus, CelestialEvent
from app.domain.model.celestial_object import ScoredCelestialsList, CelestialsList, CelestialObject
from app.domain.model.weather_conditions import WeatherConditions
from app.domain.services.observability_calculation_service import ObservabilityCalculationService
from app.orm.services.observation_site_service import ObservationSiteService
from app.orm.services.telescope_service import TelescopeService
from app.orm.services.eyepiece_service import EyepieceService
from app.utils.astroplanner_excel_importer import AstroPlannerExcelImporter
from app.utils.gui_helper import default_table, centered_table_widget_item
from app.object_lists.object_list_loader import ObjectListLoader
from app.object_lists.models import ResolutionFailure


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
        self.object_list_loader = ObjectListLoader()  # Phase 9.1: Pre-curated lists
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

        # Phase 9.1: Pre-curated Object List selector
        object_list_section = self._create_object_list_section()
        self.layout.addWidget(object_list_section)

        # Add separator between object lists and legacy import
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator2)

        # Legacy import buttons (kept for backward compatibility)
        import_label = QLabel("Or import from file:")
        import_label.setStyleSheet("color: #666; font-style: italic; margin-top: 5px;")
        self.layout.addWidget(import_label)

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
        from app.domain.model.object_classification import ObjectClassification

        sample_objects: CelestialsList = [
            CelestialObject(name="M31 - Andromeda Galaxy", canonical_id="M31", classification=ObjectClassification(primary_type="galaxy", subtype="spiral"), magnitude=3.4, size=178.0, altitude=65.0),
            CelestialObject(name="M42 - Orion Nebula", canonical_id="M42", classification=ObjectClassification(primary_type="nebula", subtype="emission"), magnitude=4.0, size=65.0, altitude=45.0),
            CelestialObject(name="M45 - Pleiades", canonical_id="M45", classification=ObjectClassification(primary_type="cluster", subtype="open"), magnitude=1.6, size=110.0, altitude=70.0),
            CelestialObject(name="Jupiter", canonical_id="Jupiter", classification=ObjectClassification(primary_type="planet"), magnitude=-2.5, size=0.7, altitude=40.0),
            CelestialObject(name="Saturn", canonical_id="Saturn", classification=ObjectClassification(primary_type="planet"), magnitude=0.5, size=0.3, altitude=35.0),
            CelestialObject(name="M13 - Hercules Cluster", canonical_id="M13", classification=ObjectClassification(primary_type="cluster", subtype="globular"), magnitude=5.8, size=20.0, altitude=55.0),
            CelestialObject(name="M57 - Ring Nebula", canonical_id="M57", classification=ObjectClassification(primary_type="nebula", subtype="planetary"), magnitude=8.8, size=1.4, altitude=50.0),
            CelestialObject(name="M27 - Dumbbell Nebula", canonical_id="M27", classification=ObjectClassification(primary_type="nebula", subtype="planetary"), magnitude=7.5, size=8.0, altitude=60.0),
            CelestialObject(name="Moon", canonical_id="Moon", classification=ObjectClassification(primary_type="moon"), magnitude=-12.6, size=31.0, altitude=42.0),
            CelestialObject(name="M51 - Whirlpool Galaxy", canonical_id="M51", classification=ObjectClassification(primary_type="galaxy", subtype="spiral"), magnitude=8.4, size=11.0, altitude=68.0),
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

    def _create_object_list_section(self) -> QGroupBox:
        """
        Phase 9.1: Create the pre-curated object list selector section.
        
        Provides dropdown for Messier, Caldwell, Solar System, etc.
        """
        group = QGroupBox("📋 Select Object List")
        layout = QHBoxLayout(group)

        # Dropdown for available lists
        self.object_list_combo = QComboBox()
        self.object_list_combo.setMinimumWidth(250)
        self._populate_object_list_dropdown()
        layout.addWidget(self.object_list_combo)

        # Load & Score button
        self.load_list_button = QPushButton("Load && Score")
        self.load_list_button.setToolTip(
            "Load the selected object list, resolve objects via catalog,\n"
            "and score them for observability with your equipment."
        )
        self.load_list_button.clicked.connect(self._load_and_score_object_list)
        layout.addWidget(self.load_list_button)

        # Status label for resolution results
        self.list_status_label = QLabel("")
        self.list_status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.list_status_label)

        layout.addStretch()

        return group

    def _populate_object_list_dropdown(self):
        """Populate the object list dropdown with available lists"""
        self.object_list_combo.clear()
        self.object_list_combo.addItem("Select a catalog...", None)

        try:
            available_lists = self.object_list_loader.get_available_lists()
            for list_meta in available_lists:
                display_text = f"{list_meta.name} ({list_meta.object_count} objects)"
                self.object_list_combo.addItem(display_text, list_meta.list_id)
        except Exception as e:
            self.object_list_combo.addItem(f"Error loading lists: {e}", None)

    def _load_and_score_object_list(self):
        """
        Load selected object list, resolve objects, and score them.
        
        Phase 9.1: Core workflow for pre-curated lists.
        """
        list_id = self.object_list_combo.currentData()
        if not list_id:
            self.list_status_label.setText("Please select a catalog first")
            self.list_status_label.setStyleSheet("color: #ff9800; font-style: italic;")
            return

        # Get list name for display
        list_name = self.object_list_combo.currentText()

        try:
            # Load the list
            obj_list = self.object_list_loader.load_list(list_id)
            total_objects = len(obj_list.objects)

            # Create progress dialog
            progress = QProgressDialog(
                f"Resolving {list_name}...",
                "Cancel",
                0,
                total_objects,
                self
            )
            progress.setWindowTitle("Loading Object List")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(500)  # Only show if takes > 500ms

            # Track if cancelled
            cancelled = False

            def update_progress(current, total):
                nonlocal cancelled
                progress.setValue(current)
                progress.setLabelText(f"Resolving objects... {current}/{total}")
                if progress.wasCanceled():
                    cancelled = True

            # Resolve objects
            result = self.object_list_loader.resolve_objects(obj_list, progress_callback=update_progress)
            progress.close()

            if cancelled:
                self.list_status_label.setText("Cancelled")
                self.list_status_label.setStyleSheet("color: #888; font-style: italic;")
                return

            # Update status
            if result.failure_count > 0:
                self.list_status_label.setText(
                    f"✓ {result.success_count}/{result.total_count} resolved"
                )
                self.list_status_label.setStyleSheet("color: #ff9800; font-style: italic;")
            else:
                self.list_status_label.setText(f"✓ {result.success_count} objects loaded")
                self.list_status_label.setStyleSheet("color: #4caf50; font-style: italic;")

            # Get selected equipment and score
            telescope, eyepiece, site = self._get_selected_equipment()
            scored_objects = self.observability_calculation_service.score_celestial_objects(
                result.resolved, telescope, eyepiece, site
            )

            # Create failure entries for table display (Decision #2: show in table)
            failure_entries = self._create_failure_table_entries(result.failures)

            # Populate table with scored objects + failures
            self.populate_table(
                scored_objects,
                data_source=f"Object List: {list_name}",
                failure_entries=failure_entries
            )

        except FileNotFoundError as e:
            QMessageBox.warning(self, "List Not Found", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error Loading List", f"Failed to load list: {e}")

    def _create_failure_table_entries(self, failures: list[ResolutionFailure]) -> list[dict]:
        """
        Create table entry dicts for failed resolutions.
        
        Decision #2: Include failures in the table with reason shown.
        """
        entries = []
        for failure in failures:
            entries.append({
                'name': failure.name,
                'type': '(Not Found)',
                'magnitude': '-',
                'size': '-',
                'altitude': '-',
                'score': '-',
                'normalized_score': failure.reason
            })
        return entries

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

    def populate_table(self, data: ScoredCelestialsList, data_source: str = "", failure_entries: list[dict] = None):
        """
        Populate the results table with scored objects.
        
        Args:
            data: List of scored celestial objects
            data_source: Display name for data source (e.g., "Messier Catalog")
            failure_entries: Optional list of failed resolution dicts to append (Phase 9.1)
        """
        # Sort by normalized score (descending - best targets first)
        sorted_data = sorted(data, key=lambda x: x.observability_score.normalized_score, reverse=True)

        # Clear existing rows
        self.table.setRowCount(0)

        # Show table and hide empty state when we have data
        if sorted_data or failure_entries:
            self.empty_state_label.hide()
            self.table.show()

            # Update and show data source indicator
            if data_source:
                self.data_source_label.setText(f"📂 {data_source}")
                self.data_source_label.show()

        # Add scored objects
        for i, celestial_object in enumerate(sorted_data):
            self.table.insertRow(i)
            self.table.setItem(i, 0, centered_table_widget_item(celestial_object.name))
            self.table.setItem(i, 1, centered_table_widget_item(celestial_object.object_type))
            self.table.setItem(i, 2, centered_table_widget_item(str(celestial_object.magnitude)))
            self.table.setItem(i, 3, centered_table_widget_item(str(celestial_object.size)))
            self.table.setItem(i, 4, centered_table_widget_item(str(celestial_object.altitude)))
            self.table.setItem(i, 5, centered_table_widget_item(str(celestial_object.observability_score.score)))
            self.table.setItem(i, 6, centered_table_widget_item(str(celestial_object.observability_score.normalized_score)))

        # Add failure entries at the bottom (Phase 9.1: show failures in table)
        if failure_entries:
            start_row = len(sorted_data)
            for j, failure in enumerate(failure_entries):
                row = start_row + j
                self.table.insertRow(row)
                
                # Name with warning icon
                name_item = centered_table_widget_item(f"⚠️ {failure['name']}")
                name_item.setToolTip(failure.get('normalized_score', 'Resolution failed'))
                self.table.setItem(row, 0, name_item)
                
                # Type shows "(Not Found)"
                type_item = centered_table_widget_item(failure['type'])
                type_item.setForeground(Qt.gray)
                self.table.setItem(row, 1, type_item)
                
                # Other columns are empty/dashes
                for col in range(2, 7):
                    item = centered_table_widget_item('-')
                    item.setForeground(Qt.gray)
                    self.table.setItem(row, col, item)

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
