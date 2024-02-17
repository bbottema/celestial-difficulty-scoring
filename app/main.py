import logging

from database import initialize_database
from app.ui.main_window.main_window import MainWindow

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    initialize_database()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
