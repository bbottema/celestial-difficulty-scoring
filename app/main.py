import logging

import injector

from config.auto_wire import auto_wire
from database import initialize_database
from ui.main_window.main_window import MainWindow

logging.basicConfig(level=logging.DEBUG)

injector = injector.Injector()

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    auto_wire('app')

    initialize_database()

    app = QApplication(sys.argv)
    window = injector.get(MainWindow)
    window.show()
    sys.exit(app.exec())
