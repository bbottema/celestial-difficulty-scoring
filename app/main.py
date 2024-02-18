import logging.config
import os
from pathlib import Path

from config.auto_wire import auto_wire, injector
from database import initialize_database
from ui.main_window.main_window import MainWindow

logging.config.fileConfig(Path(os.path.dirname(__file__)) / 'logging.ini', disable_existing_loggers=False)
logging.getLogger(__name__).info("Logging configuration loaded")

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    auto_wire('app')

    initialize_database()

    app = QApplication(sys.argv)
    window = injector.get(MainWindow)
    window.show()
    sys.exit(app.exec())
