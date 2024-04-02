from pathlib import Path

from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

PACKAGE_DIR = Path(__file__).parent.parent
PROJECT_DIR = PACKAGE_DIR.parent.parent
RESOURCES_DIR = PROJECT_DIR / 'resources'


def apply_theme(app: QApplication):
    extra = {
        # Button colors
        'danger': '#dc3545',
        'warning': '#ffc107',
        'success': '#17a2b8',
        'font_family': 'Roboto',
        'density_scale': '-1',
        'button_shape': 'default'
    }

    apply_stylesheet(app, theme=str(RESOURCES_DIR / 'celestial-theme.xml'), extra=extra)
