from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class MultiSelectDropdownExample(QMainWindow):
    def __init__(self):
        super().__init__()

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # List widget for multiselect
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)

        # Populate the list widget with items and checkboxes
        for i in range(10):  # Example item count
            item = QListWidgetItem(f"Item {i + 1}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Enable checkbox
            item.setCheckState(Qt.Unchecked)  # Set initial state
            self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)


if __name__ == "__main__":
    app = QApplication([])
    window = MultiSelectDropdownExample()
    window.show()
    app.exec()