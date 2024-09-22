from PySide6.QtWidgets import QTableWidget, QVBoxLayout, QLabel, QDoubleSpinBox
from overrides import overrides

from app.orm.model.entities import OpticalAid
from app.orm.services.optical_aid_service import OpticalAidService
from app.orm.services.observation_site_service import ObservationSiteService
from app.ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from app.utils.assume import verify_not_none
from app.utils.gui_helper import default_table, centered_table_widget_item
from app.utils.input_value_helper import parse_str_float


class ManageOpticalAidsTab(ManageEquipmentTab):
    COLUMN_NAME = 0
    COLUMN_MAGNIFICATION = 1
    COLUMN_OBSERVATION_SITE = 2
    COLUMN_BUTTONS = 3

    # form controls
    magnification_input: QDoubleSpinBox

    def __init__(self, optical_aid_service: OpticalAidService, observation_site_service: ObservationSiteService):
        super().__init__(OpticalAid, optical_aid_service, observation_site_service, optical_aid_service.mutation_events)

    @overrides
    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', 'Magnification', 'Observation sites', ''])

    @overrides
    def populate_equipment_table(self, equipment_table: QTableWidget) -> None:
        data: list[OpticalAid] = self.equipment_service.get_all()
        for i, optical_aid in enumerate(data):
            equipment_table.insertRow(i)
            equipment_table.setItem(i, self.COLUMN_NAME, centered_table_widget_item(optical_aid.name, optical_aid))
            equipment_table.setItem(i, self.COLUMN_MAGNIFICATION, centered_table_widget_item(f'{optical_aid.magnification}x', optical_aid))
            equipment_table.setItem(i, self.COLUMN_OBSERVATION_SITE, centered_table_widget_item(
                ', '.join([site.name for site in optical_aid.observation_sites]), optical_aid
            ))
            equipment_table.setCellWidget(i, self.COLUMN_BUTTONS, self._create_delete_button(optical_aid))

    @overrides
    def define_equipment_form_controls(self, form_layout: QVBoxLayout) -> None:
        # Magnification Input
        magnification_label = QLabel("Magnification:")
        self.magnification_input = QDoubleSpinBox()
        self.magnification_input.setSuffix("x")
        self.magnification_input.setMinimum(0.1)
        self.magnification_input.setMaximum(5.0)
        self.magnification_input.setSingleStep(0.1)
        form_layout.addWidget(magnification_label)
        form_layout.addWidget(self.magnification_input)

    @overrides
    def clear_form_to_defaults(self) -> None:
        self.magnification_input.setValue(1.0)

    @overrides
    def populate_form_for_selected_equipment(self, selected_equipment: OpticalAid) -> None:
        self.magnification_input.setValue(selected_equipment.magnification)

    @overrides
    def create_or_update_equipment_entity(self, equipment_id: int | None, name: str, site_names: list[str]) -> OpticalAid:
        return OpticalAid(
            id=equipment_id,
            name=name,
            magnification=verify_not_none(parse_str_float(self.magnification_input.cleanText()), "Magnification"),
            observation_sites=self.observation_site_service.get_for_names(site_names)
        )
