from PySide6.QtWidgets import (QTableWidget, QVBoxLayout, QLabel, QSpinBox)

from app.orm.model.entities import Imager
from app.orm.services.imager_service import ImagerService
from app.orm.services.observation_site_service import ObservationSiteService
from app.ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from app.utils.gui_helper import default_table, centered_table_widget_item


class ManageImagersTab(ManageEquipmentTab):
    COLUMN_NAME = 0
    COLUMN_PIXEL_SIZE = 1
    COLUMN_NUMBER_OF_PIXELS = 2
    COLUMN_SENSOR_SIZE = 3
    COLUMN_OBSERVATION_SITE = 4
    COLUMN_BUTTONS = 5  # used for the delete button

    # form controls
    pixel_size_input_main: QSpinBox
    number_of_pixels_input_main: QSpinBox
    sensor_size_input_main: QSpinBox
    pixel_size_input_guide: QSpinBox
    number_of_pixels_input_guide: QSpinBox
    sensor_size_input_guide: QSpinBox

    def __init__(self, imager_service: ImagerService, observation_site_service: ObservationSiteService):
        super().__init__(Imager, imager_service, observation_site_service, imager_service.mutation_events)

    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', 'Main Sensor', 'Guide Sensor', 'Observation sites', ''])

    def populate_equipment_table(self, equipment_table: QTableWidget) -> None:
        equipment_table.setRowCount(0)
        imagers: list[Imager] = self.equipment_service.get_all()
        for i, imager in enumerate(imagers):
            equipment_table.insertRow(i)
            equipment_table.setItem(i, self.COLUMN_NAME, centered_table_widget_item(imager.name, imager))
            main_sensor_info = f"{imager.main_pixel_size} μm, {imager.main_number_of_pixels} px, {imager.main_sensor_size} mm"
            equipment_table.setItem(i, self.COLUMN_PIXEL_SIZE, centered_table_widget_item(main_sensor_info, imager))
            guide_sensor_info = f"{imager.guide_pixel_size} μm, {imager.guide_number_of_pixels} px, {imager.guide_sensor_size} mm"
            equipment_table.setItem(i, self.COLUMN_NUMBER_OF_PIXELS, centered_table_widget_item(guide_sensor_info, imager))
            equipment_table.setItem(i, self.COLUMN_OBSERVATION_SITE, centered_table_widget_item(
                ', '.join([site.name for site in imager.observation_sites]), imager
            ))
            equipment_table.setCellWidget(i, self.COLUMN_BUTTONS, self._create_delete_button(imager))

        equipment_table.resizeRowsToContents()
        super()._reselect_current_active_equipment(equipment_table)

    def define_equipment_form_controls(self, form_layout: QVBoxLayout) -> None:
        # Add controls for Main Sensor
        form_layout.addWidget(QLabel("Main Sensor Pixel Size (μm):"))
        self.pixel_size_input_main = QSpinBox()
        self.pixel_size_input_main.setSuffix(" μm")
        self.pixel_size_input_main.setMinimum(1)
        self.pixel_size_input_main.setMaximum(50)  # Max pixel size might need to be adjusted
        form_layout.addWidget(self.pixel_size_input_main)

        form_layout.addWidget(QLabel("Main Sensor Number of Pixels:"))
        self.number_of_pixels_input_main = QSpinBox()
        self.number_of_pixels_input_main.setRange(1, 10000)  # Adjust max range as necessary
        form_layout.addWidget(self.number_of_pixels_input_main)

        form_layout.addWidget(QLabel("Main Sensor Size (mm):"))
        self.sensor_size_input_main = QSpinBox()
        self.sensor_size_input_main.setSuffix(" mm")
        self.sensor_size_input_main.setRange(1, 100)  # Adjust max range as necessary
        form_layout.addWidget(self.sensor_size_input_main)
        # Divider Label
        form_layout.addWidget(QLabel("Guide Sensor (if applicable)"))

        # Add controls for Guide Sensor
        form_layout.addWidget(QLabel("Guide Sensor Pixel Size (μm):"))
        self.pixel_size_input_guide = QSpinBox()
        self.pixel_size_input_guide.setSuffix(" μm")
        self.pixel_size_input_guide.setMinimum(1)
        self.pixel_size_input_guide.setMaximum(50)  # Max pixel size might need to be adjusted
        form_layout.addWidget(self.pixel_size_input_guide)

        form_layout.addWidget(QLabel("Guide Sensor Number of Pixels:"))
        self.number_of_pixels_input_guide = QSpinBox()
        self.number_of_pixels_input_guide.setRange(1, 10000)  # Adjust max range as necessary
        form_layout.addWidget(self.number_of_pixels_input_guide)

        form_layout.addWidget(QLabel("Guide Sensor Size (mm):"))
        self.sensor_size_input_guide = QSpinBox()
        self.sensor_size_input_guide.setSuffix(" mm")
        self.sensor_size_input_guide.setRange(1, 100)  # Adjust max range as necessary
        form_layout.addWidget(self.sensor_size_input_guide)

    def clear_form_to_defaults(self) -> None:
        self.pixel_size_input_main.setValue(1)
        self.number_of_pixels_input_main.setValue(1)
        self.sensor_size_input_main.setValue(1)
        self.pixel_size_input_guide.setValue(1)
        self.number_of_pixels_input_guide.setValue(1)
        self.sensor_size_input_guide.setValue(1)

    def populate_form_for_selected_equipment(self, imager: Imager) -> None:
        # Populate the form with values from the selected imager
        self.pixel_size_input_main.setValue(imager.main_pixel_size)
        self.number_of_pixels_input_main.setValue(imager.main_number_of_pixels)
        self.sensor_size_input_main.setValue(imager.main_sensor_size)
        self.pixel_size_input_guide.setValue(imager.guide_pixel_size)
        self.number_of_pixels_input_guide.setValue(imager.guide_number_of_pixels)
        self.sensor_size_input_guide.setValue(imager.guide_sensor_size)

    def create_or_update_equipment_entity(self, equipment_id: int | None, name: str, site_names: list[str]) -> Imager:
        return Imager(
            id=equipment_id,
            name=name,
            main_pixel_size=self.pixel_size_input_main.value(),
            main_number_of_pixels=self.number_of_pixels_input_main.value(),
            main_sensor_size=self.sensor_size_input_main.value(),
            guide_pixel_size=self.pixel_size_input_guide.value(),
            guide_number_of_pixels=self.number_of_pixels_input_guide.value(),
            guide_sensor_size=self.sensor_size_input_guide.value(),
            observation_sites=self.observation_site_service.get_for_names(site_names)
        )
