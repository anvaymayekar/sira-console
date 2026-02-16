"""Camera view widget for SIRA Console."""

from typing import Optional
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
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from src.utils.constants import Colors
import numpy as np
import cv2
from src.network import SocketClient
from src.core.media_manager import MediaManager  # NEW IMPORT


class CameraView(QWidget):
    """Camera view widget with controls."""

    def __init__(
        self,
        socket_client: Optional[SocketClient] = None,
        media_manager: Optional[MediaManager] = None,
        parent=None,
    ):
        """
        Initialize camera view.

        Args:
            socket_client: Socket client for receiving frames
            media_manager: Media manager for recordings/snapshots
            parent: Parent widget
        """
        super().__init__(parent)
        self.socket_client = socket_client
        self.media_manager = media_manager
        self._recording = False
        self._show_grid = False
        self._current_fps = 30
        self._current_frame: Optional[np.ndarray] = None  # Store current frame
        self._setup_ui()

        # Connect to socket client
        if self.socket_client:
            self.socket_client.frame_received.connect(self._update_frame)
            self.socket_client.connection_changed.connect(self._on_connection_changed)

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
        resolution_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; border: none;")

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["640x480", "1280x720", "1920x1080"])
        self.resolution_combo.setCurrentIndex(1)
        self.resolution_combo.currentTextChanged.connect(self._change_resolution)

        fps_label = QLabel("FPS:")
        fps_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; border: none;")

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

    def _toggle_recording(self, checked: bool) -> None:
        """
        Toggle recording state.

        Args:
            checked: Recording state
        """
        if not self.media_manager:
            print("Media manager not available")
            self.record_btn.setChecked(False)
            return

        if checked:
            # Start recording
            if self._current_frame is not None:
                success = self.media_manager.start_recording(self._current_frame)
                if success:
                    self._recording = True
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
                    self.record_btn.setChecked(False)
            else:
                print("No frame available to start recording")
                self.record_btn.setChecked(False)
        else:
            # Stop recording
            self.media_manager.stop_recording()
            self._recording = False
            self.record_btn.setText("Record")
            self.record_btn.setStyleSheet("")

    def _take_snapshot(self) -> None:
        """Take a snapshot of current frame."""
        if not self.media_manager:
            print("Media manager not available")
            return

        if self._current_frame is not None:
            self.media_manager.take_snapshot(self._current_frame)
        else:
            print("No frame available for snapshot")

    def _toggle_grid(self, checked: bool) -> None:
        """
        Toggle grid overlay.

        Args:
            checked: Grid state
        """
        self._show_grid = checked
        # Redraw current frame with/without grid
        if self._current_frame is not None:
            self._display_frame(self._current_frame)

    def _change_resolution(self, resolution: str) -> None:
        """
        Change camera resolution.

        Args:
            resolution: Resolution string
        """
        # This would send command to Pi to change resolution
        # For now, just placeholder
        pass

    def _change_fps(self, fps: str) -> None:
        """
        Change camera FPS.

        Args:
            fps: FPS string
        """
        self._current_fps = int(fps)
        # This would send command to Pi to change FPS
        # For now, just placeholder

    @pyqtSlot(np.ndarray)
    def _update_frame(self, frame: np.ndarray):
        """
        Update camera view with received frame.

        Args:
            frame: BGR frame from Pi
        """
        # Store current frame
        self._current_frame = frame.copy()

        # Record frame if recording
        if self._recording and self.media_manager:
            self.media_manager.record_frame(frame)

        # Display frame
        self._display_frame(frame)

    def _display_frame(self, frame: np.ndarray):
        """
        Display frame on screen.

        Args:
            frame: BGR frame to display
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
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

    @pyqtSlot(bool)
    def _on_connection_changed(self, connected: bool):
        """
        Handle connection state change.

        Args:
            connected: Connection state
        """
        if not connected:
            self.camera_label.setText("No Camera Feed - Disconnected")
            self._current_frame = None

            # Stop recording if active
            if self._recording and self.media_manager:
                self.media_manager.stop_recording()
                self._recording = False
                self.record_btn.setChecked(False)
                self.record_btn.setText("Record")
                self.record_btn.setStyleSheet("")
