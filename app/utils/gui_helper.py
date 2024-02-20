from PySide6.QtGui import Qt, QFont
from PySide6.QtWidgets import QTableWidgetItem, QTableWidget, QHeaderView

from utils.ui_debug_clipboard_watch import UiDebugClipBoardWatch


def default_table(labels: [str]) -> QTableWidget:
    table = QTableWidget(0, len(labels))
    table.setHorizontalHeaderLabels(labels)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    header_font = QFont()  # Create a new font object
    header_font.setBold(True)  # Set the font to bold
    table.horizontalHeader().setFont(header_font)

    UiDebugClipBoardWatch.install_on_table(table)

    return table


def centered_table_widget_item(value: str) -> QTableWidgetItem:
    item = QTableWidgetItem(value)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item
