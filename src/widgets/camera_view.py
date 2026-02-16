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
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QFont, QColor
from src.utils.constants import Colors
import numpy as np
import cv2
from src.network import SocketClient
from src.core.media_manager import MediaManager
from datetime import datetime


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
        self._current_frame: Optional[np.ndarray] = None
        self._recording_start_time: Optional[datetime] = None
        self._recording_blink_state = False
        self._blink_opacity = 255  # For fade effect
        self._blink_direction = -1  # -1 for fading out, 1 for fading in
        self._setup_ui()

        # Timer for updating recording duration display
        self._recording_timer = QTimer()
        self._recording_timer.timeout.connect(self._update_recording_display)

        # Timer for updating timestamp display (even when not recording)
        self._timestamp_timer = QTimer()
        self._timestamp_timer.timeout.connect(self._update_timestamp_display)
        self._timestamp_timer.start(50)  # Update every 50ms for milliseconds

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
        self.record_btn.setMinimumWidth(90)
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
        self.resolution_combo.setCurrentIndex(0)
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

    def _get_scaled_font_size(self, width: int, base_size: int = 11) -> int:
        """
        Get font size scaled to resolution.

        Args:
            width: Frame width
            base_size: Base font size for 640px width

        Returns:
            Scaled font size
        """
        # Scale based on width (640px = base, 1280px = 2x, 1920px = 3x)
        scale = width / 640.0
        return int(base_size * scale)

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
                    self._recording_start_time = datetime.now()
                    self._blink_opacity = 255
                    self._blink_direction = -1
                    self._recording_timer.start(50)  # Update every 50ms for smooth fade

                    self.record_btn.setText("Stop")
                    self.record_btn.setStyleSheet(
                        f"""
                        QPushButton {{
                            background-color: {Colors.STATUS_RED};
                            color: {Colors.TEXT_PRIMARY};
                        }}
                    """
                    )
                    # Redraw frame to show recording indicator
                    if self._current_frame is not None:
                        self._display_frame(self._current_frame)
                else:
                    self.record_btn.setChecked(False)
            else:
                print("No frame available to start recording")
                self.record_btn.setChecked(False)
        else:
            # Stop recording
            self.media_manager.stop_recording()
            self._recording = False
            self._recording_start_time = None
            self._recording_timer.stop()

            self.record_btn.setText("Record")
            self.record_btn.setStyleSheet("")

            # Redraw frame to remove recording indicator
            if self._current_frame is not None:
                self._display_frame(self._current_frame)

    def _update_recording_display(self) -> None:
        """Update the display to show current recording duration."""
        if self._recording and self._current_frame is not None:
            # Update fade effect
            self._blink_opacity += self._blink_direction * 15

            # Reverse direction at limits
            if self._blink_opacity <= 80:
                self._blink_opacity = 80
                self._blink_direction = 1
            elif self._blink_opacity >= 255:
                self._blink_opacity = 255
                self._blink_direction = -1

            self._display_frame(self._current_frame)

    def _update_timestamp_display(self) -> None:
        """Update timestamp display (even when not recording)."""
        if self._current_frame is not None:
            self._display_frame(self._current_frame)

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
            resolution: Resolution string (e.g., "1280x720")
        """
        if not self.socket_client or not self.socket_client.is_connected():
            print("Not connected - cannot change resolution")
            return

        # Send command to Pi
        command = {"type": "set_resolution", "resolution": resolution}

        print(f"Sending resolution change command: {resolution}")
        self.socket_client.send_command(command)

    def _change_fps(self, fps: str) -> None:
        """
        Change camera FPS.

        Args:
            fps: FPS string
        """
        self._current_fps = int(fps)

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

        # Display frame (will be called by timer for timestamp updates)

    def _get_recording_duration(self) -> str:
        """
        Get formatted recording duration.

        Returns:
            Duration string in format HH:MM:SS
        """
        if not self._recording_start_time:
            return "00:00:00"

        elapsed = datetime.now() - self._recording_start_time
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp with milliseconds.

        Returns:
            Timestamp string in format "DD Mon YYYY HH:MM:SS:MS"
        """
        now = datetime.now()
        return now.strftime("%d %b %Y %H:%M:%S") + f":{now.microsecond // 10000:02d}"

    def _display_frame(self, frame: np.ndarray):
        """
        Display frame on screen with overlays.

        Args:
            frame: BGR frame to display
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # dynamic font size
        w = frame.shape[1]  # Get frame width
        timestamp_size = self._get_scaled_font_size(w, base_size=8)
        duration_size = self._get_scaled_font_size(w, base_size=10)
        rec_size = self._get_scaled_font_size(w, base_size=7)
        dot_size = self._get_scaled_font_size(w, base_size=18)

        # Create painter for overlays
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw grid if enabled
        if self._show_grid:
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

        # Draw recording indicator if recording
        # if self._recording:
        #     margin = 15

        #     # Recording dot with fade effect
        #     painter.setBrush(QColor(255, 0, 0, self._blink_opacity))
        #     painter.setPen(Qt.NoPen)
        #     painter.drawEllipse(margin, margin, dot_size, dot_size)

        #     # Recording timer (aligned with dot)
        #     duration = self._get_recording_duration()
        #     font = QFont("Consolas", duration_size, QFont.Bold)
        #     painter.setFont(font)

        #     # Measure text for proper alignment
        #     fm = painter.fontMetrics()
        #     text_height = fm.height()
        #     text_width = fm.horizontalAdvance(duration)

        #     # Position text vertically centered with dot
        #     text_x = margin + dot_size + 10
        #     text_y = margin + (dot_size - text_height) // 2 + fm.ascent()

        #     # Draw text background (semi-transparent black)
        #     bg_padding = 5
        #     bg_rect = fm.boundingRect(duration)
        #     bg_rect.moveTopLeft(
        #         painter.transform().map(
        #             painter.worldTransform()
        #             .inverted()[0]
        #             .map(
        #                 painter.deviceTransform().map(
        #                     painter.transform().map(
        #                         painter.worldTransform().map(
        #                             painter.deviceTransform()
        #                             .inverted()[0]
        #                             .map(QPixmap().rect().topLeft())
        #                         )
        #                     )
        #                 )
        #             )
        #         )
        #     )
        #     bg_x = text_x - bg_padding
        #     bg_y = margin - bg_padding
        #     bg_w = text_width + bg_padding * 2
        #     bg_h = dot_size + bg_padding * 2

        #     # Draw text (white)
        #     painter.setPen(QColor(255, 255, 255))
        #     painter.drawText(text_x, text_y, duration)

        #     # "REC" text below
        #     rec_font = QFont("Consolas", rec_size, QFont.Bold)
        #     painter.setFont(rec_font)
        #     rec_y = margin + dot_size + 15
        #     painter.drawText(margin + dot_size + 10, rec_y, "REC")

        if self._recording:
            # Scale all values based on resolution
            scale = w / 640.0
            margin = int(15 * scale)

            # Recording dot with fade effect
            painter.setBrush(QColor(255, 0, 0, self._blink_opacity))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(margin, int(margin * 1.6), dot_size, dot_size)

            # Recording timer (aligned with dot)
            duration = self._get_recording_duration()
            font = QFont("Consolas", duration_size, QFont.Bold)
            painter.setFont(font)

            # Measure text for proper alignment
            fm = painter.fontMetrics()
            text_height = fm.height()

            # Position text vertically centered with dot
            text_x = margin + dot_size + int(10 * scale)
            text_y = margin + (dot_size + fm.ascent()) // 2

            # Draw text (white)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(text_x, text_y, duration)

            # "REC" text below
            rec_font = QFont("Consolas", rec_size, QFont.Bold)
            painter.setFont(rec_font)
            rec_y = margin + dot_size + int(15 * scale)
            painter.drawText(text_x, rec_y, "REC")

        # Draw timestamp (bottom-right corner) - ALWAYS visible
        timestamp = self._get_current_timestamp()
        timestamp_font = QFont("Consolas", timestamp_size, QFont.Normal)
        painter.setFont(timestamp_font)

        fm = painter.fontMetrics()
        timestamp_width = fm.horizontalAdvance(timestamp)
        timestamp_height = fm.height()

        # Position in bottom-right
        ts_margin = 10
        ts_x = w - timestamp_width - ts_margin - 10
        ts_y = h - ts_margin - 5

        # Draw timestamp text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(ts_x, ts_y, timestamp)

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
                self._recording_start_time = None
                self._recording_timer.stop()
                self.record_btn.setChecked(False)
                self.record_btn.setText("Record")
                self.record_btn.setStyleSheet("")
