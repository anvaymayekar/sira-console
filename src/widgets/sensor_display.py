"""Sensor display widget for SIRA Console."""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QGridLayout,
)
from PyQt5.QtCore import Qt
from src.utils.constants import Colors
from src.models.robot_state import SensorData
from src.utils.constants import Dimensions
from src.utils.constants import Fonts


class SensorDisplay(QWidget):
    """Sensor display widget showing robot sensor data."""

    def __init__(self, parent=None):
        """
        Initialize sensor display.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _imu_sub_label(self, sub: str) -> QLabel:
        label = QLabel(sub)
        label.setStyleSheet(
            f"color: {Colors.TEXT_DISABLED}; font-size:{Fonts.SIZE_SMALL}pt"
        )
        return label

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Set minimum width to match remote control
        self.setMinimumWidth(Dimensions.DASHBOARD_SIDEBAR)

        # Power section
        power_group = self._create_group("Power")
        power_layout = QGridLayout()
        power_layout.setColumnStretch(1, 1)

        self.battery_label = QLabel("0.0V")
        self.battery_label.setMinimumWidth(60)
        self.battery_pct_label = QLabel("0%")
        self.battery_pct_label.setMinimumWidth(50)

        power_layout.addWidget(QLabel("Battery:"), 0, 0)
        power_layout.addWidget(self.battery_label, 0, 1)
        power_layout.addWidget(self.battery_pct_label, 0, 2)

        power_group.setLayout(power_layout)

        # IMU section
        imu_group = self._create_group("IMU Orientation")
        imu_layout = QGridLayout()
        imu_layout.setColumnStretch(1, 1)

        self.imu_x_label = QLabel("0.0°")
        self.imu_x_label.setMinimumWidth(60)
        self.imu_y_label = QLabel("0.0°")
        self.imu_y_label.setMinimumWidth(60)
        self.imu_z_label = QLabel("0.0°")
        self.imu_z_label.setMinimumWidth(60)

        imu_layout.addWidget(QLabel("X:"), 0, 0)
        imu_layout.addWidget(self.imu_x_label, 0, 1)
        imu_layout.addWidget(self._imu_sub_label("roll"), 0, 2)
        imu_layout.addWidget(QLabel("Y:"), 1, 0)
        imu_layout.addWidget(self.imu_y_label, 1, 1)
        imu_layout.addWidget(self._imu_sub_label("pitch"), 1, 2)
        imu_layout.addWidget(QLabel("Z:"), 2, 0)
        imu_layout.addWidget(self.imu_z_label, 2, 1)
        imu_layout.addWidget(self._imu_sub_label("yaw"), 2, 2)

        imu_group.setLayout(imu_layout)

        # Environment section
        env_group = self._create_group("Environment")
        env_layout = QGridLayout()
        env_layout.setColumnStretch(1, 1)

        self.temp_label = QLabel("0.0°C")
        self.temp_label.setMinimumWidth(60)
        self.humidity_label = QLabel("0.0%")
        self.humidity_label.setMinimumWidth(60)

        env_layout.addWidget(QLabel("Temperature:"), 0, 0)
        env_layout.addWidget(self.temp_label, 0, 1)
        env_layout.addWidget(QLabel("Humidity:"), 1, 0)
        env_layout.addWidget(self.humidity_label, 1, 1)

        env_group.setLayout(env_layout)

        # Measurements section
        measure_group = self._create_group("Measurements")
        measure_layout = QGridLayout()
        measure_layout.setColumnStretch(1, 1)

        self.altitude_label = QLabel("0.0m")
        self.altitude_label.setMinimumWidth(60)

        self.ground_clearance_label = QLabel("0.0cm")
        self.ground_clearance_label.setMinimumWidth(60)
        self.distance_label = QLabel("0.0cm")
        self.distance_label.setMinimumWidth(60)

        measure_layout.addWidget(QLabel("Altitude:"), 0, 0)
        measure_layout.addWidget(self.altitude_label, 0, 1)
        measure_layout.addWidget(QLabel("Ground Clearance:"), 1, 0)
        measure_layout.addWidget(self.ground_clearance_label, 1, 1)
        measure_layout.addWidget(QLabel("Front Distance:"), 2, 0)
        measure_layout.addWidget(self.distance_label, 2, 1)

        measure_group.setLayout(measure_layout)

        # Add all groups
        layout.addWidget(power_group)
        layout.addWidget(imu_group)
        layout.addWidget(env_group)
        layout.addWidget(measure_group)
        layout.addStretch()

        self.setLayout(layout)

    def _create_group(self, title: str) -> QGroupBox:
        """
        Create a styled group box.

        Args:
            title: Group box title

        Returns:
            QGroupBox widget
        """
        group = QGroupBox(title)
        group.setStyleSheet(
            f"""
            QGroupBox {{
                border: 1px solid {Colors.BORDER};
                margin-top: 12px;
                padding-top: 12px;
                color: {Colors.TEXT_SECONDARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
            }}
        """
        )
        return group

    def update_sensor_data(self, data: SensorData) -> None:
        """
        Update sensor display with new data.

        Args:
            data: Sensor data object
        """
        self.battery_label.setText(f"{data.battery_voltage:.1f}V")
        self.battery_pct_label.setText(f"{data.battery_percentage:.0f}%")

        self.imu_x_label.setText(f"{data.imu_x:.1f}°")
        self.imu_y_label.setText(f"{data.imu_y:.1f}°")
        self.imu_z_label.setText(f"{data.imu_z:.1f}°")

        self.temp_label.setText(f"{data.temperature:.1f}°C")
        self.humidity_label.setText(f"{data.humidity:.1f}%")

        self.altitude_label.setText(f"{data.altitude:.1f}cm")
        self.distance_label.setText(f"{data.front_distance:.1f}cm")

        # Update colors based on values
        self._update_battery_color(data.battery_percentage)

    def _update_battery_color(self, percentage: float) -> None:
        """
        Update battery label color based on percentage.

        Args:
            percentage: Battery percentage
        """
        if percentage > 50:
            color = Colors.STATUS_GREEN
        elif percentage > 20:
            color = Colors.ACCENT_YELLOW
        else:
            color = Colors.STATUS_RED

        self.battery_pct_label.setStyleSheet(f"color: {color};")
