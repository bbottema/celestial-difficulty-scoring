from PySide6.QtWidgets import QTableWidget, QVBoxLayout, QPushButton, QTableWidgetItem, QSpinBox, QLabel

from app.orm.model.entities import Filter
from app.orm.model.wavelength_type import Wavelength
from app.orm.services.filter_service import FilterService
from app.orm.services.observation_site_service import ObservationSiteService
from app.ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from app.utils.gui_helper import default_table, centered_table_widget_item, remove_table_row_by_contained_widget


class ManageFiltersTab(ManageEquipmentTab):
    COLUMN_NAME = 0
    COLUMN_MINIMUM_EXIT_PUPIL = 1
    COLUMN_BANDPASS_WAVELENGTH = 2
    COLUMN_OBSERVATION_SITE = 3
    COLUMN_BUTTONS = 4

    # form controls
    wavelength_table: QTableWidget
    minimum_exit_pupil_input: QSpinBox
    add_wavelength_button: QPushButton

    def __init__(self, filter_service: FilterService, observation_site_service: ObservationSiteService):
        super().__init__(Filter, filter_service, observation_site_service, filter_service.mutation_events)

    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', 'Min. Exit Pupil', 'wavelengths', 'Observation sites', ''])

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

    # noinspection PyAttributeOutsideInit
    def define_equipment_form_controls(self, form_layout: QVBoxLayout):
        min_exit_pupil_label = QLabel("Minimum Exit Pupil:")
        form_layout.addWidget(min_exit_pupil_label)

        self.minimum_exit_pupil_input = QSpinBox()
        self.minimum_exit_pupil_input.setSuffix(" mm")
        self.minimum_exit_pupil_input.setMinimum(1)
        self.minimum_exit_pupil_input.setMaximum(100)
        self.minimum_exit_pupil_input.setSingleStep(1)
        form_layout.addWidget(self.minimum_exit_pupil_input)

        form_layout.addWidget(QLabel("Bandpass wavelengths:"))
        self.wavelength_table = default_table(['From', 'To', ''])
        form_layout.addWidget(self.wavelength_table)

        self.add_wavelength_button = QPushButton('+')
        self.add_wavelength_button.clicked.connect(self.add_wavelength_entry_row)
        form_layout.addWidget(self.add_wavelength_button)

    def add_wavelength_entry_row(self) -> None:
        def create_delete_row_button():
            delete_button = QPushButton("-")
            delete_button.clicked.connect(lambda: remove_table_row_by_contained_widget(self.wavelength_table, delete_button))
            return delete_button

        row_position = self.wavelength_table.rowCount()
        self.wavelength_table.insertRow(row_position)
        self.wavelength_table.setItem(row_position, 0, QTableWidgetItem("0"))
        self.wavelength_table.setItem(row_position, 1, QTableWidgetItem("0"))
        self.wavelength_table.setCellWidget(row_position, 2, create_delete_row_button())

    def clear_form_to_defaults(self) -> None:
        self.minimum_exit_pupil_input.setValue(1)
        self.wavelength_table.setRowCount(0)

    def populate_form_for_selected_equipment(self, filter: Filter) -> None:
        self.minimum_exit_pupil_input.setValue(filter.minimum_exit_pupil if filter.minimum_exit_pupil else 1)

    def create_or_update_equipment_entity(self, equipment_id: int | None, name: str, site_names: list[str]) -> Filter:
        return Filter(
            id=equipment_id,
            name=name,
            minimum_exit_pupil=self.minimum_exit_pupil_input.value(),
            wavelengths=[Wavelength(
                from_wavelength=int(self.wavelength_table.item(row, 0).text()),
                to_wavelength=int(self.wavelength_table.item(row, 1).text())
            ) for row in range(self.wavelength_table.rowCount())],
            observation_sites=self.observation_site_service.get_for_names(site_names)
        )
