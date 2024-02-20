import sys

from PySide6.QtWidgets import QApplication

from config.autowire import auto_wire, injector
from config.database import initialize_database
from config.init_logging import configure_logging
from ui.main_window.main_window import MainWindow
from utils.gui_helper import configure_close_signal_handler

if __name__ == '__main__':
    configure_logging(__file__)
    initialize_database()
    configure_close_signal_handler()
    auto_wire('app')

    app = QApplication(sys.argv)
    window = injector.get(MainWindow)
    window.show()
    sys.exit(app.exec())
