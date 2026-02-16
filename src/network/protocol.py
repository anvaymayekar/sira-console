"""Message protocol definitions."""

from enum import IntEnum


class MessageType(IntEnum):
    """Message type identifiers."""

    FRAME = 0x01  # Camera frame (JPEG)
    TELEMETRY = 0x02  # Telemetry data (JSON)
    DETECTION = 0x03  # Detection event
    SERVO_STATE = 0x04  # Servo states (future)
    COMMAND = 0xFF  # Command to Pi
