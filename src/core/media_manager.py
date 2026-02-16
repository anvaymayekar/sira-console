"""Media manager for recordings and snapshots."""

import os
from datetime import datetime
from typing import Optional
import cv2
import numpy as np
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal


class MediaManager(QObject):
    """Manages video recordings and snapshots."""

    # Signals
    snapshot_saved = pyqtSignal(str)  # Emits filepath when snapshot saved
    recording_started = pyqtSignal(str)  # Emits filepath when recording starts
    recording_stopped = pyqtSignal(str, int)  # Emits filepath and frame count
    error_occurred = pyqtSignal(str)  # Emits error message

    def __init__(self, config):
        """
        Initialize media manager.

        Args:
            config: ConfigLoader instance
        """
        super().__init__()
        self.config = config

        # Get paths from config
        self.recordings_path = Path(
            config.get_setting("media", "recordings_path", default="recordings")
        )
        self.snapshots_path = Path(
            config.get_setting("media", "snapshots_path", default="snapshots")
        )

        # Get settings
        self.recording_fps = config.get_setting("media", "recording_fps", default=30)
        self.recording_quality = config.get_setting(
            "media", "recording_quality", default=95
        )
        self.snapshot_format = config.get_setting(
            "media", "snapshot_format", default="png"
        )
        self.video_codec = config.get_setting("media", "video_codec", default="mp4v")

        # Create directories if they don't exist
        self._create_directories()

        # Recording state
        self.video_writer: Optional[cv2.VideoWriter] = None
        self.is_recording = False
        self.current_recording_path: Optional[Path] = None
        self.frame_count = 0
        self.frame_size = None  # Will be set from first frame

    def _create_directories(self) -> None:
        """Create media directories if they don't exist."""
        self.recordings_path.mkdir(parents=True, exist_ok=True)
        self.snapshots_path.mkdir(parents=True, exist_ok=True)
        print(f"Media directories ready:")
        print(f"  Recordings: {self.recordings_path.absolute()}")
        print(f"  Snapshots: {self.snapshots_path.absolute()}")

    def _generate_timestamp(self) -> str:
        """
        Generate timestamp for filenames.

        Returns:
            Timestamp string in format YYYYMMDD_HHMMSS
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def take_snapshot(self, frame: np.ndarray) -> Optional[str]:
        """
        Save a snapshot of the current frame.

        Args:
            frame: BGR frame from camera

        Returns:
            Path to saved snapshot or None if failed
        """
        if frame is None or frame.size == 0:
            error_msg = "Cannot take snapshot: invalid frame"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            return None

        try:
            timestamp = self._generate_timestamp()
            filename = f"snapshot_{timestamp}.{self.snapshot_format}"
            filepath = self.snapshots_path / filename

            # Save with high quality
            if self.snapshot_format.lower() == "png":
                cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            elif self.snapshot_format.lower() in ["jpg", "jpeg"]:
                cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
            else:
                cv2.imwrite(str(filepath), frame)

            print(f"Snapshot saved: {filepath}")
            self.snapshot_saved.emit(str(filepath))
            return str(filepath)

        except Exception as e:
            error_msg = f"Failed to save snapshot: {e}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            return None

    def start_recording(self, frame: np.ndarray) -> bool:
        """
        Start recording video.

        Args:
            frame: First frame to record (used to get dimensions)

        Returns:
            True if recording started successfully
        """
        if self.is_recording:
            print("Already recording")
            return False

        if frame is None or frame.size == 0:
            error_msg = "Cannot start recording: invalid frame"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            return False

        try:
            timestamp = self._generate_timestamp()
            filename = f"recording_{timestamp}.mp4"
            filepath = self.recordings_path / filename

            # Get frame dimensions
            height, width = frame.shape[:2]
            self.frame_size = (width, height)

            # Create VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*self.video_codec)
            self.video_writer = cv2.VideoWriter(
                str(filepath), fourcc, self.recording_fps, self.frame_size
            )

            if not self.video_writer.isOpened():
                raise Exception("Failed to open video writer")

            # Write first frame
            self.video_writer.write(frame)

            self.is_recording = True
            self.current_recording_path = filepath
            self.frame_count = 1

            print(f"Recording started: {filepath}")
            self.recording_started.emit(str(filepath))
            return True

        except Exception as e:
            error_msg = f"Failed to start recording: {e}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            self.is_recording = False
            self.video_writer = None
            return False

    def record_frame(self, frame: np.ndarray) -> bool:
        """
        Record a frame (if recording is active).

        Args:
            frame: BGR frame to record

        Returns:
            True if frame was recorded
        """
        if not self.is_recording or self.video_writer is None:
            return False

        if frame is None or frame.size == 0:
            return False

        try:
            # Resize frame if needed
            if frame.shape[:2][::-1] != self.frame_size:
                frame = cv2.resize(frame, self.frame_size)

            self.video_writer.write(frame)
            self.frame_count += 1
            return True

        except Exception as e:
            error_msg = f"Error recording frame: {e}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def stop_recording(self) -> Optional[str]:
        """
        Stop recording video.

        Returns:
            Path to saved recording or None if not recording
        """
        if not self.is_recording:
            print("Not currently recording")
            return None

        try:
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None

            filepath = str(self.current_recording_path)
            frame_count = self.frame_count

            self.is_recording = False
            self.current_recording_path = None
            self.frame_count = 0
            self.frame_size = None

            print(f"Recording stopped: {filepath} ({frame_count} frames)")
            self.recording_stopped.emit(filepath, frame_count)
            return filepath

        except Exception as e:
            error_msg = f"Error stopping recording: {e}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            self.is_recording = False
            return None

    def get_recordings_list(self) -> list:
        """
        Get list of all recordings.

        Returns:
            List of recording filenames
        """
        try:
            return sorted([f.name for f in self.recordings_path.glob("*.mp4")])
        except Exception:
            return []

    def get_snapshots_list(self) -> list:
        """
        Get list of all snapshots.

        Returns:
            List of snapshot filenames
        """
        try:
            pattern = f"*.{self.snapshot_format}"
            return sorted([f.name for f in self.snapshots_path.glob(pattern)])
        except Exception:
            return []
