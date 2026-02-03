"""Application core for SIRA Console."""

import sys
from PyQt5.QtWidgets import QApplication
from src.core.config_loader import ConfigLoader
from src.ui.main_window import MainWindow


class Application:
    """Main application class."""

    def __init__(self):
        """Initialize the application."""
        self.config = ConfigLoader()
        self.config.load_all()

        self.app = QApplication(sys.argv)
        self.app.setApplicationName("SIRA Console")
        self.app.setOrganizationName("SIRA")

        self.main_window = MainWindow(self.config)

    def run(self) -> int:
        """
        Run the application.

        Returns:
            Exit code
        """
        self.main_window.show()
        return self.app.exec_()
