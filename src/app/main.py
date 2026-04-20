"""
BTL1-3 application bootstrap.
"""
import sys
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.app import config


def run_app() -> None:
    """Configure Qt/OpenGL defaults and start the main window."""
    fmt = QSurfaceFormat()
    fmt.setSamples(config.MSAA_SAMPLES)
    QSurfaceFormat.setDefaultFormat(fmt)

    app = QApplication(sys.argv)
    app.setStyle(config.UI_STYLE)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

