from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtGui import QWindow, QMouseEvent
from PySide6.QtWidgets import *

from app.utils.os_util import ctrl_c

""" 
This module provides a way to easily copy the value of a CTRL-clicked UI element to the clipboard, focussed on helping you locate the object in your code base.
It installs an event filter on a QObject and listens for click events on various UI elements.
Or it installs click handlers on a QTableWidget's cells and headers, since they don't propagate click events to their parent.
"""

CUSTOM_NAME_PROPERTY = "customName"


def configure_debug_clipboard_watch(app: QApplication):
    watch = UiDebugClipBoardWatch()
    app.installEventFilter(watch)
    app.aboutToQuit.connect(lambda: app.removeEventFilter(watch))


class UiDebugClipBoardWatch(QObject):

    @staticmethod
    def install_on_table(table: QTableWidget):
        """ Installs click handlers on the table's cells and headers to copy the cell's value or the header's label to the clipboard """

        def item_clicked(item):
            if QApplication.keyboardModifiers() & Qt.ControlModifier:
                ctrl_c(item.text(), "Table cell value '{copied_value}' copied to clipboard [Table Cell Click]")

        def header_clicked(section):
            if QApplication.keyboardModifiers() & Qt.ControlModifier:
                header_text = table.horizontalHeaderItem(section).text()
                ctrl_c(header_text, "Header label '{copied_value}' copied to clipboard [Header Click]")

        table.itemClicked.connect(item_clicked)
        table.horizontalHeader().sectionClicked.connect(header_clicked)

    def eventFilter(self, watched, event: QEvent):
        if event.type() == QEvent.MouseButtonPress and QMouseEvent(event).modifiers() & Qt.ControlModifier:
            if watched.property("customName"):
                self._handle_custom_name_event(watched)
            elif isinstance(watched, QLineEdit):
                self._handle_line_edit_event(watched)
            elif isinstance(watched, QPushButton):
                self._handle_push_button_event(watched)
            elif isinstance(watched, QLabel):
                self._handle_label_event(watched)
            elif isinstance(watched, QHeaderView):
                self._handle_header_view_event(watched, event)
            elif isinstance(watched, QTabBar):
                self._handle_tab_bar_event(watched, event)
            elif not isinstance(watched, (QPushButton, QLabel, QTabBar, QWidget, QWindow)):
                self._handle_default_event(watched)
            # else:
            #     print(f"'{watched}' event not handled by ClassNameCopyEventFilter")
        return super().eventFilter(watched, event)

    @staticmethod
    def _handle_custom_name_event(watched):
        ctrl_c(watched.property("customName"), "Custom Name '{copied_value}' copied to clipboard [" + CUSTOM_NAME_PROPERTY + "]")

    @staticmethod
    def _handle_line_edit_event(watched: QLineEdit):
        if watched.placeholderText():  # Check if the QLineEdit has a placeholder text set
            ctrl_c(watched.placeholderText(), "Placeholder text '{copied_value}' copied to clipboard [QLineEdit Click]")
        elif watched.text():
            ctrl_c(watched.text(), "Text '{copied_value}' copied to clipboard [QLineEdit Click]")
        else:
            print(f"QLineEdit clicked, but no text or placeholder to copy. Consider defining custom property '{CUSTOM_NAME_PROPERTY}'")

    @staticmethod
    def _handle_push_button_event(watched):
        ctrl_c(watched.text(), "Button text '{copied_value}' copied to clipboard [Button Click]")

    @staticmethod
    def _handle_label_event(watched):
        ctrl_c(watched.text(), "Label text '{copied_value}' copied to clipboard [Label Click]")

    @staticmethod
    def _handle_header_view_event(watched, event):
        if isinstance(watched.parent(), QTableWidget):
            table = watched.parent()
            column = watched.logicalIndexAt(event.pos())
            cell = table.horizontalHeaderItem(column)
            ctrl_c(cell.text(), "Column Name '{copied_value}' copied to clipboard [Header Click]")
        else:
            ctrl_c("QHeaderView", "Class Name '{copied_value}' copied to clipboard [Header Click]")

    @staticmethod
    def _handle_tab_bar_event(watched, event):
        tab_widget = watched.parent()
        if isinstance(tab_widget, QTabWidget):
            tab_index = watched.tabAt(event.pos())
            if tab_index != -1:
                widget = tab_widget.widget(tab_index)
                if widget:
                    # Check if the widget is of a generic type and prefer the tab's title if so
                    class_name = widget.__class__.__name__
                    if class_name in ["QWidget", "QFrame", "QScrollArea"]:
                        tab_title = tab_widget.tabText(tab_index)
                        ctrl_c(tab_title, "Tab Title '{copied_value}' copied to clipboard [Tab Click]")
                    else:
                        ctrl_c(class_name, "Class Name '{copied_value}' copied to clipboard [Tab Click]")

    @staticmethod
    def _handle_default_event(watched):
        ctrl_c(watched.__class__.__name__, "Class Name '{copied_value}' copied to clipboard [Other Click]")
