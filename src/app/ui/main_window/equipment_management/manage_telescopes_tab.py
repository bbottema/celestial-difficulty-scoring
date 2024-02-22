import sys

from PySide6.QtWidgets import QPushButton, QTableWidget, QLabel, QDoubleSpinBox, QVBoxLayout, QComboBox

from app.domain.model.telescope_type import TelescopeType
from app.orm.entities import Telescope
from app.ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from app.utils.gui_helper import centered_table_widget_item, default_table


class ManageTelescopesTab(ManageEquipmentTab):
    COLUMN_NAME = 0
    COLUMN_OBSERVATION_SITE = 1
    COLUMN_TYPE = 2
    COLUMN_APERTURE = 3
    COLUMN_FOCAL_LENGTH = 4
    COLUMN_FOCAL_RATIO = 5
    COLUMN_BUTTONS = 6

    def __init__(self, telescope_service, observation_site_service):
        super().__init__('Telescope', observation_site_service)
        self.telescope_service = telescope_service

    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', 'Type', 'Aperture', 'Focal Length', 'Focal Ratio', 'Observation sites', ''])

    def populate_equipment_table(self, *args):
        self.equipment_table.setRowCount(0)
        data: [Telescope] = self.telescope_service.get_all()
        for i, telescope in enumerate(data):
            self.equipment_table.insertRow(i)
            self.equipment_table.setItem(i, self.COLUMN_NAME, centered_table_widget_item(telescope.name))
            self.equipment_table.setItem(i, self.COLUMN_TYPE, centered_table_widget_item(telescope.type))
            self.equipment_table.setItem(i, self.COLUMN_APERTURE, centered_table_widget_item(f'{telescope.aperture} mm'))
            self.equipment_table.setItem(i, self.COLUMN_FOCAL_LENGTH, centered_table_widget_item(f'{telescope.focal_length} mm'))
            self.equipment_table.setItem(i, self.COLUMN_FOCAL_RATIO, centered_table_widget_item(f'f/{telescope.focal_ratio}'))
            self.equipment_table.setItem(i, self.COLUMN_OBSERVATION_SITE, centered_table_widget_item(
                ', '.join([site.name for site in telescope.observation_sites])
            ))
            self.equipment_table.setCellWidget(i, self.COLUMN_BUTTONS, self._create_delete_button(telescope))

    def _create_delete_button(self, telescope):
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda *args, site_id=telescope.id: self.delete_telescope(site_id))
        return delete_button

    def define_equipment_form_controls(self, form_layout: QVBoxLayout):
        # we already get name and observation site from the abstract class, as well as the Save button
        # let's add the rest of the fields: type, aperture, focal length, focal ratio
        # NOTE: depending on which input is filled in by the user, focal length or focal ratio, the other one will be calculated on the fly
        self._add_equipment_type_input(form_layout)
        self._add_equipment_aperture_input(form_layout)
        self._add_equipment_focal_length_input(form_layout)
        self._add_equipment_focal_ratio_input(form_layout)

    def _add_equipment_focal_ratio_input(self, form_layout: QVBoxLayout):
        focal_ratio_label = QLabel("Focal Ratio:")
        self.focal_ratio_input = focal_ratio_input = QDoubleSpinBox()
        focal_ratio_input.setPrefix("f/")
        focal_ratio_input.setDecimals(1)
        focal_ratio_input.setMinimum(0)
        focal_ratio_input.setMaximum(sys.maxsize)
        focal_ratio_input.setSingleStep(1)
        focal_ratio_input.valueChanged.connect(lambda new_ratio_value: self._calculate_focal_length(new_ratio_value))
        form_layout.addWidget(focal_ratio_label)
        form_layout.addWidget(focal_ratio_input)
        pass

    def _add_equipment_focal_length_input(self, form_layout: QVBoxLayout):
        focal_length_label = QLabel("Focal Length:")
        self.focal_length_input = focal_length_input = QDoubleSpinBox()
        focal_length_input.setSuffix(" mm")
        focal_length_input.setMinimum(0)
        focal_length_input.setMaximum(sys.maxsize)
        focal_length_input.setDecimals(0)
        focal_length_input.setSingleStep(50)
        focal_length_input.valueChanged.connect(lambda new_focal_length_value: self._calculate_focal_ratio(new_focal_length_value))
        form_layout.addWidget(focal_length_label)
        form_layout.addWidget(focal_length_input)
        pass

    def _add_equipment_aperture_input(self, form_layout: QVBoxLayout):
        aperture_label = QLabel("Aperture:")
        self.aperture_input = aperture_input = QDoubleSpinBox()
        aperture_input.setSuffix(" mm")
        aperture_input.setMinimum(0)
        aperture_input.setMaximum(sys.maxsize)
        aperture_input.setDecimals(0)
        aperture_input.setSingleStep(10)
        aperture_input.valueChanged.connect(lambda new_aperture_value: self._calculate_focal_length_from_aperture(new_aperture_value))
        form_layout.addWidget(aperture_label)
        form_layout.addWidget(aperture_input)
        pass

    def _add_equipment_type_input(self, form_layout: QVBoxLayout):
        # dropdown using TelescopeType enum
        telescope_type_label = QLabel("Type:")
        telescope_type_combo = QComboBox()
        telescope_type_combo.addItems([telescope_type.name for telescope_type in TelescopeType])
        form_layout.addWidget(telescope_type_label)
        form_layout.addWidget(telescope_type_combo)
        pass

    def _calculate_focal_length(self, new_ratio_value: float):
        if not self.focal_length_input.hasFocus() and new_ratio_value != 0:
            self.focal_length_input.setValue(self.aperture_input.value() * new_ratio_value)

    def _calculate_focal_ratio(self, new_focal_length_value: float):
        if not self.focal_ratio_input.hasFocus() and new_focal_length_value != 0:
            self.focal_ratio_input.setValue(new_focal_length_value / self.aperture_input.value())

    def _calculate_focal_length_from_aperture(self, new_aperture_value: float):
        if not self.focal_length_input.hasFocus() and new_aperture_value != 0:
            self.focal_length_input.setValue(new_aperture_value * self.focal_ratio_input.value())
