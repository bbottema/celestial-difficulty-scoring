import os
import signal
from typing import Any

from PySide6 import QtWidgets
from PySide6.QtCore import QTimer
from PySide6.QtGui import Qt, QFont, QColor
from PySide6.QtWidgets import QTableWidgetItem, QTableWidget, QHeaderView, QWidget, QHBoxLayout, QLayout, QBoxLayout, QSpinBox

from app.utils.ui_debug_clipboard_watch import UiDebugClipBoardWatch

DATA_ROLE = Qt.ItemDataRole.UserRole + 1


def configure_close_signal_handler():
    import sys
    from PySide6.QtWidgets import QApplication, QMessageBox

    def _sigint_handler(*args):
        sys.stderr.write('\r')
        if QMessageBox.question(None, '', "Are you sure you want to quit?",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            QApplication.quit()

    signal.signal(signal.SIGINT, _sigint_handler)

    timer = QTimer()
    timer.start(500)  # You may change this if you wish.
    timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.


def default_table(labels: list[str], editable=False) -> QTableWidget:
    table = QTableWidget(0, len(labels))
    table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
    table.setHorizontalHeaderLabels(labels)
    table.verticalHeader().setVisible(False)
    if not editable:
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    header_font = QFont()  # Create a new font object
    header_font.setBold(True)  # Set the font to bold
    table.horizontalHeader().setFont(header_font)

    UiDebugClipBoardWatch.install_on_table(table)

    return table


def centered_table_widget_item(value: str, data: Any = None) -> QTableWidgetItem:
    item = QTableWidgetItem(value)
    item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
    if data is not None:
        item.setData(DATA_ROLE, data)
    return item


def remove_table_row_by_contained_widget(table: QTableWidget, row_widget: QWidget) -> None:
    table.removeRow(table.indexAt(row_widget.pos()).row())


def get_selection_background_colour() -> QColor:
    return get_qt_material_colour('QTMATERIAL_PRIMARYCOLOR', 0.2)


def get_selection_foreground_colour() -> QColor:
    return get_qt_material_colour('QTMATERIAL_SECONDARYTEXTCOLOR')


def get_qt_material_colour(qt_material_colour_name: str, alpha_f: float = 1.0) -> QColor:
    colour = QColor(os.environ.get(qt_material_colour_name))
    colour.setAlphaF(alpha_f)
    return colour


def colour_as_rgba(color: QColor) -> str:
    return f'rgba({color.red()}, {color.green()}, {color.blue()}, {color.alphaF()})'


def add_to_layout_aligned_right(layout: QBoxLayout, widget: QWidget):
    align_right_layout = QHBoxLayout()
    align_right_layout.addStretch()
    align_right_layout.addWidget(widget)
    layout.addLayout(align_right_layout)


def add_qspinbox_with_suffix_to_layout(layout: QLayout, prefix: str | None, suffix: str | None, min_value: int, max_value: int) -> QSpinBox:
    spin_box = QSpinBox()
    if prefix:
        spin_box.setPrefix(prefix)
    if suffix:
        spin_box.setSuffix(suffix)
    spin_box.setMinimum(min_value)
    spin_box.setMaximum(max_value)
    layout.addWidget(spin_box)
    return spin_box
