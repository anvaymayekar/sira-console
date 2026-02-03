"""Status bar component for SIRA Console."""

from PyQt5.QtWidgets import QStatusBar, QLabel
from PyQt5.QtCore import Qt
from src.utils.constants import MovementStatus, Colors


class CustomStatusBar(QStatusBar):
    """Custom status bar widget."""

    def __init__(self, parent=None):
        """
        Initialize status bar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Left: Movement status
        self.movement_label = QLabel("Ready")
        self.movement_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; padding: 0 10px;"
        )
        self.addWidget(self.movement_label)

        # Right: FPS and Latency
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; padding: 0 10px;"
        )
        self.addPermanentWidget(self.fps_label)

        self.latency_label = QLabel("Latency: 0ms")
        self.latency_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; padding: 0 10px;"
        )
        self.addPermanentWidget(self.latency_label)

    def set_movement_status(self, status: MovementStatus) -> None:
        """
        Set movement status.

        Args:
            status: Movement status enum
        """
        text = status.value
        color = (
            Colors.STATUS_GREEN
            if status == MovementStatus.WALKING
            else Colors.TEXT_SECONDARY
        )

        self.movement_label.setText(text)
        self.movement_label.setStyleSheet(f"color: {color}; padding: 0 10px;")

    def set_fps(self, fps: int) -> None:
        """
        Set FPS value.

        Args:
            fps: Frames per second
        """
        self.fps_label.setText(f"FPS: {fps}")

    def set_latency(self, latency: int) -> None:
        """
        Set latency value.

        Args:
            latency: Latency in milliseconds
        """
        self.latency_label.setText(f"Latency: {latency}ms")
