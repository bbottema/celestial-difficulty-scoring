from PySide6.QtWidgets import QTableWidget, QVBoxLayout, QPushButton, QTableWidgetItem

from app.orm.model.entities import Filter
from app.orm.services.filter_service import FilterService
from app.orm.services.observation_site_service import ObservationSiteService
from app.ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from app.utils.gui_helper import default_table, centered_table_widget_item


class ManageFiltersTab(ManageEquipmentTab):
    COLUMN_NAME = 0
    COLUMN_MINIMUM_EXIT_PUPIL = 1
    COLUMN_BANDPASS_WAVELENGTH = 2
    COLUMN_OBSERVATION_SITE = 3
    COLUMN_BUTTONS = 4

    # form controls
    wavelength_table: QTableWidget
    add_wavelength_button: QPushButton

    # telescope_type_combo: QComboBox
    # aperture_input: QSpinBox
    # focal_length_input: QSpinBox
    # focal_ratio_input: QDoubleSpinBox

    def __init__(self, filter_service: FilterService, observation_site_service: ObservationSiteService):
        super().__init__(Filter, filter_service, observation_site_service, filter_service.mutation_events)

    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', 'wavelengths', 'Observation sites', ''])

    def populate_equipment_table(self, equipment_table: QTableWidget) -> None:
        equipment_table.setRowCount(0)
        data: list[Filter] = self.equipment_service.get_all()
        for i, filter in enumerate(data):
            equipment_table.insertRow(i)
            equipment_table.setItem(i, self.COLUMN_NAME, centered_table_widget_item(filter.name, filter))
            equipment_table.setItem(i, self.COLUMN_MINIMUM_EXIT_PUPIL, centered_table_widget_item(f'{filter.minimum_exit_pupil} mm', filter))
            equipment_table.setItem(i, self.COLUMN_BANDPASS_WAVELENGTH, centered_table_widget_item(
                ', '.join([f'{wavelength.from_wavelength}-{wavelength.to_wavelength}' for wavelength in filter.wavelengths]), filter
            ))
            equipment_table.setItem(i, self.COLUMN_OBSERVATION_SITE, centered_table_widget_item(
                ', '.join([site.name for site in filter.observation_sites]), filter
            ))
            equipment_table.setCellWidget(i, self.COLUMN_BUTTONS, self._create_delete_button(filter))

        equipment_table.resizeRowsToContents()
        super()._reselect_current_active_equipment(equipment_table)

    def define_equipment_form_controls(self, form_layout: QVBoxLayout):
        self.wavelength_table = default_table(['From', 'To'])
        form_layout.addWidget(self.wavelength_table)

        self.add_wavelength_button = QPushButton('+')
        self.add_wavelength_button.clicked.connect(self.add_wavelength_entry_row)
        form_layout.addWidget(self.add_wavelength_button)

    def add_wavelength_entry_row(self):
        row_position = self.wavelength_table.rowCount()
        self.wavelength_table.insertRow(row_position)
        self.wavelength_table.setItem(row_position, 0, QTableWidgetItem("0"))
        self.wavelength_table.setItem(row_position, 1, QTableWidgetItem("0"))
        pass
