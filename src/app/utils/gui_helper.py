import signal
from typing import Any

from PySide6.QtCore import QTimer
from PySide6.QtGui import Qt, QFont, QColor
from PySide6.QtWidgets import QTableWidgetItem, QTableWidget, QHeaderView

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


def default_table(labels: list[str]) -> QTableWidget:
    table = QTableWidget(0, len(labels))
    table.setHorizontalHeaderLabels(labels)
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


def clear_table_row_selection_styles(table: QTableWidget, color: Qt.GlobalColor = Qt.GlobalColor.white):
    for row in range(table.rowCount()):
        for column in range(table.columnCount()):
            item = table.item(row, column)
            if item is not None:
                item.setBackground(color)


def apply_row_selection_styles(table: QTableWidget, row, color: QColor):
    clear_table_row_selection_styles(table)
    for column in range(table.columnCount()):
        row_item = table.item(row, column)
        if row_item is not None:
            row_item.setBackground(color)
