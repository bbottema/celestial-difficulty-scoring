from abc import abstractmethod, ABC, ABCMeta
from typing import TypeVar, Generic, Type, final

from PySide6.QtCore import Qt
from PySide6.QtWidgets import *

from app.config.event_bus_config import bus, NightGuideEvent
from app.orm.repositories.base_equipment_repository import EquipmentEntity
from app.orm.services.base_service import MutationEvents, BaseService
from app.orm.services.observation_site_service import ObservationSiteService
from app.utils.assume import verify_not_none
from app.utils.gui_helper import DATA_ROLE, get_selection_background_colour, colour_as_rgba, get_selection_foreground_colour

Checked: Qt.CheckState = Qt.CheckState.Checked
Unchecked: Qt.CheckState = Qt.CheckState.Unchecked

T = TypeVar('T', bound=EquipmentEntity)


class MetaQWidgetABCMeta(type(QWidget), ABCMeta):  # type: ignore
    pass


class ManageEquipmentTab(Generic[T], QWidget, ABC, metaclass=MetaQWidgetABCMeta):
    name_edit: QLineEdit
    equipment_table: QTableWidget
    equipment_type: Type[T]
    selected_equipment: T | None
    observation_site_list_widget: QListWidget

    def __init__(self, equipment_type: Type[T], equipment_service: BaseService[T], observation_site_service: ObservationSiteService,
                 equipment_events: MutationEvents):
        super().__init__()
        self.equipment_type = equipment_type
        self.equipment_service = equipment_service
        self.observation_site_service = observation_site_service
        self.selected_equipment = None
        self.setup_equipment_tab()

        # necessary delay because the calls to resizeRowsToContents() only work after the app has been rendered
        bus.on(NightGuideEvent.APP_STARTED, lambda *args: self._populate_equipment_table(self.equipment_table))

        bus.on(NightGuideEvent.OBSERVATION_SITE_ADDED, lambda *args: self._repopulate_equipment_table_on_repo_changes())
        bus.on(NightGuideEvent.OBSERVATION_SITE_UPDATED, lambda *args: self._repopulate_equipment_table_on_repo_changes())
        bus.on(NightGuideEvent.OBSERVATION_SITE_DELETED, lambda *args: self._repopulate_equipment_table_on_repo_changes())

        bus.on(equipment_events.added, lambda *args: self._repopulate_equipment_table_on_repo_changes())
        bus.on(equipment_events.updated, lambda *args: self._repopulate_equipment_table_on_repo_changes())
        bus.on(equipment_events.deleted, lambda *args: self._repopulate_equipment_table_on_repo_changes())

    @final
    # noinspection PyAttributeOutsideInit
    def setup_equipment_tab(self):
        self.layout = QHBoxLayout(self)
        self._create_table_on_the_left(self.layout)
        self._create_form_on_the_right(self.layout)

    @final
    def _create_table_on_the_left(self, horizontal_layout: QHBoxLayout):
        self.equipment_table = self.create_equipment_table()
        self.equipment_table.setStyleSheet(f"""
            QTableWidget::item:selected {{ 
                selection-color: {colour_as_rgba(get_selection_foreground_colour())}; 
                color: {colour_as_rgba(get_selection_foreground_colour())}; 
                background-color: {colour_as_rgba(get_selection_background_colour())}; 
            }}
        """)
        self.equipment_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # select row on cell click
        self.equipment_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)  # disallow column and table selection
        self.equipment_table.itemClicked.connect(self._select_equipment)
        horizontal_layout.addWidget(self.equipment_table, 2)

    @final
    def _select_equipment(self, item: QTableWidgetItem):
        self.equipment_table.selectRow(item.row())
        self.selected_equipment = item.data(DATA_ROLE)
        self._populate_observation_sites_dropdown(self.observation_site_list_widget)
        self._populate_form_for_selected_equipment(verify_not_none(self.selected_equipment, f"selected {self.equipment_type.__name__}"))

    def _populate_form_for_selected_equipment(self, selected_equipment: T):
        self.name_edit.setText(selected_equipment.name)
        self.populate_form_for_selected_equipment(selected_equipment)

    @final
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

        self._clear_form_to_defaults()

    @final
    def _clear_form_to_defaults(self) -> None:
        self.name_edit.clear()
        for i in range(self.observation_site_list_widget.count()):
            item = self.observation_site_list_widget.item(i)
            checkbox = self.observation_site_list_widget.itemWidget(item)
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(False)

        self.clear_form_to_defaults()

    @final
    def _add_new_equipment_button(self, form_layout):
        new_equipment_button = QPushButton(f"New {self.equipment_type.__name__.capitalize()}")
        new_equipment_button.clicked.connect(self._handle_new_equipment_button_click)
        form_layout.addWidget(new_equipment_button)

    @final
    def _add_equipment_name_input(self, form_layout):
        self.name_edit = QLineEdit()
        form_layout.addWidget(QLabel(f"{self.equipment_type.__name__.capitalize()} Name:"))
        form_layout.addWidget(self.name_edit)

    @final
    def _add_observation_sites_dropdown(self, form_layout):
        form_layout.addWidget(QLabel("Observation Site:"))
        self.observation_site_list_widget = QListWidget()
        self.observation_site_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self._populate_observation_sites_dropdown(self.observation_site_list_widget)
        form_layout.addWidget(self.observation_site_list_widget)

    @final
    def _populate_observation_sites_dropdown(self, observation_site_list_widget: QListWidget):
        observation_site_list_widget.clear()
        for observation_site in self.observation_site_service.get_all():
            item = QListWidgetItem()
            checkbox = QCheckBox(observation_site.name)
            checkbox.setChecked(True if self.selected_equipment and observation_site in self.selected_equipment.observation_sites else False)
            observation_site_list_widget.addItem(item)
            observation_site_list_widget.setItemWidget(item, checkbox)

    @final
    def _add_save_button(self, form_layout):
        save_equipment_button = QPushButton("Save")
        save_equipment_button.clicked.connect(self._handle_save_equipment_button_click)
        form_layout.addWidget(save_equipment_button)

    @final
    def _repopulate_equipment_table_on_repo_changes(self):
        self._populate_equipment_table(self.equipment_table)
        self._populate_observation_sites_dropdown(self.observation_site_list_widget)

    @final
    def _reselect_current_active_equipment(self, equipment_table: QTableWidget) -> None:
        if self.selected_equipment:
            for row in range(equipment_table.rowCount()):
                equipment_associated_with_row = equipment_table.item(row, 0).data(DATA_ROLE)
                if equipment_associated_with_row == self.selected_equipment:
                    equipment_table.selectRow(row)
                    # update selected equipment, so the content is up-to-date (in case the table was rebuilt due to a repo event)
                    self.selected_equipment = equipment_associated_with_row
                    return

    @final
    def _handle_new_equipment_button_click(self) -> None:
        self.selected_equipment = None
        self.equipment_table.clearSelection()
        self.equipment_table.selectionModel().clearSelection()
        self._clear_form_to_defaults()

    @final
    def _handle_save_equipment_button_click(self) -> None:
        equipment_id = self.selected_equipment.id if self.selected_equipment else None
        name = self.name_edit.text()

        site_names = []
        for i in range(self.observation_site_list_widget.count()):
            item = self.observation_site_list_widget.item(i)
            widget = self.observation_site_list_widget.itemWidget(item)
            if isinstance(widget, QCheckBox) and widget.isChecked():
                site_names.append(widget.text())

        updated_equipment: T = self.create_or_update_equipment_entity(equipment_id, name, site_names)

        if updated_equipment.id:
            self.equipment_service.update(updated_equipment)
        else:
            self.equipment_service.add(updated_equipment)

    def _populate_equipment_table(self, equipment_table: QTableWidget) -> None:
        equipment_table.setRowCount(0)
        self.populate_equipment_table(equipment_table)
        equipment_table.resizeRowsToContents()
        self._reselect_current_active_equipment(equipment_table)

    @final
    def _create_delete_button(self, equipment):
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda *args, equipment_id=equipment.id: self.equipment_service.delete_by_id(equipment_id))
        return delete_button

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
    def clear_form_to_defaults(self) -> None:
        pass

    @abstractmethod
    def populate_form_for_selected_equipment(self, selected_equipment: T) -> None:
        pass

    @abstractmethod
    def create_or_update_equipment_entity(self, equipment_id: int | None, name: str, site_names: list[str]) -> T:
        pass
