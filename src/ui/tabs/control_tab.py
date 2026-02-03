"""Control tab for SIRA Console."""

from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QPushButton,
    QCheckBox,
    QLabel,
)
from PyQt5.QtCore import Qt
from src.widgets import PoseVisualizer, ServoMatrix
from src.core.config_loader import ConfigLoader
from src.utils.constants import Colors


class ControlTab(QWidget):
    """Control tab containing 3D visualization and servo matrix."""

    def __init__(self, config: ConfigLoader, parent=None):
        """
        Initialize control tab.

        Args:
            config: Configuration loader
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self._test_mode = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)

        # Left side: 3D Pose Visualizer (2 parts width)
        self.pose_visualizer = PoseVisualizer()

        # Right side: Servo Matrix with controls (1 part width)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(8)

        # Control header
        control_header = QWidget()
        control_layout = QHBoxLayout(control_header)
        control_layout.setContentsMargins(0, 0, 0, 0)

        # Test mode toggle
        test_label = QLabel("Test Mode:")
        test_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")

        self.test_switch = QCheckBox()
        self.test_switch.toggled.connect(self._toggle_test_mode)

        # Reset button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self._reset_servos)
        self.reset_btn.setEnabled(False)

        control_layout.addWidget(test_label)
        control_layout.addWidget(self.test_switch)
        control_layout.addStretch()
        control_layout.addWidget(self.reset_btn)

        # Servo matrix
        self.servo_matrix = ServoMatrix(self.config)

        # Info label
        info_label = QLabel(
            "Enable Test Mode to adjust servo angles manually.\n"
            "Values are shown in real-time when test mode is disabled."
        )
        info_label.setStyleSheet(
            f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                background-color: {Colors.PANEL_BG};
                padding: 8px;
                border: 1px solid {Colors.BORDER};
                font-size: 8pt;
            }}
        """
        )
        info_label.setWordWrap(True)

        right_layout.addWidget(control_header)
        right_layout.addWidget(self.servo_matrix, 1)
        right_layout.addWidget(info_label)

        # Add to main splitter
        main_splitter.addWidget(self.pose_visualizer)
        main_splitter.addWidget(right_widget)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 1)

        layout.addWidget(main_splitter)

        self.setLayout(layout)

    def _toggle_test_mode(self, checked: bool) -> None:
        """
        Toggle test mode.

        Args:
            checked: Test mode state
        """
        self._test_mode = checked
        self.servo_matrix.set_test_mode(checked)
        self.reset_btn.setEnabled(checked)

    def _reset_servos(self) -> None:
        """Reset all servos to default positions."""
        self.servo_matrix.reset_all()

    def get_test_mode(self) -> bool:
        """
        Get current test mode state.

        Returns:
            Test mode state
        """
        return self._test_mode
