from PySide6.QtWidgets import (QTableWidget, QVBoxLayout, QLabel, QSpinBox, QCheckBox, QHBoxLayout)
from overrides import overrides

from app.orm.model.entities import Imager
from app.orm.services.imager_service import ImagerService
from app.orm.services.observation_site_service import ObservationSiteService
from app.ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab
from app.utils.assume import verify_not_none
from app.utils.gui_helper import default_table, centered_table_widget_item, add_to_layout_aligned_right, add_qspinbox_with_suffix_to_layout
from app.utils.imager_calculator import calculate_sensor_size
from app.utils.input_value_helper import parse_str_int


class ManageImagersTab(ManageEquipmentTab):
    COLUMN_NAME = 0
    COLUMN_MAIN_SENSOR = 1
    COLUMN_GUIDE_SENSOR = 2
    COLUMN_OBSERVATION_SITE = 3
    COLUMN_BUTTONS = 4

    # form controls
    pixel_size_input_main_w: QSpinBox
    pixel_size_input_main_h: QSpinBox
    number_of_pixels_input_main_w: QSpinBox
    number_of_pixels_input_main_h: QSpinBox
    main_sensor_size_label: QLabel

    guide_sensor_size_label: QLabel
    guide_sensor_checkbox: QCheckBox
    pixel_size_input_guide_w: QSpinBox
    pixel_size_input_guide_h: QSpinBox
    guide_sensor_pixel_number_label: QLabel
    number_of_pixels_input_guide_w: QSpinBox
    number_of_pixels_input_guide_h: QSpinBox
    guide_sensor_pixel_size_label: QLabel

    def __init__(self, imager_service: ImagerService, observation_site_service: ObservationSiteService):
        super().__init__(Imager, imager_service, observation_site_service, imager_service.mutation_events)

    @overrides
    def create_equipment_table(self) -> QTableWidget:
        return default_table(['Name', 'Main Sensor', 'Guide Sensor', 'Observation sites', ''])

    @overrides
    def populate_equipment_table(self, equipment_table: QTableWidget) -> None:
        imagers: list[Imager] = self.equipment_service.get_all()
        for i, imager in enumerate(imagers):
            equipment_table.insertRow(i)
            equipment_table.setItem(i, self.COLUMN_NAME, centered_table_widget_item(imager.name, imager))
            main_sensor_info = (f"{imager.main_pixel_size_width} x {imager.main_pixel_size_height} μm,"
                                f" {imager.main_number_of_pixels_width} x {imager.main_number_of_pixels_height} px,"
                                f" {imager.main_sensor_size_width_mm()} x {imager.main_sensor_size_height_mm()} mm")
            equipment_table.setItem(i, self.COLUMN_MAIN_SENSOR, centered_table_widget_item(main_sensor_info, imager))
            guide_sensor_info = (f"{imager.guide_pixel_size_width} x {imager.guide_pixel_size_height} μm,"
                                 f" {imager.guide_number_of_pixels_width} x {imager.guide_number_of_pixels_height} px,"
                                 f" {imager.guide_sensor_size_width_mm()} x {imager.guide_sensor_size_height_mm()} mm") \
                if imager.has_guide_sensor() else "N/A"
            equipment_table.setItem(i, self.COLUMN_GUIDE_SENSOR, centered_table_widget_item(guide_sensor_info, imager))
            equipment_table.setItem(i, self.COLUMN_OBSERVATION_SITE, centered_table_widget_item(
                ', '.join([site.name for site in imager.observation_sites]), imager
            ))
            equipment_table.setCellWidget(i, self.COLUMN_BUTTONS, self._create_delete_button(imager))

    @overrides
    def define_equipment_form_controls(self, form_layout: QVBoxLayout) -> None:
        # Add controls for Main Sensor
        form_layout.addWidget(QLabel("Main Sensor Pixel Size (μm):"))
        main_pixel_size_layout = QHBoxLayout()
        self.pixel_size_input_main_w = add_qspinbox_with_suffix_to_layout(main_pixel_size_layout, "x", " μm", 1, 50)
        self.pixel_size_input_main_h = add_qspinbox_with_suffix_to_layout(main_pixel_size_layout, "y", " μm", 1, 50)
        form_layout.addLayout(main_pixel_size_layout)

        form_layout.addWidget(QLabel("Main Sensor Number of Pixels:"))
        main_num_pixels_layout = QHBoxLayout()
        self.number_of_pixels_input_main_w = add_qspinbox_with_suffix_to_layout(main_num_pixels_layout, "w", None, 1, 10000)
        self.number_of_pixels_input_main_h = add_qspinbox_with_suffix_to_layout(main_num_pixels_layout, "h", None, 1, 10000)
        form_layout.addLayout(main_num_pixels_layout)

        self.main_sensor_size_label = QLabel(f"Sensor Size: {0:.2f} x {0:.2f} mm")
        add_to_layout_aligned_right(form_layout, self.main_sensor_size_label)

        self.guide_sensor_checkbox = QCheckBox("Imager has guide sensor")
        self.guide_sensor_checkbox.toggled.connect(self.toggle_guide_sensor_inputs)
        form_layout.addWidget(self.guide_sensor_checkbox)

        # Add controls for Guide Sensor
        self.guide_sensor_pixel_size_label = QLabel("Guide Sensor Pixel Size (μm):")
        form_layout.addWidget(self.guide_sensor_pixel_size_label)
        guide_pixel_size_layout = QHBoxLayout()
        self.pixel_size_input_guide_w = add_qspinbox_with_suffix_to_layout(guide_pixel_size_layout, "x", " μm", 1, 50)
        self.pixel_size_input_guide_h = add_qspinbox_with_suffix_to_layout(guide_pixel_size_layout, "y", " μm", 1, 50)
        form_layout.addLayout(guide_pixel_size_layout)

        self.guide_sensor_pixel_number_label = QLabel("Guide Sensor Number of Pixels:")
        form_layout.addWidget(self.guide_sensor_pixel_number_label)
        guide_num_pixels_layout = QHBoxLayout()
        self.number_of_pixels_input_guide_w = add_qspinbox_with_suffix_to_layout(guide_num_pixels_layout, "w", None, 1, 10000)
        self.number_of_pixels_input_guide_h = add_qspinbox_with_suffix_to_layout(guide_num_pixels_layout, "h", None, 1, 10000)
        form_layout.addLayout(guide_num_pixels_layout)

        self.guide_sensor_size_label = QLabel(f"Sensor Size: {0:.2f} x {0:.2f} mm")
        add_to_layout_aligned_right(form_layout, self.guide_sensor_size_label)

        self.toggle_guide_sensor_inputs(False)

        # Connect signals for real-time sensor size calculation
        self.pixel_size_input_main_w.valueChanged.connect(self.update_sensor_size_labels)
        self.pixel_size_input_main_h.valueChanged.connect(self.update_sensor_size_labels)
        self.number_of_pixels_input_main_w.valueChanged.connect(self.update_sensor_size_labels)
        self.number_of_pixels_input_main_h.valueChanged.connect(self.update_sensor_size_labels)
        self.pixel_size_input_guide_w.valueChanged.connect(self.update_sensor_size_labels)
        self.pixel_size_input_guide_h.valueChanged.connect(self.update_sensor_size_labels)
        self.number_of_pixels_input_guide_w.valueChanged.connect(self.update_sensor_size_labels)
        self.number_of_pixels_input_guide_h.valueChanged.connect(self.update_sensor_size_labels)

    def toggle_guide_sensor_inputs(self, checked: bool):
        self.pixel_size_input_guide_w.setVisible(checked)
        self.pixel_size_input_guide_h.setVisible(checked)
        self.number_of_pixels_input_guide_w.setVisible(checked)
        self.number_of_pixels_input_guide_h.setVisible(checked)
        self.guide_sensor_size_label.setVisible(checked)
        self.guide_sensor_pixel_size_label.setVisible(checked)
        self.guide_sensor_pixel_number_label.setVisible(checked)

    def update_sensor_size_labels(self):
        # Calculate sensor sizes and update labels for both main and guide sensors
        main_sensor_width_mm = calculate_sensor_size(self.pixel_size_input_main_w.value(), self.number_of_pixels_input_main_w.value())
        main_sensor_height_mm = calculate_sensor_size(self.pixel_size_input_main_h.value(), self.number_of_pixels_input_main_h.value())
        self.main_sensor_size_label.setText(f"Sensor Size: {main_sensor_width_mm:.2f} x {main_sensor_height_mm:.2f} mm")

        if self.guide_sensor_checkbox.isChecked():
            guide_sensor_width_mm = calculate_sensor_size(self.pixel_size_input_guide_w.value(), self.number_of_pixels_input_guide_w.value())
            guide_sensor_height_mm = calculate_sensor_size(self.pixel_size_input_guide_h.value(), self.number_of_pixels_input_guide_h.value())
            self.guide_sensor_size_label.setText(f"Sensor Size: {guide_sensor_width_mm:.2f} x {guide_sensor_height_mm:.2f} mm")

    @overrides
    def clear_form_to_defaults(self) -> None:
        self.pixel_size_input_main_w.setValue(1)
        self.pixel_size_input_main_h.setValue(1)
        self.number_of_pixels_input_main_w.setValue(1)
        self.number_of_pixels_input_main_h.setValue(1)
        self.pixel_size_input_guide_w.setValue(1)
        self.pixel_size_input_guide_h.setValue(1)
        self.number_of_pixels_input_guide_w.setValue(1)
        self.number_of_pixels_input_guide_h.setValue(1)
        self.guide_sensor_checkbox.setChecked(False)

    @overrides
    def populate_form_for_selected_equipment(self, selected_equipment: Imager) -> None:
        self.pixel_size_input_main_w.setValue(selected_equipment.main_pixel_size_width)
        self.pixel_size_input_main_h.setValue(selected_equipment.main_pixel_size_height)
        self.number_of_pixels_input_main_w.setValue(selected_equipment.main_number_of_pixels_width)
        self.number_of_pixels_input_main_h.setValue(selected_equipment.main_number_of_pixels_height)
        if selected_equipment.guide_pixel_size_width and selected_equipment.guide_pixel_size_height:
            self.guide_sensor_checkbox.setChecked(True)
            self.pixel_size_input_guide_w.setValue(verify_not_none(selected_equipment.guide_pixel_size_width, "Guide pixel size width"))
            self.pixel_size_input_guide_h.setValue(verify_not_none(selected_equipment.guide_pixel_size_height, "Guide pixel size height"))
            self.number_of_pixels_input_guide_w.setValue(verify_not_none(selected_equipment.guide_number_of_pixels_width, "Guide number of pixels width"))
            self.number_of_pixels_input_guide_h.setValue(verify_not_none(selected_equipment.guide_number_of_pixels_height, "Guide number of pixels height"))

    @overrides
    def create_or_update_equipment_entity(self, equipment_id: int | None, name: str, site_names: list[str]) -> Imager:
        return Imager(
            id=equipment_id,
            name=name,
            main_pixel_size_width=(verify_not_none(parse_str_int(self.pixel_size_input_main_w.cleanText()), "Main pixel size width")),
            main_pixel_size_height=(verify_not_none(parse_str_int(self.pixel_size_input_main_h.cleanText()), "Main pixel size height")),
            main_number_of_pixels_width=(verify_not_none(parse_str_int(self.number_of_pixels_input_main_w.cleanText()), "Main number of pixels width")),
            main_number_of_pixels_height=(verify_not_none(parse_str_int(self.number_of_pixels_input_main_h.cleanText()), "Main number of pixels height")),
            guide_pixel_size_width=(verify_not_none(parse_str_int(self.pixel_size_input_guide_w.cleanText()),
                                                    "Guide pixel size width")) if self.guide_sensor_checkbox.isChecked() else None,
            guide_pixel_size_height=(verify_not_none(parse_str_int(self.pixel_size_input_guide_h.cleanText()),
                                                     "Guide pixel size height")) if self.guide_sensor_checkbox.isChecked() else None,
            guide_number_of_pixels_width=(verify_not_none(parse_str_int(self.number_of_pixels_input_guide_w.cleanText()),
                                                          "Guide number of pixels width")) if self.guide_sensor_checkbox.isChecked() else None,
            guide_number_of_pixels_height=(verify_not_none(parse_str_int(self.number_of_pixels_input_guide_h.cleanText()),
                                                           "Guide number of pixels height")) if self.guide_sensor_checkbox.isChecked() else None,
            observation_sites=self.observation_site_service.get_for_names(site_names)
        )
