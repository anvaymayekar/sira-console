"""Servo matrix widget for SIRA Console."""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout,
    QSlider,
    QSpinBox,
    QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal
from src.utils.constants import Colors
from src.core.config_loader import ConfigLoader


class ServoControl(QWidget):
    """Individual servo control widget."""

    angle_changed = pyqtSignal(int)

    def __init__(
        self,
        joint_name: str,
        default_angle: int,
        min_angle: int,
        max_angle: int,
        safe_min: int,
        safe_max: int,
        parent=None,
    ):
        """
        Initialize servo control.

        Args:
            joint_name: Name of the joint
            default_angle: Default angle
            min_angle: Minimum angle
            max_angle: Maximum angle
            safe_min: Safe minimum angle
            safe_max: Safe maximum angle
            parent: Parent widget
        """
        super().__init__(parent)
        self.joint_name = joint_name
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.safe_min = safe_min
        self.safe_max = safe_max
        self._current_angle = default_angle
        self._test_mode = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Angle display
        self.angle_label = QLabel(f"{self._current_angle}°")
        self.angle_label.setAlignment(Qt.AlignCenter)
        self.angle_label.setStyleSheet(
            f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: 10pt;
                font-weight: bold;
                padding: 4px;
                background-color: {Colors.PANEL_BG};
                border: 1px solid {Colors.BORDER};
            }}
        """
        )

        # Slider (hidden by default)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(self.min_angle)
        self.slider.setMaximum(self.max_angle)
        self.slider.setValue(self._current_angle)
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.slider.hide()

        # Spin box (hidden by default)
        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(self.min_angle)
        self.spin_box.setMaximum(self.max_angle)
        self.spin_box.setValue(self._current_angle)
        self.spin_box.valueChanged.connect(self._on_spin_changed)
        self.spin_box.hide()

        layout.addWidget(self.angle_label)
        layout.addWidget(self.slider)
        layout.addWidget(self.spin_box)

        self.setLayout(layout)
        self._update_color()

    def set_test_mode(self, enabled: bool) -> None:
        """
        Enable or disable test mode.

        Args:
            enabled: Test mode state
        """
        self._test_mode = enabled

        if enabled:
            self.angle_label.hide()
            self.slider.show()
            self.spin_box.show()
            self.setStyleSheet("")
        else:
            self.angle_label.show()
            self.slider.hide()
            self.spin_box.hide()
            self.setStyleSheet("opacity: 0.6;")

    def set_angle(self, angle: int) -> None:
        """
        Set servo angle.

        Args:
            angle: Angle in degrees
        """
        self._current_angle = angle
        self.angle_label.setText(f"{angle}°")
        self.slider.blockSignals(True)
        self.spin_box.blockSignals(True)
        self.slider.setValue(angle)
        self.spin_box.setValue(angle)
        self.slider.blockSignals(False)
        self.spin_box.blockSignals(False)
        self._update_color()

    def get_angle(self) -> int:
        """
        Get current angle.

        Returns:
            Current angle
        """
        return self._current_angle

    def _on_slider_changed(self, value: int) -> None:
        """
        Handle slider value change.

        Args:
            value: New slider value
        """
        self._current_angle = value
        self.spin_box.blockSignals(True)
        self.spin_box.setValue(value)
        self.spin_box.blockSignals(False)
        self._update_color()
        self.angle_changed.emit(value)

    def _on_spin_changed(self, value: int) -> None:
        """
        Handle spin box value change.

        Args:
            value: New spin box value
        """
        self._current_angle = value
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        self._update_color()
        self.angle_changed.emit(value)

    def _update_color(self) -> None:
        """Update display color based on angle."""
        if self._current_angle < self.safe_min or self._current_angle > self.safe_max:
            color = Colors.STATUS_RED
        elif (
            self._current_angle < self.safe_min + 10
            or self._current_angle > self.safe_max - 10
        ):
            color = Colors.ACCENT_YELLOW
        else:
            color = Colors.STATUS_GREEN

        self.angle_label.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                font-size: 10pt;
                font-weight: bold;
                padding: 4px;
                background-color: {Colors.PANEL_BG};
                border: 1px solid {Colors.BORDER};
            }}
        """
        )


