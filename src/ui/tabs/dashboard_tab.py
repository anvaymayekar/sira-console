"""Dashboard tab for SIRA Console."""

from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QPushButton,
    QButtonGroup,
)
from PyQt5.QtCore import Qt
from src.widgets import CameraView, SensorDisplay, RemoteControl, TelemetryLogsWidget


class DashboardTab(QWidget):
    """Dashboard tab containing camera, sensors, and telemetry."""

    def __init__(self, parent=None):
        """
        Initialize dashboard tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._current_widget = 0  # 0: sensors, 1: remote
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)

        # Left side: Camera view (2 parts width)
        self.camera_view = CameraView()

        # Right side: Vertical splitter (1 part width)
        right_splitter = QSplitter(Qt.Vertical)

        # Top right: Sensor/Remote toggle widget (2 parts height)
        toggle_widget = QWidget()
        toggle_layout = QVBoxLayout(toggle_widget)
        toggle_layout.setContentsMargins(8, 8, 8, 8)
        toggle_layout.setSpacing(8)

        # Toggle buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)

        self.sensors_btn = QPushButton("Sensors")
        self.sensors_btn.setCheckable(True)
        self.sensors_btn.setChecked(True)

        self.remote_btn = QPushButton("Remote Control")
        self.remote_btn.setCheckable(True)

        # Button group for exclusive selection
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.sensors_btn, 0)
        self.button_group.addButton(self.remote_btn, 1)
        self.button_group.buttonClicked[int].connect(self._toggle_widget)

        button_layout.addWidget(self.sensors_btn)
        button_layout.addWidget(self.remote_btn)

        toggle_layout.addLayout(button_layout)

        # Widget container
        self.sensor_display = SensorDisplay()
        self.remote_control = RemoteControl()
        self.remote_control.hide()

        toggle_layout.addWidget(self.sensor_display, 1)
        toggle_layout.addWidget(self.remote_control, 1)

        # Bottom right: Telemetry logs (1 part height)
        self.telemetry_logs = TelemetryLogsWidget()

        # Add to right splitter
        right_splitter.addWidget(toggle_widget)
        right_splitter.addWidget(self.telemetry_logs)
        right_splitter.setStretchFactor(0, 2)
        right_splitter.setStretchFactor(1, 1)

        # Add to main splitter
        main_splitter.addWidget(self.camera_view)
        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 1)

        layout.addWidget(main_splitter)

        self.setLayout(layout)

    def _toggle_widget(self, button_id: int) -> None:
        """
        Toggle between sensor and remote control widgets.

        Args:
            button_id: Button ID (0: sensors, 1: remote)
        """
        self._current_widget = button_id

        if button_id == 0:
            self.sensor_display.show()
            self.remote_control.hide()
        else:
            self.sensor_display.hide()
            self.remote_control.show()
