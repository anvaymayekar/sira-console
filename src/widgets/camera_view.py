"""Camera view widget for SIRA Console."""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QRadioButton,
    QLabel,
    QComboBox,
    QFrame,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from src.utils.constants import Colors
import numpy as np


class CameraView(QWidget):
    """Camera view widget with controls."""

    def __init__(self, parent=None):
        """
        Initialize camera view.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._recording = False
        self._show_grid = False
        self._current_fps = 30
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Camera display area
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {Colors.PRIMARY_BG};
                border: 1px solid {Colors.BORDER};
            }}
        """
        )
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setText("No Camera Feed")

        # Control bar
        control_bar = QFrame()
        control_bar.setStyleSheet(
            f"""
            QFrame {{
                background-color: {Colors.SECONDARY_BG};
                border: 1px solid {Colors.BORDER};
                border-top: none;
            }}
        """
        )
        control_layout = QHBoxLayout(control_bar)
        control_layout.setContentsMargins(10, 8, 10, 8)

        # Left controls
        self.record_btn = QPushButton("Record")
        self.record_btn.setCheckable(True)
        self.record_btn.clicked.connect(self._toggle_recording)

        self.snapshot_btn = QPushButton("Snapshot")
        self.snapshot_btn.clicked.connect(self._take_snapshot)

        self.grid_check = QRadioButton("Grid")
        self.grid_check.toggled.connect(self._toggle_grid)

        control_layout.addWidget(self.record_btn)
        control_layout.addWidget(self.snapshot_btn)
        control_layout.addWidget(self.grid_check)
        control_layout.addStretch()

        # Right controls
        resolution_label = QLabel("Resolution:")
        resolution_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["640x480", "1280x720", "1920x1080"])
        self.resolution_combo.setCurrentIndex(1)
        self.resolution_combo.currentTextChanged.connect(self._change_resolution)

        fps_label = QLabel("FPS:")
        fps_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")

        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["15", "30", "60"])
        self.fps_combo.setCurrentIndex(1)
        self.fps_combo.currentTextChanged.connect(self._change_fps)

        control_layout.addWidget(resolution_label)
        control_layout.addWidget(self.resolution_combo)
        control_layout.addWidget(fps_label)
        control_layout.addWidget(self.fps_combo)

        layout.addWidget(self.camera_label, 1)
        layout.addWidget(control_bar)

        self.setLayout(layout)

        # Setup demo timer
        self._demo_timer = QTimer()
        self._demo_timer.timeout.connect(self._update_demo_frame)
        self._demo_timer.start(33)  # ~30 FPS

    def _toggle_recording(self, checked: bool) -> None:
        """
        Toggle recording state.

        Args:
            checked: Recording state
        """
        self._recording = checked
        if checked:
            self.record_btn.setText("Stop")
            self.record_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {Colors.STATUS_RED};
                    color: {Colors.TEXT_PRIMARY};
                }}
            """
            )
        else:
            self.record_btn.setText("Record")
            self.record_btn.setStyleSheet("")

    def _take_snapshot(self) -> None:
        """Take a snapshot of current frame."""
        pass  # Placeholder for snapshot functionality

    def _toggle_grid(self, checked: bool) -> None:
        """
        Toggle grid overlay.

        Args:
            checked: Grid state
        """
        self._show_grid = checked

    def _change_resolution(self, resolution: str) -> None:
        """
        Change camera resolution.

        Args:
            resolution: Resolution string
        """
        pass  # Placeholder for resolution change

    def _change_fps(self, fps: str) -> None:
        """
        Change camera FPS.

        Args:
            fps: FPS string
        """
        self._current_fps = int(fps)

    def _update_demo_frame(self) -> None:
        """Update demo frame with placeholder content."""
        # Create a demo frame
        width, height = 640, 480
        image = np.zeros((height, width, 3), dtype=np.uint8)

        # Add some pattern
        image[::20, :] = [30, 30, 30]
        image[:, ::20] = [30, 30, 30]

        # Convert to QPixmap
        h, w, ch = image.shape
        bytes_per_line = ch * w
        q_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # Draw grid if enabled
        if self._show_grid:
            painter = QPainter(pixmap)
            pen = QPen(Qt.white)
            pen.setWidth(1)
            painter.setPen(pen)

            # Draw 3x3 grid
            for i in range(1, 3):
                x = w * i // 3
                painter.drawLine(x, 0, x, h)
            for i in range(1, 3):
                y = h * i // 3
                painter.drawLine(0, y, w, y)
            painter.end()

        self.camera_label.setPixmap(
            pixmap.scaled(
                self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
