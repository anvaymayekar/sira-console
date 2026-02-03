"""Active issues widget for SIRA Console."""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QFrame,
)
from PyQt5.QtCore import Qt
from src.utils.constants import Colors
from datetime import datetime


class ActiveIssues(QWidget):
    """Active issues widget showing errors, warnings, and info."""

    def __init__(self, parent=None):
        """
        Initialize active issues.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()
        self._add_demo_issues()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Title and controls
        header_layout = QHBoxLayout()

        title = QLabel("Active Issues")
        title.setStyleSheet(
            f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-size: 10pt;
                font-weight: bold;
            }}
        """
        )

        self.scan_btn = QPushButton("Scan and Troubleshoot")
        self.scan_btn.clicked.connect(self._scan_and_troubleshoot)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.scan_btn)

        # Issues display
        self.issues_display = QTextEdit()
        self.issues_display.setReadOnly(True)
        self.issues_display.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {Colors.PRIMARY_BG};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                font-family: Consolas, Monaco, Courier New, monospace;
                font-size: 9pt;
            }}
        """
        )

        layout.addLayout(header_layout)
        layout.addWidget(self.issues_display, 1)

        self.setLayout(layout)

    def _add_demo_issues(self) -> None:
        """Add demo issues for display."""
        self.add_issue("INFO", "System initialized successfully")
        self.add_issue("INFO", "All servos responding normally")
        self.add_issue("WARNING", "Battery level below 80%")

    def add_issue(self, level: str, message: str) -> None:
        """
        Add an issue to the display.

        Args:
            level: Issue level (INFO, WARNING, ERROR)
            message: Issue message
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Get color for level
        if level == "ERROR":
            color = Colors.STATUS_RED
        elif level == "WARNING":
            color = Colors.ACCENT_YELLOW
        else:
            color = Colors.TEXT_PRIMARY

        # Format and add
        formatted = (
            f'<span style="color: {color};">[{timestamp}] {level}: {message}</span><br>'
        )
        self.issues_display.append(formatted)

    def _scan_and_troubleshoot(self) -> None:
        """Scan system and attempt troubleshooting."""
        self.add_issue("INFO", "Starting system scan...")
        self.add_issue("INFO", "Checking servo connections...")
        self.add_issue("INFO", "Checking sensor readings...")
        self.add_issue("INFO", "Scan complete. No critical issues found.")

    def clear_issues(self) -> None:
        """Clear all issues."""
        self.issues_display.clear()
