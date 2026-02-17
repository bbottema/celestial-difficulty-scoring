from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTextEdit, QLabel, QGroupBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QSpinBox, QComboBox
)
from PySide6.QtCore import Qt
from injector import inject
from pathlib import Path
import traceback

from app.config.autowire import component
from app.catalog.catalog_service import CatalogService
from app.catalog.providers.openngc_provider import OpenNGCProvider


@component
class CatalogDataComponent(QWidget):
    @inject
    def __init__(self, catalog_service: CatalogService):
        super().__init__(None)
        self.catalog_service = catalog_service
        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)

    def init_ui(self):
        # Create sub-tabs
        self.subtabs = QTabWidget()

        # OpenNGC parent tab with nested tabs
        self.openngc_parent_widget = self._create_openngc_parent_tab()
        self.subtabs.addTab(self.openngc_parent_widget, "OpenNGC Provider")

        # Provider tabs
        self.simbad_widget = self._create_simbad_provider_tab()
        self.subtabs.addTab(self.simbad_widget, "SIMBAD Provider")

        self.horizons_widget = self._create_horizons_provider_tab()
        self.subtabs.addTab(self.horizons_widget, "Horizons Provider")

        self.layout.addWidget(self.subtabs)

    def _create_openngc_parent_tab(self):
        """Create OpenNGC parent tab with nested tabs for Lookup, Browser, and Provider"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Info
        info = QLabel("OpenNGC catalog access - Lookup objects, browse catalog, or test provider API")
        info.setStyleSheet("font-style: italic; color: gray; padding: 5px;")
        layout.addWidget(info)

        # Create nested tabs for OpenNGC features
        openngc_tabs = QTabWidget()

        # Lookup subtab
        self.lookup_widget = self._create_lookup_tab()
        openngc_tabs.addTab(self.lookup_widget, "Lookup")

        # Browser subtab
        self.browser_widget = self._create_browser_tab()
        openngc_tabs.addTab(self.browser_widget, "Browser")

        # OpenNGC provider tab
        self.openngc_widget = self._create_openngc_provider_tab()
        openngc_tabs.addTab(self.openngc_widget, "Search")

        layout.addWidget(openngc_tabs)
        widget.setLayout(layout)
        return widget

    def _create_lookup_tab(self):
        """Create the object lookup subtab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Catalog Data Lookup")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Search section
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout()

        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter object name (e.g., M31, NGC7000, Jupiter)")
        self.search_input.returnPressed.connect(self.on_search)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.on_search)

        search_input_layout.addWidget(QLabel("Object:"))
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(self.search_button)

        search_layout.addLayout(search_input_layout)
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Results section
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Search results will appear here...")

        results_layout.addWidget(self.results_text)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        widget.setLayout(layout)
        return widget

    def _create_browser_tab(self):
        """Create the catalog browser subtab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("OpenNGC Catalog Browser")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        info_label = QLabel("Browse the complete OpenNGC catalog (~14,000 deep-sky objects)")
        info_label.setStyleSheet("font-style: italic; color: gray;")
        layout.addWidget(info_label)

        # Controls
        controls_layout = QHBoxLayout()

        # Page size selector
        controls_layout.addWidget(QLabel("Page size:"))
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setRange(10, 500)
        self.page_size_spin.setValue(50)
        self.page_size_spin.setSingleStep(10)
        self.page_size_spin.valueChanged.connect(self.on_page_size_changed)
        controls_layout.addWidget(self.page_size_spin)

        # Type filter
        controls_layout.addWidget(QLabel("Filter by type:"))
        self.type_filter_combo = QComboBox()
        self.type_filter_combo.addItem("All", None)
        self.type_filter_combo.addItem("Galaxies (G)", "G")
        self.type_filter_combo.addItem("Emission Nebulae (HII, EmN)", "nebula_emission")
        self.type_filter_combo.addItem("Planetary Nebulae (PN)", "PN")
        self.type_filter_combo.addItem("Open Clusters (OCl)", "OCl")
        self.type_filter_combo.addItem("Globular Clusters (GCl)", "GCl")
        self.type_filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        controls_layout.addWidget(self.type_filter_combo)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Pagination controls
        pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.on_previous_page)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.on_next_page)
        self.page_label = QLabel("Page 1 of ?")

        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addStretch()
        layout.addLayout(pagination_layout)

        # Table
        self.catalog_table = QTableWidget()
        self.catalog_table.setColumnCount(8)
        self.catalog_table.setHorizontalHeaderLabels([
            "ID", "Type", "RA", "Dec", "Mag", "Size", "Classification", "Common Name"
        ])
        self.catalog_table.horizontalHeader().setStretchLastSection(True)
        self.catalog_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.catalog_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.catalog_table.cellDoubleClicked.connect(self.on_row_double_clicked)

        layout.addWidget(self.catalog_table)

        widget.setLayout(layout)

        # Initialize browser state
        self.current_page = 0
        self.page_size = 50
        self.type_filter = None
        self.filtered_data = None
        self.openngc_provider = None

        # Load initial data
        self.load_catalog_data()

        return widget

    # Lookup tab methods
    def on_search(self):
        query = self.search_input.text().strip()
        if not query:
            self.results_text.setPlainText("Please enter an object name.")
            return

        self.results_text.setPlainText(f"Searching for '{query}'...\n")

        try:
            # Try to get the object
            obj = self.catalog_service.get_object(query)

            if obj is None:
                self.results_text.setPlainText(f"Object '{query}' not found.\n\nTried providers based on name pattern.")
                return

            # Format the results
            result_text = self._format_object(obj)
            self.results_text.setPlainText(result_text)

        except Exception as e:
            print(f"ERROR searching for {query}: {e}")
            traceback.print_exc()
            self.results_text.setPlainText(f"Error: {str(e)}\n\nCheck console for full traceback.")

    def _format_object(self, obj) -> str:
        """Format a CelestialObject for display"""
        lines = []
        lines.append(f"=== {obj.canonical_id} ===\n")

        # Basic info
        lines.append("BASIC INFORMATION")
        lines.append(f"  Canonical ID: {obj.canonical_id}")
        if obj.aliases:
            lines.append(f"  Aliases: {', '.join(obj.aliases)}")
        lines.append(f"  Classification: {obj.classification.primary_type}")
        if obj.classification.subtype:
            lines.append(f"    Subtype: {obj.classification.subtype}")
        if obj.classification.morphology:
            lines.append(f"    Morphology: {obj.classification.morphology}")
        lines.append("")

        # Position
        lines.append("POSITION")
        lines.append(f"  RA: {obj.ra:.6f}°")
        lines.append(f"  Dec: {obj.dec:.6f}°")
        lines.append("")

        # Physical properties
        lines.append("PROPERTIES")
        if obj.magnitude is not None and obj.magnitude < 90:
            lines.append(f"  Magnitude: {obj.magnitude:.2f}")
        if obj.size:
            size_str = f"{obj.size.major_arcmin:.2f}'"
            if obj.size.minor_arcmin is not None:
                size_str += f" × {obj.size.minor_arcmin:.2f}'"
            lines.append(f"  Angular Size: {size_str}")
            if obj.size.position_angle_deg is not None:
                lines.append(f"    Position Angle: {obj.size.position_angle_deg}°")
        if obj.surface_brightness:
            lines.append(f"  Surface Brightness: {obj.surface_brightness.value:.2f} mag/arcsec²")
            lines.append(f"    Source: {obj.surface_brightness.source}")
            if obj.surface_brightness.band:
                lines.append(f"    Band: {obj.surface_brightness.band}")
        lines.append("")

        # Provenance
        lines.append("DATA PROVENANCE")
        for i, prov in enumerate(obj.provenance, 1):
            lines.append(f"  Source {i}: {prov.source}")
            lines.append(f"    Fetched: {prov.fetched_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            lines.append(f"    Confidence: {prov.confidence:.2f}")
            if prov.catalog_version:
                lines.append(f"    Version: {prov.catalog_version}")

        return "\n".join(lines)

    # Browser tab methods
    def load_catalog_data(self):
        """Load OpenNGC catalog data"""
        try:
            # Initialize OpenNGC provider if not already done
            if self.openngc_provider is None:
                # Path from this file: src/app/ui/main_window/catalog_data/catalog_data_component.py
                # Need to go up 6 levels to project root, then into data/catalogs
                csv_path = Path(__file__).parent.parent.parent.parent.parent.parent / "data" / "catalogs" / "NGC.csv"
                print(f"Loading OpenNGC from: {csv_path}")
                self.openngc_provider = OpenNGCProvider(csv_path)

            # Get dataframe
            df = self.openngc_provider.df

            # Apply type filter
            if self.type_filter:
                if self.type_filter == "nebula_emission":
                    df = df[df['obj_type'].isin(['HII', 'EmN'])]
                else:
                    df = df[df['obj_type'] == self.type_filter]

            self.filtered_data = df
            self.current_page = 0
            self.update_table()

        except Exception as e:
            print(f"ERROR loading catalog: {e}")
            traceback.print_exc()
            self.catalog_table.setRowCount(1)
            self.catalog_table.setItem(0, 0, QTableWidgetItem(f"Error loading catalog: {str(e)}"))

    def update_table(self):
        """Update table with current page of data"""
        if self.filtered_data is None or len(self.filtered_data) == 0:
            self.catalog_table.setRowCount(0)
            self.page_label.setText("No data")
            return

        # Calculate pagination
        total_rows = len(self.filtered_data)
        total_pages = (total_rows + self.page_size - 1) // self.page_size
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, total_rows)

        # Update label
        self.page_label.setText(f"Page {self.current_page + 1} of {total_pages} ({total_rows} objects)")

        # Update button states
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)

        # Get page data
        page_data = self.filtered_data.iloc[start_idx:end_idx]

        # Populate table
        self.catalog_table.setRowCount(len(page_data))

        for row_idx, (_, row) in enumerate(page_data.iterrows()):
            # ID
            self.catalog_table.setItem(row_idx, 0, QTableWidgetItem(str(row.get('name', ''))))

            # Type
            obj_type = row.get('obj_type', '')
            self.catalog_table.setItem(row_idx, 1, QTableWidgetItem(str(obj_type)))

            # RA (sexagesimal)
            ra = row.get('ra_sex', row.get('ra', ''))
            self.catalog_table.setItem(row_idx, 2, QTableWidgetItem(str(ra) if ra else ''))

            # Dec (sexagesimal)
            dec = row.get('dec_sex', row.get('dec', ''))
            self.catalog_table.setItem(row_idx, 3, QTableWidgetItem(str(dec) if dec else ''))

            # Magnitude
            mag = row.get('mag_v', '')
            self.catalog_table.setItem(row_idx, 4, QTableWidgetItem(str(mag) if mag else ''))

            # Size
            maj = row.get('maj_arcmin', '')
            min_ax = row.get('min_arcmin', '')
            if maj:
                size_str = f"{maj}'"
                if min_ax:
                    size_str += f" × {min_ax}'"
                self.catalog_table.setItem(row_idx, 5, QTableWidgetItem(size_str))
            else:
                self.catalog_table.setItem(row_idx, 5, QTableWidgetItem(''))

            # Classification (Hubble type for galaxies)
            hubble = row.get('hubble_type', '')
            self.catalog_table.setItem(row_idx, 6, QTableWidgetItem(str(hubble) if hubble else ''))

            # Common name
            common = row.get('comname', '')
            messier = row.get('messier_nr', '')
            name_str = ''
            if messier:
                name_str = f"M{messier}"
            if common:
                if name_str:
                    name_str += f" ({common})"
                else:
                    name_str = common
            self.catalog_table.setItem(row_idx, 7, QTableWidgetItem(name_str))

    def on_previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table()

    def on_next_page(self):
        """Go to next page"""
        total_rows = len(self.filtered_data) if self.filtered_data is not None else 0
        total_pages = (total_rows + self.page_size - 1) // self.page_size
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_table()

    def on_page_size_changed(self, value):
        """Handle page size change"""
        self.page_size = value
        self.current_page = 0
        self.update_table()

    def on_filter_changed(self, index):
        """Handle type filter change"""
        self.type_filter = self.type_filter_combo.itemData(index)
        self.load_catalog_data()

    def on_row_double_clicked(self, row, column):
        """Handle double-click on table row - load object in Lookup tab"""
        object_id = self.catalog_table.item(row, 0).text()
        self.search_input.setText(object_id)
        self.subtabs.setCurrentIndex(0)  # Switch to Lookup tab
        self.on_search()

    # Provider tabs
    def _create_openngc_provider_tab(self):
        """Create OpenNGC provider testing tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Search OpenNGC")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        info = QLabel("Query the local OpenNGC catalog directly. This is a local CSV file with ~14,000 objects.")
        info.setStyleSheet("font-style: italic; color: gray;")
        layout.addWidget(info)

        # Query section
        query_group = QGroupBox("Query Parameters")
        query_layout = QVBoxLayout()

        # Object ID input
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Object ID:"))
        self.openngc_id_input = QLineEdit()
        self.openngc_id_input.setPlaceholderText("e.g., NGC7000, M31, IC1396")
        self.openngc_id_input.returnPressed.connect(self.on_openngc_query)
        id_layout.addWidget(self.openngc_id_input)
        query_layout.addLayout(id_layout)

        # Query button
        button_layout = QHBoxLayout()
        openngc_query_btn = QPushButton("Query get_object()")
        openngc_query_btn.clicked.connect(self.on_openngc_query)
        button_layout.addWidget(openngc_query_btn)

        openngc_resolve_btn = QPushButton("Query resolve_name()")
        openngc_resolve_btn.clicked.connect(self.on_openngc_resolve)
        button_layout.addWidget(openngc_resolve_btn)
        button_layout.addStretch()
        query_layout.addLayout(button_layout)

        query_group.setLayout(query_layout)
        layout.addWidget(query_group)

        # Results
        results_group = QGroupBox("Raw Response")
        results_layout = QVBoxLayout()
        self.openngc_results = QTextEdit()
        self.openngc_results.setReadOnly(True)
        self.openngc_results.setPlaceholderText("Query results will appear here...")
        results_layout.addWidget(self.openngc_results)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        widget.setLayout(layout)
        return widget

    def _create_simbad_provider_tab(self):
        """Create SIMBAD provider testing tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Search SIMBAD")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        info = QLabel("Query SIMBAD astronomical database (online). Rate limit: ~5 queries/sec.")
        info.setStyleSheet("font-style: italic; color: gray;")
        layout.addWidget(info)

        # Query section
        query_group = QGroupBox("Query Parameters")
        query_layout = QVBoxLayout()

        # Object name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Object Name:"))
        self.simbad_name_input = QLineEdit()
        self.simbad_name_input.setPlaceholderText("e.g., M31, NGC7000, Betelgeuse")
        self.simbad_name_input.returnPressed.connect(self.on_simbad_query)
        name_layout.addWidget(self.simbad_name_input)
        query_layout.addLayout(name_layout)

        # Query button
        button_layout = QHBoxLayout()
        simbad_query_btn = QPushButton("Query get_object()")
        simbad_query_btn.clicked.connect(self.on_simbad_query)
        button_layout.addWidget(simbad_query_btn)

        simbad_resolve_btn = QPushButton("Query resolve_name()")
        simbad_resolve_btn.clicked.connect(self.on_simbad_resolve)
        button_layout.addWidget(simbad_resolve_btn)
        button_layout.addStretch()
        query_layout.addLayout(button_layout)

        query_group.setLayout(query_layout)
        layout.addWidget(query_group)

        # Results
        results_group = QGroupBox("Raw Response")
        results_layout = QVBoxLayout()
        self.simbad_results = QTextEdit()
        self.simbad_results.setReadOnly(True)
        self.simbad_results.setPlaceholderText("Query results will appear here (may take a few seconds)...")
        results_layout.addWidget(self.simbad_results)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        widget.setLayout(layout)
        return widget

    def _create_horizons_provider_tab(self):
        """Create Horizons provider testing tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Search Horizons")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        info = QLabel("Query JPL Horizons for Solar System objects (online). Uses current UTC time and geocenter.")
        info.setStyleSheet("font-style: italic; color: gray;")
        layout.addWidget(info)

        # Query section
        query_group = QGroupBox("Query Parameters")
        query_layout = QVBoxLayout()

        # Object name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Object Name:"))
        self.horizons_name_input = QLineEdit()
        self.horizons_name_input.setPlaceholderText("e.g., Jupiter, Mars, Moon, Venus")
        self.horizons_name_input.returnPressed.connect(self.on_horizons_query)
        name_layout.addWidget(self.horizons_name_input)
        query_layout.addLayout(name_layout)

        # Query button
        button_layout = QHBoxLayout()
        horizons_query_btn = QPushButton("Query get_object()")
        horizons_query_btn.clicked.connect(self.on_horizons_query)
        button_layout.addWidget(horizons_query_btn)
        button_layout.addStretch()
        query_layout.addLayout(button_layout)

        query_group.setLayout(query_layout)
        layout.addWidget(query_group)

        # Results
        results_group = QGroupBox("Raw Response")
        results_layout = QVBoxLayout()
        self.horizons_results = QTextEdit()
        self.horizons_results.setReadOnly(True)
        self.horizons_results.setPlaceholderText("Query results will appear here (may take a few seconds)...")
        results_layout.addWidget(self.horizons_results)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        widget.setLayout(layout)
        return widget

    # Provider query handlers
    def on_openngc_query(self):
        """Query OpenNGC provider directly"""
        obj_id = self.openngc_id_input.text().strip()
        if not obj_id:
            self.openngc_results.setPlainText("Please enter an object ID.")
            return

        self.openngc_results.setPlainText(f"Querying OpenNGC for '{obj_id}'...\n")

        try:
            from pathlib import Path
            from app.catalog.providers.openngc_provider import OpenNGCProvider

            # Initialize provider
            csv_path = Path(__file__).parent.parent.parent.parent.parent.parent / "data" / "catalogs" / "NGC.csv"
            provider = OpenNGCProvider(csv_path)

            # Query
            result = provider.get_object(obj_id)

            if result is None:
                self.openngc_results.setPlainText(f"Object '{obj_id}' not found in OpenNGC.")
            else:
                self.openngc_results.setPlainText(self._format_object(result))

        except Exception as e:
            print(f"ERROR querying OpenNGC: {e}")
            traceback.print_exc()
            self.openngc_results.setPlainText(f"Error: {str(e)}\n\nCheck console for traceback.")

    def on_openngc_resolve(self):
        """Resolve name with OpenNGC provider"""
        obj_id = self.openngc_id_input.text().strip()
        if not obj_id:
            self.openngc_results.setPlainText("Please enter an object ID.")
            return

        self.openngc_results.setPlainText(f"Resolving name with OpenNGC: '{obj_id}'...\n")

        try:
            from pathlib import Path
            from app.catalog.providers.openngc_provider import OpenNGCProvider

            csv_path = Path(__file__).parent.parent.parent.parent.parent.parent / "data" / "catalogs" / "NGC.csv"
            provider = OpenNGCProvider(csv_path)

            result = provider.resolve_name(obj_id)

            if result is None:
                self.openngc_results.setPlainText(f"Name '{obj_id}' could not be resolved by OpenNGC.")
            else:
                self.openngc_results.setPlainText(f"Resolved to: {result}")

        except Exception as e:
            print(f"ERROR resolving with OpenNGC: {e}")
            traceback.print_exc()
            self.openngc_results.setPlainText(f"Error: {str(e)}\n\nCheck console for traceback.")

    def on_simbad_query(self):
        """Query SIMBAD provider directly"""
        obj_name = self.simbad_name_input.text().strip()
        if not obj_name:
            self.simbad_results.setPlainText("Please enter an object name.")
            return

        self.simbad_results.setPlainText(f"Querying SIMBAD for '{obj_name}'...\n(This may take a few seconds)")

        try:
            from app.catalog.providers.simbad_provider import SimbadProvider

            provider = SimbadProvider()
            result = provider.get_object(obj_name)

            if result is None:
                self.simbad_results.setPlainText(f"Object '{obj_name}' not found in SIMBAD.")
            else:
                self.simbad_results.setPlainText(self._format_object(result))

        except Exception as e:
            print(f"ERROR querying SIMBAD: {e}")
            traceback.print_exc()
            self.simbad_results.setPlainText(f"Error: {str(e)}\n\nCheck console for traceback.")

    def on_simbad_resolve(self):
        """Resolve name with SIMBAD provider"""
        obj_name = self.simbad_name_input.text().strip()
        if not obj_name:
            self.simbad_results.setPlainText("Please enter an object name.")
            return

        self.simbad_results.setPlainText(f"Resolving name with SIMBAD: '{obj_name}'...\n(This may take a few seconds)")

        try:
            from app.catalog.providers.simbad_provider import SimbadProvider

            provider = SimbadProvider()
            result = provider.resolve_name(obj_name)

            if result is None:
                self.simbad_results.setPlainText(f"Name '{obj_name}' could not be resolved by SIMBAD.")
            else:
                self.simbad_results.setPlainText(f"Resolved to: {result}")

        except Exception as e:
            print(f"ERROR resolving with SIMBAD: {e}")
            traceback.print_exc()
            self.simbad_results.setPlainText(f"Error: {str(e)}\n\nCheck console for traceback.")

    def on_horizons_query(self):
        """Query Horizons provider directly"""
        obj_name = self.horizons_name_input.text().strip()
        if not obj_name:
            self.horizons_results.setPlainText("Please enter an object name.")
            return

        self.horizons_results.setPlainText(f"Querying Horizons for '{obj_name}' from geocenter...\n(This may take a few seconds)")

        try:
            from app.catalog.providers.horizons_provider import HorizonsProvider
            from datetime import datetime, timezone

            # Use geocenter (default)
            provider = HorizonsProvider()

            # Use current time
            obs_time = datetime.now(timezone.utc)

            result = provider.get_object(obj_name, time=obs_time)

            if result is None:
                self.horizons_results.setPlainText(f"Object '{obj_name}' not found in Horizons or query failed.")
            else:
                self.horizons_results.setPlainText(self._format_object(result))

        except Exception as e:
            print(f"ERROR querying Horizons: {e}")
            traceback.print_exc()
            self.horizons_results.setPlainText(f"Error: {str(e)}\n\nCheck console for traceback.")
