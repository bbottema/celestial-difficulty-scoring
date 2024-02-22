import sys

from PySide6.QtWidgets import *

from app.config.autowire import autowire, injector
from app.config.database import initialize_database
from app.config.init_logging import configure_logging
from app.ui.main_window.main_window import MainWindow
from app.utils.gui_helper import configure_close_signal_handler
from app.utils.ui_debug_clipboard_watch import configure_debug_clipboard_watch

if __name__ == '__main__':
    app = QApplication(sys.argv)

    configure_logging(__file__)
    initialize_database()
    configure_close_signal_handler()
    autowire('src')
    configure_debug_clipboard_watch(app)

    window = injector.get(MainWindow)
    window.show()
    sys.exit(app.exec())
