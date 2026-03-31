import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QSurfaceFormat

# Import the main window from the interface module
from interface.main_window import MainWindow

# Ensure the working directory is set to the project root.
# This guarantees that relative paths to assets (models, shaders, JSON) resolve correctly.
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)


def main():
    """
    Main execution function.
    Sets up the application style, configures OpenGL properties, and displays the UI.
    """
    app = QApplication(sys.argv)
    
    # Apply a clean, cross-platform UI style
    app.setStyle("Fusion") 

    # Configure global OpenGL settings
    # Enable 8x Multisample Anti-Aliasing (MSAA) for smoother 3D rendering edges
    fmt = QSurfaceFormat()
    fmt.setSamples(8)
    QSurfaceFormat.setDefaultFormat(fmt)
    
    # Initialize and display the primary application window
    window = MainWindow()
    window.show()
    
    # Start the application's event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()