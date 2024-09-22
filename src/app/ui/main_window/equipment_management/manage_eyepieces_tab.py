from PySide6.QtWidgets import QTableWidget, QVBoxLayout, QLabel, QSpinBox, QDoubleSpinBox
from overrides import overrides

from app.orm.model.entities import Eyepiece
from app.orm.services.eyepiece_service import EyepieceService
from app.orm.services.observation_site_service import ObservationSiteService
from app.ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from app.utils.assume import verify_not_none
from app.utils.gui_helper import default_table, centered_table_widget_item
from app.utils.input_value_helper import parse_str_int, parse_str_float


class ManageEyepiecesTab(ManageEquipmentTab):
    COLUMN_NAME = 0
    COLUMN_FOCAL_LENGTH = 1
    COLUMN_BARREL_SIZE = 2
    COLUMN_APPARENT_FOV = 3
    COLUMN_OBSERVATION_SITE = 4
    COLUMN_BUTTONS = 5

    # form controls
    focal_length_input: QSpinBox
    barrel_size_input: QDoubleSpinBox
    apparent_fov_input: QSpinBox

    def __init__(self, eyepiece_service: EyepieceService, observation_site_service: ObservationSiteService):
        super().__init__(Eyepiece, eyepiece_service, observation_site_service, eyepiece_service.mutation_events)

    @overrides
    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', 'Focal Length', 'Barrel Size', 'Apparent FOV', 'Observation sites', ''])

    @overrides
    def populate_equipment_table(self, equipment_table: QTableWidget) -> None:
        data: list[Eyepiece] = self.equipment_service.get_all()
        for i, eyepiece in enumerate(data):
            equipment_table.insertRow(i)
            equipment_table.setItem(i, self.COLUMN_NAME, centered_table_widget_item(eyepiece.name, eyepiece))
            equipment_table.setItem(i, self.COLUMN_FOCAL_LENGTH, centered_table_widget_item(f'{eyepiece.focal_length} mm', eyepiece))
            equipment_table.setItem(i, self.COLUMN_BARREL_SIZE, centered_table_widget_item(f'{eyepiece.barrel_size}"', eyepiece))
            equipment_table.setItem(i, self.COLUMN_APPARENT_FOV, centered_table_widget_item(f'{eyepiece.apparent_field_of_view}°', eyepiece))
            equipment_table.setItem(i, self.COLUMN_OBSERVATION_SITE, centered_table_widget_item(
                ', '.join([site.name for site in eyepiece.observation_sites]), eyepiece
            ))
            equipment_table.setCellWidget(i, self.COLUMN_BUTTONS, self._create_delete_button(eyepiece))

    @overrides
    def define_equipment_form_controls(self, form_layout: QVBoxLayout) -> None:
        # Focal Length Input
        focal_length_label = QLabel("Focal Length:")
        self.focal_length_input = QSpinBox()
        self.focal_length_input.setSuffix(" mm")
        self.focal_length_input.setMinimum(1)
        self.focal_length_input.setMaximum(100)
        self.focal_length_input.setSingleStep(1)
        form_layout.addWidget(focal_length_label)
        form_layout.addWidget(self.focal_length_input)

        # Barrel Size Input
        barrel_size_label = QLabel("Barrel Size:")
        self.barrel_size_input = QDoubleSpinBox()
        self.barrel_size_input.setSuffix('"')
        self.barrel_size_input.setMinimum(0.965)
        self.barrel_size_input.setMaximum(3.0)
        self.barrel_size_input.setSingleStep(0.01)
        form_layout.addWidget(barrel_size_label)
        form_layout.addWidget(self.barrel_size_input)

        # Apparent Field of View Input
        apparent_fov_label = QLabel("Apparent Field of View:")
        self.apparent_fov_input = QSpinBox()
        self.apparent_fov_input.setSuffix("°")
        self.apparent_fov_input.setMinimum(30)
        self.apparent_fov_input.setMaximum(120)
        self.apparent_fov_input.setSingleStep(1)
        form_layout.addWidget(apparent_fov_label)
        form_layout.addWidget(self.apparent_fov_input)

    @overrides
    def clear_form_to_defaults(self) -> None:
        self.focal_length_input.setValue(20)
        self.barrel_size_input.setValue(1.25)
        self.apparent_fov_input.setValue(50)

    @overrides
    def populate_form_for_selected_equipment(self, selected_equipment: Eyepiece) -> None:
        self.focal_length_input.setValue(selected_equipment.focal_length)
        self.barrel_size_input.setValue(selected_equipment.barrel_size)
        self.apparent_fov_input.setValue(selected_equipment.apparent_field_of_view)

    @overrides
    def create_or_update_equipment_entity(self, equipment_id: int | None, name: str, site_names: list[str]) -> Eyepiece:
        return Eyepiece(
            id=equipment_id,
            name=name,
            focal_length=verify_not_none(parse_str_int(self.focal_length_input.cleanText()), "Focal Length"),
            barrel_size=verify_not_none(parse_str_float(self.barrel_size_input.cleanText()), "Barrel Size"),
            apparent_field_of_view=verify_not_none(parse_str_int(self.apparent_fov_input.cleanText()), "Apparent Field of View"),
            observation_sites=self.observation_site_service.get_for_names(site_names)
        )
