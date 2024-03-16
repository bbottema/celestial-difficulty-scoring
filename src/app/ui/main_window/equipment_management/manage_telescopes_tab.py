from PySide6.QtWidgets import QTableWidget, QLabel, QDoubleSpinBox, QVBoxLayout, QComboBox, QSpinBox

from app.domain.model.telescope_type import TelescopeType
from app.orm.model.entities import Telescope
from app.orm.services.observation_site_service import ObservationSiteService
from app.orm.services.telescope_service import TelescopeService
from app.ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from app.utils.assume import verify_not_none
from app.utils.gui_helper import centered_table_widget_item, default_table
from app.utils.input_value_helper import parse_str_float, parse_str_int
from app.utils.telescope_calculator import calculate_focal_length, calculate_focal_ratio, calculate_focal_length_from_aperture

MAX_SPINNER_VALUE = 2147483647  # Maximum for a 32-bit signed integer, the max for int-based spinners


class ManageTelescopesTab(ManageEquipmentTab[Telescope]):
    COLUMN_NAME = 0
    COLUMN_TYPE = 1
    COLUMN_APERTURE = 2
    COLUMN_FOCAL_LENGTH = 3
    COLUMN_FOCAL_RATIO = 4
    COLUMN_OBSERVATION_SITE = 5
    COLUMN_BUTTONS = 6

    # form controls
    telescope_type_combo: QComboBox
    aperture_input: QSpinBox
    focal_length_input: QSpinBox
    focal_ratio_input: QDoubleSpinBox

    def __init__(self, telescope_service: TelescopeService, observation_site_service: ObservationSiteService):
        super().__init__(Telescope, telescope_service, observation_site_service, telescope_service.mutation_events)

    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', 'Type', 'Aperture', 'Focal Length', 'Focal Ratio', 'Observation sites', ''])

    def populate_equipment_table(self, equipment_table: QTableWidget) -> None:
        data: list[Telescope] = self.equipment_service.get_all()
        for i, telescope in enumerate(data):
            equipment_table.insertRow(i)
            equipment_table.setItem(i, self.COLUMN_NAME, centered_table_widget_item(telescope.name, telescope))
            equipment_table.setItem(i, self.COLUMN_TYPE, centered_table_widget_item(telescope.type.label, telescope))
            equipment_table.setItem(i, self.COLUMN_APERTURE, centered_table_widget_item(f'{telescope.aperture} mm', telescope))
            equipment_table.setItem(i, self.COLUMN_FOCAL_LENGTH, centered_table_widget_item(f'{telescope.focal_length} mm', telescope))
            equipment_table.setItem(i, self.COLUMN_FOCAL_RATIO, centered_table_widget_item(f'f/{telescope.focal_ratio}', telescope))
            equipment_table.setItem(i, self.COLUMN_OBSERVATION_SITE, centered_table_widget_item(
                ', '.join([site.name for site in telescope.observation_sites]), telescope
            ))
            equipment_table.setCellWidget(i, self.COLUMN_BUTTONS, self._create_delete_button(telescope))

    def define_equipment_form_controls(self, form_layout: QVBoxLayout):
        self._add_equipment_type_input(form_layout)
        self._add_equipment_aperture_input(form_layout)
        self._add_equipment_focal_length_input(form_layout)
        self._add_equipment_focal_ratio_input(form_layout)

    def _add_equipment_type_input(self, form_layout: QVBoxLayout):
        telescope_type_label = QLabel("Type:")
        self.telescope_type_combo = QComboBox()
        for tt in TelescopeType:
            self.telescope_type_combo.addItem(tt.label, tt.name)
        form_layout.addWidget(telescope_type_label)
        form_layout.addWidget(self.telescope_type_combo)
        pass

    def _add_equipment_aperture_input(self, form_layout: QVBoxLayout):
        aperture_label = QLabel("Aperture:")
        self.aperture_input = aperture_input = QSpinBox()
        aperture_input.setSuffix(" mm")
        aperture_input.setMinimum(0)
        aperture_input.setMaximum(MAX_SPINNER_VALUE)
        aperture_input.setSingleStep(10)
        aperture_input.valueChanged.connect(lambda new_aperture_value: calculate_focal_length_from_aperture_input(new_aperture_value))
        form_layout.addWidget(aperture_label)
        form_layout.addWidget(aperture_input)

        def calculate_focal_length_from_aperture_input(new_aperture_value: int):
            if not self.focal_length_input.hasFocus():
                self.focal_length_input.setValue(calculate_focal_length_from_aperture(new_aperture_value, self.focal_ratio_input.value()))

    def _add_equipment_focal_length_input(self, form_layout: QVBoxLayout):
        focal_length_label = QLabel("Focal Length:")
        self.focal_length_input = focal_length_input = QSpinBox()
        focal_length_input.setSuffix(" mm")
        focal_length_input.setMinimum(0)
        focal_length_input.setMaximum(MAX_SPINNER_VALUE)
        focal_length_input.setSingleStep(50)
        focal_length_input.valueChanged.connect(lambda new_focal_length_value: calculate_focal_ratio_from_focal_length_input(new_focal_length_value))
        form_layout.addWidget(focal_length_label)
        form_layout.addWidget(focal_length_input)

        def calculate_focal_ratio_from_focal_length_input(new_focal_length_value: int):
            if not self.focal_ratio_input.hasFocus():
                self.focal_ratio_input.setValue(calculate_focal_ratio(self.aperture_input.value(), new_focal_length_value))

    def _add_equipment_focal_ratio_input(self, form_layout: QVBoxLayout):
        focal_ratio_label = QLabel("Focal Ratio:")
        self.focal_ratio_input = focal_ratio_input = QDoubleSpinBox()
        focal_ratio_input.setPrefix("f/")
        focal_ratio_input.setDecimals(1)
        focal_ratio_input.setMinimum(0)
        focal_ratio_input.setMaximum(MAX_SPINNER_VALUE)
        focal_ratio_input.setSingleStep(1)

        focal_ratio_input.valueChanged.connect(lambda new_ratio_value: calculate_focal_length_from_ratio_input(new_ratio_value))
        form_layout.addWidget(focal_ratio_label)
        form_layout.addWidget(focal_ratio_input)

        def calculate_focal_length_from_ratio_input(new_ratio_value: float):
            if not self.focal_length_input.hasFocus():
                self.focal_length_input.setValue(calculate_focal_length(self.aperture_input.value(), new_ratio_value))

    def clear_form_to_defaults(self):
        self.telescope_type_combo.setCurrentText(TelescopeType.ACHROMATIC_REFRACTOR.label)
        self.aperture_input.setValue(80)
        self.focal_length_input.setValue(900)
        self.focal_ratio_input.setValue(11.3)

    def populate_form_for_selected_equipment(self, telescope: Telescope) -> None:
        self.telescope_type_combo.setCurrentText(telescope.type.label)
        self.aperture_input.setValue(telescope.aperture)
        self.focal_length_input.setValue(telescope.focal_length)
        self.focal_ratio_input.setValue(telescope.focal_ratio)

    def create_or_update_equipment_entity(self, equipment_id: int | None, name: str, site_names: list[str]) -> Telescope:
        return Telescope(
            id=equipment_id,
            name=name,
            type=(TelescopeType[self.telescope_type_combo.currentData()]),
            aperture=(verify_not_none(parse_str_int(self.aperture_input.cleanText()), "Aperture")),
            focal_length=verify_not_none(parse_str_int(self.focal_length_input.cleanText()), "Focal length"),
            focal_ratio=verify_not_none(parse_str_float(self.focal_ratio_input.cleanText()), "Focal ratio"),
            observation_sites=self.observation_site_service.get_for_names(site_names)
        )
