"""Diagnostics tab for SIRA Console."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt5.QtCore import Qt
from src.widgets import SystemHealth, ActiveIssues


class DiagnosticsTab(QWidget):
    """Diagnostics tab containing system health and active issues."""

    def __init__(self, parent=None):
        """
        Initialize diagnostics tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Vertical splitter
        splitter = QSplitter(Qt.Vertical)

        # System health widget
        self.system_health = SystemHealth()

        # Active issues widget
        self.active_issues = ActiveIssues()

        # Add to splitter
        splitter.addWidget(self.system_health)
        splitter.addWidget(self.active_issues)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

        self.setLayout(layout)
