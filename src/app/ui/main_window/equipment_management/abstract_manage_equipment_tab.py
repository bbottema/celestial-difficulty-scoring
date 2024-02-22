from abc import abstractmethod, ABC, ABCMeta

from PySide6.QtCore import Qt
from PySide6.QtWidgets import *


class MetaQWidgetABCMeta(type(QWidget), ABCMeta):  # type: ignore
    pass


class ManageEquipmentTab(QWidget, ABC, metaclass=MetaQWidgetABCMeta):

    def __init__(self, equipment_type, observation_site_service):
        super().__init__()
        self.equipment_type = equipment_type
        self.observation_site_service = observation_site_service
        self.setup_equipment_tab()

    # noinspection PyAttributeOutsideInit
    def setup_equipment_tab(self):
        self.layout = QHBoxLayout(self)
        self._create_table_on_the_left(self.layout)
        self._create_form_on_the_right(self.layout)

    def _create_table_on_the_left(self, horizontal_layout: QHBoxLayout):
        self.equipment_table = self.create_equipment_table()
        horizontal_layout.addWidget(self.equipment_table, 2)

    def _create_form_on_the_right(self, horizontal_layout: QHBoxLayout):
        form_layout = QVBoxLayout()
        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        horizontal_layout.addWidget(form_widget, 1)

        self._add_new_equipment_button(form_layout)
        self._add_equipment_name_input(form_layout)

        self.define_equipment_form_controls(form_layout)

        self._add_observation_sites_dropdown(form_layout)
        form_layout.addItem(QSpacerItem(20, 40))
        self._add_save_button(form_layout)

    def _add_new_equipment_button(self, form_layout):
        form_layout.addWidget(QPushButton(f"New {self.equipment_type}"))

    def _add_equipment_name_input(self, form_layout):
        name_edit = QLineEdit()
        form_layout.addWidget(QLabel(f"{self.equipment_type.capitalize()} Name:"))
        form_layout.addWidget(name_edit)

    def _add_observation_sites_dropdown(self, form_layout):
        form_layout.addWidget(QLabel("Observation Site:"))
        observation_site_list_widget = QListWidget()
        observation_site_list_widget.setSelectionMode(QListWidget.MultiSelection)
        for observation_site in self.observation_site_service.get_all():
            item = QListWidgetItem(observation_site.name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            observation_site_list_widget.addItem(item)
        form_layout.addWidget(observation_site_list_widget)

    def _add_save_button(self, form_layout):
        form_layout.addWidget(QPushButton("Save"))

    @abstractmethod
    def create_equipment_table(self) -> QTableWidget:
        pass

    @abstractmethod
    def populate_equipment_table(self, equipment_table: QTableWidget):
        pass

    @abstractmethod
    def define_equipment_form_controls(self, form_layout: QVBoxLayout):
        pass
