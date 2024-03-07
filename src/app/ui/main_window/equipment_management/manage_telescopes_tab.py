from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QTableWidget, QLabel, QDoubleSpinBox, QVBoxLayout, QComboBox, QSpinBox

from app.domain.model.telescope_type import TelescopeType
from app.orm.entities import Telescope
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
        self.telescope_service = telescope_service  # is used in the super().__init__ call
        super().__init__(Telescope, observation_site_service)

    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', 'Type', 'Aperture', 'Focal Length', 'Focal Ratio', 'Observation sites', ''])

    def populate_equipment_table(self, equipment_table: QTableWidget) -> None:
        equipment_table.setRowCount(0)
        data: list[Telescope] = self.telescope_service.get_all()
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

    def _create_delete_button(self, telescope):
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda *args, telescope_id=telescope.id: self.telescope_service.delete_by_id(telescope_id))
        return delete_button

    def define_equipment_form_controls(self, form_layout: QVBoxLayout):
        self._add_equipment_type_input(form_layout)
        self._add_equipment_aperture_input(form_layout)
        self._add_equipment_focal_length_input(form_layout)
        self._add_equipment_focal_ratio_input(form_layout)

        self.clear_form_to_defaults()

    def _add_equipment_aperture_input(self, form_layout: QVBoxLayout):
        aperture_label = QLabel("Aperture:")
        self.aperture_input = aperture_input = QSpinBox()
        aperture_input.setSuffix(" mm")
        aperture_input.setMinimum(0)
        aperture_input.setMaximum(MAX_SPINNER_VALUE)
        aperture_input.setSingleStep(10)
        aperture_input.valueChanged.connect(lambda new_aperture_value: self._calculate_focal_length_from_aperture(new_aperture_value))
        form_layout.addWidget(aperture_label)
        form_layout.addWidget(aperture_input)
        pass

    def _add_equipment_focal_length_input(self, form_layout: QVBoxLayout):
        focal_length_label = QLabel("Focal Length:")
        self.focal_length_input = focal_length_input = QSpinBox()
        focal_length_input.setSuffix(" mm")
        focal_length_input.setMinimum(0)
        focal_length_input.setMaximum(MAX_SPINNER_VALUE)
        focal_length_input.setSingleStep(50)
        focal_length_input.valueChanged.connect(lambda new_focal_length_value: self._calculate_focal_ratio(new_focal_length_value))
        form_layout.addWidget(focal_length_label)
        form_layout.addWidget(focal_length_input)
        pass

    def _add_equipment_focal_ratio_input(self, form_layout: QVBoxLayout):
        focal_ratio_label = QLabel("Focal Ratio:")
        self.focal_ratio_input = focal_ratio_input = QDoubleSpinBox()
        focal_ratio_input.setPrefix("f/")
        focal_ratio_input.setDecimals(1)
        focal_ratio_input.setMinimum(0)
        focal_ratio_input.setMaximum(MAX_SPINNER_VALUE)
        focal_ratio_input.setSingleStep(1)
        focal_ratio_input.valueChanged.connect(lambda new_ratio_value: self._calculate_focal_length(new_ratio_value))
        form_layout.addWidget(focal_ratio_label)
        form_layout.addWidget(focal_ratio_input)
        pass

    def _add_equipment_type_input(self, form_layout: QVBoxLayout):
        telescope_type_label = QLabel("Type:")
        self.telescope_type_combo = QComboBox()
        for tt in TelescopeType:
            self.telescope_type_combo.addItem(tt.label, tt.name)
        form_layout.addWidget(telescope_type_label)
        form_layout.addWidget(self.telescope_type_combo)
        pass

    def _calculate_focal_length(self, new_ratio_value: float):
        if not self.focal_length_input.hasFocus():
            self.focal_length_input.setValue(calculate_focal_length(self.aperture_input.value(), new_ratio_value))

    def _calculate_focal_ratio(self, new_focal_length_value: int):
        if not self.focal_ratio_input.hasFocus():
            self.focal_ratio_input.setValue(calculate_focal_ratio(self.aperture_input.value(), new_focal_length_value))

    def _calculate_focal_length_from_aperture(self, new_aperture_value: int):
        if not self.focal_length_input.hasFocus():
            self.focal_length_input.setValue(calculate_focal_length_from_aperture(new_aperture_value, self.focal_ratio_input.value()))

    def handle_new_equipment_button_click(self) -> None:
        super().handle_new_equipment_button_click()
        self.clear_form_to_defaults()

    def clear_form_to_defaults(self):
        self.name_edit.clear()
        self.telescope_type_combo.setCurrentText(TelescopeType.ACHROMATIC_REFRACTOR.label)
        self.aperture_input.setValue(80)
        self.focal_length_input.setValue(900)
        self.focal_ratio_input.setValue(11.3)

    def handle_save_equipment_button_click(self) -> None:
        site_names = self._get_selected_observation_sites_names()
        telescope = Telescope(
            id=self.selected_equipment.id if self.selected_equipment else None,
            name=self.name_edit.text(),
            type=(TelescopeType[self.telescope_type_combo.currentData()]),
            aperture=(verify_not_none(parse_str_int(self.aperture_input.cleanText()), "Aperture")),
            focal_length=verify_not_none(parse_str_int(self.focal_length_input.cleanText()), "Focal length"),
            focal_ratio=verify_not_none(parse_str_float(self.focal_ratio_input.cleanText()), "Focal ratio"),
            observation_sites=self.observation_site_service.get_for_names(site_names)
        )

        if telescope.id:
            self.telescope_service.update(telescope)
        else:
            self.telescope_service.add(telescope)

    def _get_selected_observation_sites_names(self) -> list[str]:
        osl_widget = self.observation_site_list_widget
        return [osl_widget.item(i).text() for i in range(osl_widget.count())
                if osl_widget.item(i).checkState() == Qt.CheckState.Checked]

    def handle_select_equipment(self, telescope: Telescope):
        self.name_edit.setText(telescope.name)
        self.telescope_type_combo.setCurrentText(telescope.type.label)
        self.aperture_input.setValue(telescope.aperture)
        self.focal_length_input.setValue(telescope.focal_length)
        self.focal_ratio_input.setValue(telescope.focal_ratio)
