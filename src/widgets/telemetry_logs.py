"""Telemetry logs widget for SIRA Console."""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLineEdit,
    QCheckBox,
)
from typing import Optional
from src.network import SocketClient
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QTextCursor, QColor
from src.utils.constants import LogLevel, Colors
from src.models.telemetry import TelemetryLog


class TelemetryLogsWidget(QWidget):
    """Telemetry logs widget with search and controls."""

    def __init__(self, socket_client: Optional[SocketClient] = None, parent=None):
        """
        Initialize telemetry logs widget.

        Args:
            socket_client: Socket client for receiving telemetry
            parent: Parent widget
        """
        super().__init__(parent)
        self.socket_client = socket_client
        self.telemetry = TelemetryLog()
        self._auto_scroll = True
        self._setup_ui()

        # Connect to socket client if provided
        if self.socket_client:
            self.socket_client.telemetry_received.connect(self._on_telemetry_received)
            self.socket_client.connection_changed.connect(self._on_connection_changed)

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {Colors.PRIMARY_BG};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                font-family: Consolas, Monaco, Courier New, monospace;
                font-size: 8pt;
            }}
        """
        )

        # Search bar
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search logs...")
        self.search_input.textChanged.connect(self._on_search)

        self.auto_scroll_check = QCheckBox("Auto-scroll")
        self.auto_scroll_check.setChecked(True)
        self.auto_scroll_check.toggled.connect(self._toggle_auto_scroll)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.auto_scroll_check)

        # Control buttons
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_logs)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear_logs)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        layout.addWidget(self.log_display, 1)
        layout.addLayout(search_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Add some demo logs
        self._add_demo_logs()

    def _add_demo_logs(self) -> None:
        """Add demo log entries."""
        self.add_log(LogLevel.INFO, "System initialized successfully")
        self.add_log(LogLevel.INFO, "Waiting for connection...")

    def add_log(self, level: LogLevel, message: str) -> None:
        """
        Add a log entry.

        Args:
            level: Log level
            message: Log message
        """
        self.telemetry.add_entry(level, message)

        # Get color for level
        if level == LogLevel.ERROR:
            color = Colors.STATUS_RED
        elif level == LogLevel.WARNING:
            color = Colors.ACCENT_YELLOW
        else:
            color = Colors.TEXT_PRIMARY

        # Format and add to display
        entry = self.telemetry.get_entries()[-1]
        formatted = f'<span style="color: {color};">{entry.to_string()}</span><br>'

        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(formatted)

        # Auto scroll if enabled
        if self._auto_scroll:
            self.log_display.verticalScrollBar().setValue(
                self.log_display.verticalScrollBar().maximum()
            )

    def _on_search(self, query: str) -> None:
        """
        Handle search input.

        Args:
            query: Search query
        """
        if not query:
            self._display_all_logs()
            return

        # Search and display matching entries
        self.log_display.clear()
        matches = self.telemetry.search(query)

        for entry in matches:
            if entry.level == LogLevel.ERROR:
                color = Colors.STATUS_RED
            elif entry.level == LogLevel.WARNING:
                color = Colors.ACCENT_YELLOW
            else:
                color = Colors.TEXT_PRIMARY

            formatted = f'<span style="color: {color};">{entry.to_string()}</span><br>'
            cursor = self.log_display.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertHtml(formatted)

    def _display_all_logs(self) -> None:
        """Display all log entries."""
        self.log_display.clear()
        for entry in self.telemetry.get_entries():
            if entry.level == LogLevel.ERROR:
                color = Colors.STATUS_RED
            elif entry.level == LogLevel.WARNING:
                color = Colors.ACCENT_YELLOW
            else:
                color = Colors.TEXT_PRIMARY

            formatted = f'<span style="color: {color};">{entry.to_string()}</span><br>'
            cursor = self.log_display.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertHtml(formatted)

    def _toggle_auto_scroll(self, checked: bool) -> None:
        """
        Toggle auto-scroll.

        Args:
            checked: Auto-scroll state
        """
        self._auto_scroll = checked

    def _save_logs(self) -> None:
        """Save logs to file."""
        # Placeholder for save functionality
        self.add_log(LogLevel.INFO, "Logs saved to file")

    def _clear_logs(self) -> None:
        """Clear all logs."""
        self.telemetry.clear()
        self.log_display.clear()
        self.add_log(LogLevel.INFO, "Logs cleared")

    @pyqtSlot(dict)
    def _on_telemetry_received(self, data: dict):
        """
        Handle telemetry data from Pi.

        Args:
            data: Telemetry dictionary
        """
        # Log human detection
        if data.get("human_detected"):
            self.add_log(LogLevel.WARNING, "⚠ HUMAN DETECTED!")

        # Optionally log other data periodically
        # Uncomment if you want to see all telemetry:
        # battery = data.get('battery_voltage', 0)
        # temp = data.get('temperature', 0)
        # self.add_log(LogLevel.INFO, f"Battery: {battery:.2f}V, Temp: {temp:.1f}°C")

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool):
        """
        Handle connection state change.

        Args:
            connected: Connection state
        """
        if connected:
            self.add_log(LogLevel.INFO, "Connected to Hexapod")
        else:
            self.add_log(LogLevel.WARNING, "Disconnected from Hexapod")
