"""Signal indicator component for SIRA Console."""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from src.utils.constants import ConnectionStatus, Colors
from src.ui.styles import get_status_indicator_style


class SignalIndicator(QWidget):
    """Signal indicator widget showing connection status."""

    def __init__(self, parent=None):
        """
        Initialize signal indicator.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._status = ConnectionStatus.DISCONNECTED
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(8)

        # Status indicator dot
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(10, 10)
        self.status_dot.setStyleSheet(
            get_status_indicator_style(Colors.STATUS_GRAY, 10)
        )

        # Status text
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")

        layout.addWidget(self.status_dot)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.setLayout(layout)

    def set_status(self, status: ConnectionStatus) -> None:
        """
        Set connection status.

        Args:
            status: Connection status enum
        """
        self._status = status

        if status == ConnectionStatus.CONNECTED:
            color = Colors.STATUS_GREEN
            text = "Connected"
        elif status == ConnectionStatus.ERROR:
            color = Colors.STATUS_RED
            text = "Error"
        else:
            color = Colors.STATUS_GRAY
            text = "Disconnected"

        self.status_dot.setStyleSheet(get_status_indicator_style(color, 10))
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color};")
