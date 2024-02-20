from abc import abstractmethod

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QLineEdit, QLabel, QPushButton, QSpacerItem, QListWidget, QListWidgetItem, QSizePolicy, \
    QHBoxLayout


class ManageEquipmentTab(QWidget):

    def __init__(self, equipment_type, observation_site_service):
        super().__init__()
        self.equipment_type = equipment_type
        self.observation_site_service = observation_site_service
        self.setup_equipment_tab()

    # noinspection PyAttributeOutsideInit
    def setup_equipment_tab(self):
        self.layout = QHBoxLayout(self)
        self.equipment_table = QTableWidget()
        self.layout.addWidget(self.equipment_table, 2)

        form_layout = QVBoxLayout()

        self.add_new_equipment_button(form_layout)
        self.add_equipment_name_input(form_layout)

        # insert subclass form controls

        self.add_observation_sites_dropdown(form_layout)
        form_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.add_save_button(form_layout)

        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        self.layout.addWidget(form_widget, 1)

    def add_new_equipment_button(self, form_layout):
        form_layout.addWidget(QPushButton(f"New {self.equipment_type}"))

    def add_equipment_name_input(self, form_layout):
        name_edit = QLineEdit()
        form_layout.addWidget(QLabel(f"{self.equipment_type.capitalize()} Name:"))
        form_layout.addWidget(name_edit)

    def add_observation_sites_dropdown(self, form_layout):
        form_layout.addWidget(QLabel("Observation Site:"))
        observation_site_list_widget = QListWidget()
        observation_site_list_widget.setSelectionMode(QListWidget.MultiSelection)
        for observation_site in self.observation_site_service.get_all():
            item = QListWidgetItem(observation_site.name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            observation_site_list_widget.addItem(item)
        form_layout.addWidget(observation_site_list_widget)

    def add_save_button(self, form_layout):
        form_layout.addWidget(QPushButton("Save"))

    @abstractmethod
    def populate_equipment_table(self, *args):
        raise NotImplementedError('This method needs to be implemented in the child class')
