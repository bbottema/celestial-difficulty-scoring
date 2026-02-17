"""
Target List Management UI Component.

Phase 9.2: Enables users to create and manage custom observing lists.
"""
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSplitter,
    QLabel, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox, QFileDialog,
    QGroupBox, QCheckBox, QHeaderView, QFrame
)
from PySide6.QtCore import Qt
from injector import inject

from app.config.autowire import component
from app.config.event_bus_config import NightGuideEvent, database_ready_bus, bus
from app.orm.model.entities import TargetList, TargetListItem
from app.orm.services.target_list_service import TargetListService
from app.target_lists.import_export import TargetListImportExport
from app.utils.gui_helper import default_table, centered_table_widget_item

logger = logging.getLogger(__name__)


@component
class TargetListComponent(QWidget):
    """
    Main component for target list management.
    
    Layout:
    - Left panel: List of target lists (table)
    - Right panel: Objects in selected list (table)
    """

    @inject
    def __init__(self, target_list_service: TargetListService):
        super().__init__(None)
        self.target_list_service = target_list_service
        self.import_export = TargetListImportExport(target_list_service)
        self.selected_list_id: Optional[int] = None
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.init_ui(layout)
        self._subscribe_to_events()

    def init_ui(self, layout: QVBoxLayout):
        # Title
        title = QLabel("📋 My Target Lists")
        title.setStyleSheet("font-weight: bold; font-size: 16px; padding: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Create and manage custom observing lists. Add objects, track observations, and export for use in the field.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; padding: 0 10px 10px 10px;")
        layout.addWidget(desc)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel: Target lists
        left_panel = self._create_lists_panel()
        splitter.addWidget(left_panel)

        # Right panel: List items
        right_panel = self._create_items_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([300, 500])

        # Initial population
        database_ready_bus.subscribe(self._populate_lists_table)

    def _create_lists_panel(self) -> QWidget:
        """Create the left panel with target lists table."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 5, 0)

        # Lists table
        self.lists_table = default_table(['Name', 'Objects', 'Observed'])
        self.lists_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.lists_table.setSelectionMode(QTableWidget.SingleSelection)
        self.lists_table.itemSelectionChanged.connect(self._on_list_selected)
        layout.addWidget(self.lists_table)

        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.new_list_btn = QPushButton("New List")
        self.new_list_btn.clicked.connect(self._create_new_list)
        buttons_layout.addWidget(self.new_list_btn)

        self.edit_list_btn = QPushButton("Edit")
        self.edit_list_btn.clicked.connect(self._edit_selected_list)
        self.edit_list_btn.setEnabled(False)
        buttons_layout.addWidget(self.edit_list_btn)

        self.delete_list_btn = QPushButton("Delete")
        self.delete_list_btn.clicked.connect(self._delete_selected_list)
        self.delete_list_btn.setEnabled(False)
        buttons_layout.addWidget(self.delete_list_btn)

        layout.addLayout(buttons_layout)

        # Import/Export buttons
        io_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("Import CSV")
        self.import_btn.clicked.connect(self._import_csv)
        io_layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("Export CSV")
        self.export_btn.clicked.connect(self._export_csv)
        self.export_btn.setEnabled(False)
        io_layout.addWidget(self.export_btn)

        layout.addLayout(io_layout)

        return panel

    def _create_items_panel(self) -> QWidget:
        """Create the right panel with list items table."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 0, 0, 0)

        # Header with list name
        self.items_header = QLabel("Select a list to view objects")
        self.items_header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(self.items_header)

        # Items table
        self.items_table = default_table(['Name', 'Type', 'Mag', 'RA', 'Dec', 'Observed'])
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.setSelectionMode(QTableWidget.ExtendedSelection)
        layout.addWidget(self.items_table)

        # Item action buttons
        buttons_layout = QHBoxLayout()

        self.add_object_btn = QPushButton("Add Object")
        self.add_object_btn.clicked.connect(self._add_object)
        self.add_object_btn.setEnabled(False)
        buttons_layout.addWidget(self.add_object_btn)

        self.remove_object_btn = QPushButton("Remove")
        self.remove_object_btn.clicked.connect(self._remove_selected_objects)
        self.remove_object_btn.setEnabled(False)
        buttons_layout.addWidget(self.remove_object_btn)

        self.mark_observed_btn = QPushButton("Mark Observed")
        self.mark_observed_btn.clicked.connect(self._mark_selected_observed)
        self.mark_observed_btn.setEnabled(False)
        buttons_layout.addWidget(self.mark_observed_btn)

        buttons_layout.addStretch()

        # Score button
        self.score_list_btn = QPushButton("Score List")
        self.score_list_btn.setToolTip("Score all objects in this list for observability")
        self.score_list_btn.clicked.connect(self._score_selected_list)
        self.score_list_btn.setEnabled(False)
        buttons_layout.addWidget(self.score_list_btn)

        layout.addLayout(buttons_layout)

        return panel

    def _subscribe_to_events(self):
        """Subscribe to target list events."""
        bus.on(NightGuideEvent.TARGET_LIST_CREATED, lambda _: self._populate_lists_table())
        bus.on(NightGuideEvent.TARGET_LIST_UPDATED, lambda _: self._populate_lists_table())
        bus.on(NightGuideEvent.TARGET_LIST_DELETED, lambda _: self._on_list_deleted())
        bus.on(NightGuideEvent.TARGET_LIST_ITEM_ADDED, lambda _: self._refresh_items())
        bus.on(NightGuideEvent.TARGET_LIST_ITEM_REMOVED, lambda _: self._refresh_items())
        bus.on(NightGuideEvent.TARGET_LIST_ITEM_UPDATED, lambda _: self._refresh_items())

    def _populate_lists_table(self, *args):
        """Populate the target lists table."""
        self.lists_table.setSortingEnabled(False)
        self.lists_table.setRowCount(0)
        
        lists = self.target_list_service.get_all_lists()
        
        for i, target_list in enumerate(lists):
            self.lists_table.insertRow(i)
            
            name_item = centered_table_widget_item(target_list.name)
            name_item.setData(Qt.UserRole, target_list.id)
            self.lists_table.setItem(i, 0, name_item)
            
            self.lists_table.setItem(i, 1, centered_table_widget_item(str(target_list.object_count)))
            self.lists_table.setItem(i, 2, centered_table_widget_item(
                f"{target_list.observed_count}/{target_list.object_count}"
            ))
        
        self.lists_table.setSortingEnabled(True)
        
        # Re-select if we had a selection
        if self.selected_list_id:
            self._select_list_by_id(self.selected_list_id)

    def _populate_items_table(self, target_list: TargetList):
        """Populate the items table for a target list."""
        self.items_table.setSortingEnabled(False)
        self.items_table.setRowCount(0)
        
        for i, item in enumerate(target_list.items or []):
            self.items_table.insertRow(i)
            
            name_item = centered_table_widget_item(item.object_name)
            name_item.setData(Qt.UserRole, item.id)
            self.items_table.setItem(i, 0, name_item)
            
            self.items_table.setItem(i, 1, centered_table_widget_item(item.object_type or '-'))
            self.items_table.setItem(i, 2, centered_table_widget_item(
                f"{item.magnitude:.1f}" if item.magnitude else '-'
            ))
            self.items_table.setItem(i, 3, centered_table_widget_item(
                f"{item.ra:.4f}" if item.ra else '-'
            ))
            self.items_table.setItem(i, 4, centered_table_widget_item(
                f"{item.dec:.4f}" if item.dec else '-'
            ))
            
            observed_text = "✓" if item.observed else ""
            self.items_table.setItem(i, 5, centered_table_widget_item(observed_text))
        
        self.items_table.setSortingEnabled(True)

    def _on_list_selected(self):
        """Handle list selection change."""
        selected_rows = self.lists_table.selectionModel().selectedRows()
        
        if selected_rows:
            row = selected_rows[0].row()
            name_item = self.lists_table.item(row, 0)
            list_id = name_item.data(Qt.UserRole)
            self.selected_list_id = list_id
            
            target_list = self.target_list_service.get_list(list_id)
            if target_list:
                self.items_header.setText(f"📋 {target_list.name}")
                self._populate_items_table(target_list)
                
                # Enable buttons
                self.edit_list_btn.setEnabled(True)
                self.delete_list_btn.setEnabled(True)
                self.export_btn.setEnabled(True)
                self.add_object_btn.setEnabled(True)
                self.remove_object_btn.setEnabled(True)
                self.mark_observed_btn.setEnabled(True)
                self.score_list_btn.setEnabled(True)
        else:
            self.selected_list_id = None
            self.items_header.setText("Select a list to view objects")
            self.items_table.setRowCount(0)
            
            # Disable buttons
            self.edit_list_btn.setEnabled(False)
            self.delete_list_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
            self.add_object_btn.setEnabled(False)
            self.remove_object_btn.setEnabled(False)
            self.mark_observed_btn.setEnabled(False)
            self.score_list_btn.setEnabled(False)

    def _on_list_deleted(self):
        """Handle list deletion."""
        self.selected_list_id = None
        self._populate_lists_table()
        self._on_list_selected()

    def _refresh_items(self, *args):
        """Refresh items table for current selection."""
        if self.selected_list_id:
            target_list = self.target_list_service.get_list(self.selected_list_id)
            if target_list:
                self._populate_items_table(target_list)
        self._populate_lists_table()

    def _select_list_by_id(self, list_id: int):
        """Select a list in the table by ID."""
        for row in range(self.lists_table.rowCount()):
            item = self.lists_table.item(row, 0)
            if item and item.data(Qt.UserRole) == list_id:
                self.lists_table.selectRow(row)
                break

    # ----- List Actions -----

    def _create_new_list(self):
        """Open dialog to create a new target list."""
        dialog = TargetListDialog(self)
        if dialog.exec():
            name, description = dialog.get_values()
            try:
                self.target_list_service.create_list(name, description)
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def _edit_selected_list(self):
        """Edit the selected target list."""
        if not self.selected_list_id:
            return
        
        target_list = self.target_list_service.get_list(self.selected_list_id)
        if not target_list:
            return
        
        dialog = TargetListDialog(self, target_list)
        if dialog.exec():
            name, description = dialog.get_values()
            try:
                self.target_list_service.update_list(self.selected_list_id, name, description)
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def _delete_selected_list(self):
        """Delete the selected target list."""
        if not self.selected_list_id:
            return
        
        target_list = self.target_list_service.get_list(self.selected_list_id)
        if not target_list:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete List",
            f"Are you sure you want to delete '{target_list.name}'?\n"
            f"This will remove all {target_list.object_count} objects in the list.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.target_list_service.delete_list(self.selected_list_id)

    # ----- Item Actions -----

    def _add_object(self):
        """Add an object to the selected list."""
        if not self.selected_list_id:
            return
        
        dialog = AddObjectDialog(self)
        if dialog.exec():
            object_name = dialog.get_object_name()
            if object_name:
                item = self.target_list_service.add_object(self.selected_list_id, object_name)
                if not item:
                    QMessageBox.warning(
                        self,
                        "Object Not Found",
                        f"Could not find '{object_name}' in the catalog.\n"
                        "Please check the name and try again."
                    )

    def _remove_selected_objects(self):
        """Remove selected objects from the list."""
        selected_rows = self.items_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        reply = QMessageBox.question(
            self,
            "Remove Objects",
            f"Remove {len(selected_rows)} selected object(s) from the list?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for index in selected_rows:
                row = index.row()
                item = self.items_table.item(row, 0)
                item_id = item.data(Qt.UserRole)
                self.target_list_service.remove_object(item_id)

    def _mark_selected_observed(self):
        """Toggle observed status of selected objects."""
        selected_rows = self.items_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        for index in selected_rows:
            row = index.row()
            item = self.items_table.item(row, 0)
            item_id = item.data(Qt.UserRole)
            
            # Get current status
            observed_item = self.items_table.item(row, 5)
            currently_observed = observed_item.text() == "✓"
            
            # Toggle
            self.target_list_service.mark_observed(item_id, not currently_observed)

    def _score_selected_list(self):
        """Score the selected list and display results."""
        if not self.selected_list_id:
            return
        
        # TODO: Integrate with scoring service and results display
        # For now, just show a message
        QMessageBox.information(
            self,
            "Score List",
            "Scoring integration coming soon!\n\n"
            "This will score all objects in the list and display them in the "
            "main scoring table."
        )

    # ----- Import/Export -----

    def _import_csv(self):
        """Import a target list from CSV."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Import Target List",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not filepath:
            return
        
        # Get list name from user
        dialog = TargetListDialog(self, title="Import List")
        if not dialog.exec():
            return
        
        name, description = dialog.get_values()
        
        try:
            target_list, failed = self.import_export.import_csv(
                Path(filepath), name
            )
            
            msg = f"Imported {target_list.object_count} objects to '{name}'."
            if failed:
                msg += f"\n\n{len(failed)} objects could not be resolved:\n"
                msg += ", ".join(failed[:10])
                if len(failed) > 10:
                    msg += f"... and {len(failed) - 10} more"
            
            QMessageBox.information(self, "Import Complete", msg)
            
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", f"Failed to import CSV: {e}")

    def _export_csv(self):
        """Export the selected list to CSV."""
        if not self.selected_list_id:
            return
        
        target_list = self.target_list_service.get_list(self.selected_list_id)
        if not target_list:
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Target List",
            f"{target_list.name}.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not filepath:
            return
        
        try:
            self.import_export.export_csv(target_list, Path(filepath))
            QMessageBox.information(
                self,
                "Export Complete",
                f"Exported {target_list.object_count} objects to:\n{filepath}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export CSV: {e}")


class TargetListDialog(QDialog):
    """Dialog for creating/editing a target list."""

    def __init__(self, parent, target_list: Optional[TargetList] = None, title: str = None):
        super().__init__(parent)
        self.target_list = target_list
        
        self.setWindowTitle(title or ("Edit List" if target_list else "New Target List"))
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        if target_list:
            self.name_input.setText(target_list.name)
        layout.addRow("Name:", self.name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        if target_list and target_list.description:
            self.description_input.setPlainText(target_list.description)
        layout.addRow("Description:", self.description_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_values(self) -> tuple[str, Optional[str]]:
        """Get the dialog values."""
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip() or None
        return name, description


class AddObjectDialog(QDialog):
    """Dialog for adding an object to a target list."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Add Object")
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Enter an object name or identifier:\n"
            "Examples: M31, NGC 7000, Jupiter, Andromeda Galaxy"
        )
        instructions.setStyleSheet("color: #666;")
        layout.addWidget(instructions)
        
        # Input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Object name...")
        layout.addWidget(self.name_input)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.name_input.setFocus()

    def get_object_name(self) -> str:
        """Get the entered object name."""
        return self.name_input.text().strip()
