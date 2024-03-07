from abc import abstractmethod, ABC, ABCMeta
from typing import TypeVar, Generic, Type

from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *

from app.orm.repositories.base_equipment_repository import EquipmentEntity
from app.orm.services.observation_site_service import ObservationSiteService
from app.utils.assume import verify_not_none
from app.utils.gui_helper import DATA_ROLE, apply_row_selection_styles, clear_table_row_selection_styles

Checked: Qt.CheckState = Qt.CheckState.Checked
Unchecked: Qt.CheckState = Qt.CheckState.Unchecked

T = TypeVar('T', bound=EquipmentEntity)

SELECTED_ROW_BACKGROUND_COLOR = QtGui.QColor(173, 216, 230)


class MetaQWidgetABCMeta(type(QWidget), ABCMeta):  # type: ignore
    pass


class ManageEquipmentTab(Generic[T], QWidget, ABC, metaclass=MetaQWidgetABCMeta):
    name_edit: QLineEdit
    equipment_table: QTableWidget
    equipment_type: Type[T]
    selected_equipment: T | None
    observation_site_list_widget: QListWidget

    def __init__(self, equipment_type: Type[T], observation_site_service: ObservationSiteService):
        super().__init__()
        self.equipment_type = equipment_type
        self.observation_site_service = observation_site_service
        self.selected_equipment = None
        self.setup_equipment_tab()
        self.populate_equipment_table(self.equipment_table)

    # noinspection PyAttributeOutsideInit
    def setup_equipment_tab(self):
        self.layout = QHBoxLayout(self)
        self._create_table_on_the_left(self.layout)
        self._create_form_on_the_right(self.layout)

    def _create_table_on_the_left(self, horizontal_layout: QHBoxLayout):
        self.equipment_table = self.create_equipment_table()
        self.equipment_table.setStyleSheet("""
            QTableWidget::item:selected { color: inherit; background-color: {SELECTED_ROW_BACKGROUND_COLOR.name()}; }
            QHeaderView::section:selected { color: inherit; background-color: {SELECTED_ROW_BACKGROUND_COLOR.name()}; }
        """)
        self.equipment_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.equipment_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.equipment_table.itemClicked.connect(self._select_equipment)
        self.selected_row_style = "background-color: lightblue;"
        horizontal_layout.addWidget(self.equipment_table, 2)

    def _select_equipment(self, item: QTableWidgetItem):
        apply_row_selection_styles(self.equipment_table, item.row(), SELECTED_ROW_BACKGROUND_COLOR)
        self.selected_equipment = item.data(DATA_ROLE)
        self._populate_observation_sites_dropdown(self.observation_site_list_widget)
        self.handle_select_equipment(verify_not_none(self.selected_equipment, f"selected {self.equipment_type.__name__}"))

    def _create_form_on_the_right(self, horizontal_layout: QHBoxLayout):
        form_layout = QVBoxLayout()
        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        horizontal_layout.addWidget(form_widget, 1)

        self._add_new_equipment_button(form_layout)
        self._add_equipment_name_input(form_layout)
        self.define_equipment_form_controls(form_layout)
        self._add_observation_sites_dropdown(form_layout)
        form_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self._add_save_button(form_layout)

    def _add_new_equipment_button(self, form_layout):
        new_equipment_button = QPushButton(f"New {self.equipment_type.__name__.capitalize()}")
        new_equipment_button.clicked.connect(self.handle_new_equipment_button_click)
        form_layout.addWidget(new_equipment_button)

    def _add_equipment_name_input(self, form_layout):
        self.name_edit = QLineEdit()
        form_layout.addWidget(QLabel(f"{self.equipment_type.__name__.capitalize()} Name:"))
        form_layout.addWidget(self.name_edit)

    def _add_observation_sites_dropdown(self, form_layout):
        form_layout.addWidget(QLabel("Observation Site:"))
        self.observation_site_list_widget = QListWidget()
        self.observation_site_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self._populate_observation_sites_dropdown(self.observation_site_list_widget)
        form_layout.addWidget(self.observation_site_list_widget)

    def _populate_observation_sites_dropdown(self, observation_site_list_widget: QListWidget):
        observation_site_list_widget.clear()
        for observation_site in self.observation_site_service.get_all():
            item = QListWidgetItem(observation_site.name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Checked if self.selected_equipment and observation_site in self.selected_equipment else Unchecked)
            observation_site_list_widget.addItem(item)

    def _add_save_button(self, form_layout):
        save_equipment_button = QPushButton("Save")
        save_equipment_button.clicked.connect(self.handle_save_equipment_button_click)
        form_layout.addWidget(save_equipment_button)

    @abstractmethod
    def create_equipment_table(self) -> QTableWidget:
        pass

    @abstractmethod
    def populate_equipment_table(self, equipment_table: QTableWidget) -> None:
        pass

    @abstractmethod
    def define_equipment_form_controls(self, form_layout: QVBoxLayout) -> None:
        pass

    @abstractmethod
    def handle_new_equipment_button_click(self) -> None:
        self.equipment_table.clearSelection()
        clear_table_row_selection_styles(self.equipment_table)

    @abstractmethod
    def handle_save_equipment_button_click(self) -> None:
        pass

    @abstractmethod
    def handle_select_equipment(self, selected_equipment: T):
        pass