class ServoMatrix(QWidget):
    """Servo matrix widget showing all servo controls."""

    def __init__(self, config: ConfigLoader, parent=None):
        """
        Initialize servo matrix.

        Args:
            config: Configuration loader
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self._test_mode = False
        self._servo_controls = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Title
        title = QLabel("Servo Matrix")
        title.setStyleSheet(
            f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-size: 10pt;
                font-weight: bold;
            }}
        """
        )

        # Grid
        grid_frame = QFrame()
        grid_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {Colors.SECONDARY_BG};
                border: 1px solid {Colors.BORDER};
            }}
        """
        )
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setSpacing(8)

        # Get configuration
        limb_names = self.config.get_servo_param("limb_names", default=[])
        joint_names = self.config.get_servo_param("joint_names", default=[])
        servo_defaults = self.config.get_servo_param("servo_defaults", default={})

        # Add headers
        for col, limb_name in enumerate(limb_names):
            header = QLabel(limb_name)
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet(
                f"""
                QLabel {{
                    color: {Colors.TEXT_SECONDARY};
                    font-size: 9pt;
                    font-weight: bold;
                }}
            """
            )
            grid_layout.addWidget(header, 0, col + 1)

        # Add servo controls
        for row, joint_name in enumerate(joint_names):
            # Row header
            row_header = QLabel(joint_name)
            row_header.setStyleSheet(
                f"""
                QLabel {{
                    color: {Colors.TEXT_SECONDARY};
                    font-size: 9pt;
                    font-weight: bold;
                }}
            """
            )
            grid_layout.addWidget(row_header, row + 1, 0)

            # Get joint config
            joint_key = joint_name.lower()
            joint_config = servo_defaults.get(joint_key, {})

            default_angle = joint_config.get("default_angle", 0)
            min_angle = joint_config.get("min_angle", 0)
            max_angle = joint_config.get("max_angle", 180)
            safe_min = joint_config.get("safe_min", 10)
            safe_max = joint_config.get("safe_max", 170)

            # Create servo controls
            for col in range(6):
                servo = ServoControl(
                    joint_name, default_angle, min_angle, max_angle, safe_min, safe_max
                )
                self._servo_controls.append(servo)
                grid_layout.addWidget(servo, row + 1, col + 1)

        layout.addWidget(title)
        layout.addWidget(grid_frame, 1)

        self.setLayout(layout)

    def set_test_mode(self, enabled: bool) -> None:
        """
        Enable or disable test mode.

        Args:
            enabled: Test mode state
        """
        self._test_mode = enabled
        for servo in self._servo_controls:
            servo.set_test_mode(enabled)

    def set_servo_angle(self, limb: int, joint: int, angle: int) -> None:
        """
        Set angle for a specific servo.

        Args:
            limb: Limb index (0-5)
            joint: Joint index (0-2)
            angle: Angle in degrees
        """
        index = limb + joint * 6
        if 0 <= index < len(self._servo_controls):
            self._servo_controls[index].set_angle(angle)

    def get_servo_angle(self, limb: int, joint: int) -> int:
        """
        Get angle for a specific servo.

        Args:
            limb: Limb index (0-5)
            joint: Joint index (0-2)

        Returns:
            Servo angle
        """
        index = limb + joint * 6
        if 0 <= index < len(self._servo_controls):
            return self._servo_controls[index].get_angle()
        return 0

    def reset_all(self) -> None:
        """Reset all servos to default angles."""
        joint_names = self.config.get_servo_param("joint_names", default=[])
        servo_defaults = self.config.get_servo_param("servo_defaults", default={})

        for joint_idx, joint_name in enumerate(joint_names):
            joint_key = joint_name.lower()
            joint_config = servo_defaults.get(joint_key, {})
            default_angle = joint_config.get("default_angle", 0)

            for limb_idx in range(6):
                self.set_servo_angle(limb_idx, joint_idx, default_angle)
