"""System health widget for SIRA Console."""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QGridLayout,
    QFrame,
    QScrollArea,
)
from PyQt5.QtCore import Qt, QTimer
from src.utils.constants import Colors
import random


class HealthMetric(QWidget):
    """Individual health metric widget."""

    def __init__(self, name: str, parent=None):
        """
        Initialize health metric.

        Args:
            name: Metric name
            parent: Parent widget
        """
        super().__init__(parent)
        self.name = name
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)

        # Name label
        self.name_label = QLabel(self.name)
        self.name_label.setFixedWidth(150)
        self.name_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(100)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid {Colors.BORDER};
                border-radius: 2px;
                text-align: center;
                background-color: {Colors.PANEL_BG};
                color: {Colors.SECONDARY_BG};

            }}
            QProgressBar::chunk {{
                background-color: {Colors.STATUS_GREEN};

            }}
        """
        )

        # Status label
        self.status_label = QLabel("OK")
        self.status_label.setFixedWidth(80)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"color: {Colors.STATUS_GREEN};")

        layout.addWidget(self.name_label)
        layout.addWidget(self.progress, 1)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def set_value(self, value: int) -> None:
        """
        Set health metric value.

        Args:
            value: Health value (0-100)
        """
        self.progress.setValue(value)

        # Update color and status
        if value >= 80:
            color = Colors.STATUS_GREEN
            status = "OK"
            chunk_color = Colors.STATUS_GREEN
        elif value >= 50:
            color = Colors.ACCENT_YELLOW
            status = "Warning"
            chunk_color = Colors.ACCENT_YELLOW
        else:
            color = Colors.STATUS_RED
            status = "Critical"
            chunk_color = Colors.STATUS_RED

        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"color: {color};")

        self.progress.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid {Colors.BORDER};
                border-radius: 2px;
                text-align: center;
                background-color: {Colors.PANEL_BG};
                color: {Colors.SECONDARY_BG};
            }}
            QProgressBar::chunk {{
                background-color: {chunk_color};
            }}
        """
        )


class SystemHealth(QWidget):
    """System health widget showing all health metrics."""

    def __init__(self, parent=None):
        """
        Initialize system health.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._metrics = []
        self._setup_ui()
        self._start_updates()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Title
        title = QLabel("System Health")
        title.setStyleSheet(
            f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-size: 10pt;
                font-weight: bold;
            }}
        """
        )

        # Scroll area for metrics
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # Container for metrics
        container = QWidget()
        container.setObjectName("HealthContainer")
        container.setAttribute(Qt.WA_StyledBackground, True)

        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(4)

        # Add health metrics
        metrics_config = [
            "Power System",
            "Communication",
            "Servo Controller",
            "IMU Sensor",
            "Distance Sensors",
            "Environment Sensors",
            "CPU Load",
            "Memory Usage",
            "Servo Health (FL)",
            "Servo Health (FR)",
            "Servo Health (ML)",
            "Servo Health (MR)",
            "Servo Health (RL)",
            "Servo Health (RR)",
        ]

        for metric_name in metrics_config:
            metric = HealthMetric(metric_name)
            self._metrics.append(metric)
            container_layout.addWidget(metric)

        container_layout.addStretch()

        scroll.setWidget(container)

        layout.addWidget(title)
        layout.addWidget(scroll, 1)

        self.setLayout(layout)

    def _start_updates(self) -> None:
        """Start periodic health updates."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_metrics)
        self.update_timer.start(2000)  # Update every 2 seconds

    def _update_metrics(self) -> None:
        """Update health metrics with simulated data."""
        for metric in self._metrics:
            # Simulate health values
            current = metric.progress.value()
            change = random.randint(-5, 3)
            new_value = max(70, min(100, current + change))
            metric.set_value(new_value)
