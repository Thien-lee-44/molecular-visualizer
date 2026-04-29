"""
Handles Qt application initialization and main window execution.
"""
import sys
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.app import config


def run_app() -> None:
    """
    Configures Qt/OpenGL defaults, initializes the application loop, 
    and displays the main window.
    """
    # Setup OpenGL format based on configuration
    fmt = QSurfaceFormat()
    fmt.setSamples(config.MSAA_SAMPLES)
    QSurfaceFormat.setDefaultFormat(fmt)

    # Initialize QApplication
    app = QApplication(sys.argv)
    app.setStyle(config.UI_STYLE)

    # Boot main interface
    window = MainWindow()
    window.show()
    sys.exit(app.exec())