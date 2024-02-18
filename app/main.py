# import logging

# import injector

# from app.config.auto_wire import auto_wire
from database import initialize_database
# from app.ui.main_window.main_window import MainWindow

# logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    # auto_wire()

    initialize_database()

    app = QApplication(sys.argv)
    # window = injector.get(MainWindow)
    # window = MainWindow()
    # window.show()
    sys.exit(app.exec())
