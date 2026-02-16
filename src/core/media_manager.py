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

        # Create directories if they don't exist
        self._create_directories()

        # Recording state
        self.video_writer: Optional[cv2.VideoWriter] = None
        self.is_recording = False
        self.current_recording_path: Optional[Path] = None
        self.frame_count = 0
        self.frame_size = None
        self.recording_start_time: Optional[datetime] = None

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

    def _add_timestamp_overlay(
        self, frame: np.ndarray, recording: bool = False
    ) -> np.ndarray:
        """
        Add timestamp overlay to frame.

        Args:
            frame: BGR frame
            recording: If True, adds recording duration; if False, adds snapshot timestamp

        Returns:
            Frame with timestamp overlay
        """
        frame_copy = frame.copy()
        h, w = frame_copy.shape[:2]

        # Generate timestamp text
        now = datetime.now()
        timestamp = (
            now.strftime("%d %b %Y %H:%M:%S") + f":{now.microsecond // 10000:02d}"
        )

        # Font settings
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        thickness = 1
        color = (255, 255, 255)
        bg_color = (0, 0, 0)

        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            timestamp, font, font_scale, thickness
        )

        # Position in bottom-right
        margin = 10
        x = w - text_width - margin - 20
        y = h - margin - 10

        # Draw text
        cv2.putText(
            frame_copy,
            timestamp,
            (x, y),
            font,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA,
        )

        # If recording, add duration and REC indicator in top-left
        if recording and self.recording_start_time:
            elapsed = datetime.now() - self.recording_start_time
            total_seconds = int(elapsed.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            # Red dot
            cv2.circle(frame_copy, (25, 25), 10, (0, 0, 255), -1)

            # Duration text
            duration_x = 50
            duration_y = 30
            (dur_width, dur_height), _ = cv2.getTextSize(
                duration, font, font_scale, thickness
            )

            # Text
            cv2.putText(
                frame_copy,
                duration,
                (duration_x, duration_y),
                font,
                font_scale,
                color,
                thickness,
                cv2.LINE_AA,
            )

            # REC text
            cv2.putText(
                frame_copy,
                "REC",
                (duration_x, duration_y + 20),
                font,
                0.3,
                (0, 0, 255),
                1,
                cv2.LINE_AA,
            )

        return frame_copy

    def take_snapshot(self, frame: np.ndarray) -> Optional[str]:
        """
        Save a snapshot of the current frame with timestamp overlay.

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

            # Add timestamp overlay to snapshot
            frame_with_timestamp = self._add_timestamp_overlay(frame, recording=False)

            # Save with high quality
            if self.snapshot_format.lower() == "png":
                cv2.imwrite(
                    str(filepath),
                    frame_with_timestamp,
                    [cv2.IMWRITE_PNG_COMPRESSION, 0],
                )
            elif self.snapshot_format.lower() in ["jpg", "jpeg"]:
                cv2.imwrite(
                    str(filepath), frame_with_timestamp, [cv2.IMWRITE_JPEG_QUALITY, 100]
                )
            else:
                cv2.imwrite(str(filepath), frame_with_timestamp)

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
        Start recording video with best quality using OpenCV.

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
            filename = f"recording_{timestamp}.avi"  # Changed to AVI for better quality
            filepath = self.recordings_path / filename

            # Get frame dimensions
            height, width = frame.shape[:2]
            self.frame_size = (width, height)

            # Try codecs in order of quality
            # MJPEG = Motion JPEG (best quality with OpenCV, larger files)
            codec_options = [
                ("MJPG", "Motion JPEG - Best Quality"),  # Highest quality
                ("XVID", "Xvid MPEG-4"),  # Good quality
                ("mp4v", "MPEG-4"),  # Fallback
            ]

            self.video_writer = None
            selected_codec = None

            for codec_code, codec_name in codec_options:
                try:
                    fourcc = cv2.VideoWriter_fourcc(*codec_code)

                    # For MJPEG, use AVI container for best compatibility
                    if codec_code == "MJPG":
                        test_path = self.recordings_path / f"recording_{timestamp}.avi"
                    else:
                        test_path = self.recordings_path / f"recording_{timestamp}.mp4"

                    writer = cv2.VideoWriter(
                        str(test_path),
                        fourcc,
                        self.recording_fps,
                        self.frame_size,
                        True,  # isColor
                    )

                    if writer.isOpened():
                        self.video_writer = writer
                        self.current_recording_path = test_path
                        selected_codec = codec_name
                        print(f"✓ Using codec: {codec_name}")
                        break
                    else:
                        writer.release()
                except Exception as e:
                    print(f"  Codec {codec_name} failed: {e}")
                    continue

            if self.video_writer is None or not self.video_writer.isOpened():
                raise Exception("Failed to initialize video writer with any codec")

            # Set recording start time
            self.recording_start_time = datetime.now()

            # Write first frame with overlay
            frame_with_overlay = self._add_timestamp_overlay(frame, recording=True)
            self.video_writer.write(frame_with_overlay)

            self.is_recording = True
            self.frame_count = 1

            print(f"Recording started: {self.current_recording_path}")
            print(f"  Resolution: {width}x{height}")
            print(f"  FPS: {self.recording_fps}")
            print(f"  Codec: {selected_codec}")

            self.recording_started.emit(str(self.current_recording_path))
            return True

        except Exception as e:
            error_msg = f"Failed to start recording: {e}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            self.is_recording = False
            if self.video_writer:
                self.video_writer.release()
            self.video_writer = None
            self.recording_start_time = None
            return False

    def record_frame(self, frame: np.ndarray) -> bool:
        """
        Record a frame with timestamp overlay (if recording is active).

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

            # Add timestamp overlay
            frame_with_overlay = self._add_timestamp_overlay(frame, recording=True)

            # Write frame
            self.video_writer.write(frame_with_overlay)
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
            self.recording_start_time = None

            # Verify file was created and get size
            if Path(filepath).exists():
                file_size = Path(filepath).stat().st_size / (1024 * 1024)  # MB
                print(f"Recording saved: {filepath}")
                print(f"  Frames: {frame_count}")
                print(f"  Size: {file_size:.2f} MB")
                self.recording_stopped.emit(filepath, frame_count)
                return filepath
            else:
                error_msg = "Recording file was not created"
                print(error_msg)
                self.error_occurred.emit(error_msg)
                return None

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
            # Look for both AVI and MP4 files
            recordings = []
            recordings.extend([f.name for f in self.recordings_path.glob("*.avi")])
            recordings.extend([f.name for f in self.recordings_path.glob("*.mp4")])
            return sorted(recordings)
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
