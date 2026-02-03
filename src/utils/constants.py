"""Constants for SIRA Console."""

from enum import Enum


class ConnectionStatus(Enum):
    """Connection status enum."""
    DISCONNECTED = "Disconnected"
    CONNECTED = "Connected"
    ERROR = "Error"


class MovementStatus(Enum):
    """Movement status enum."""
    READY = "Ready"
    WALKING = "Walking"


class LogLevel(Enum):
    """Log level enum."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


# Color definitions
class Colors:
    """Color constants for the application."""
    
    # Backgrounds
    PRIMARY_BG = "#0a0a0a"
    SECONDARY_BG = "#1a1a1a"
    PANEL_BG = "#141414"
    
    # Borders and dividers
    BORDER = "#2a2a2a"
    DIVIDER = "#2a2a2a"
    
    # Text
    TEXT_PRIMARY = "#e0e0e0"
    TEXT_SECONDARY = "#a0a0a0"
    TEXT_DISABLED = "#5a5a5a"
    
    # Accent
    ACCENT_YELLOW = "#ffc107"
    
    # Status
    STATUS_GREEN = "#00ff41"
    STATUS_RED = "#ff1744"
    STATUS_GRAY = "#546e7a"
    STATUS_ORANGE = "#ff9800"
    
    # Servo ranges
    SERVO_SAFE = "#00ff41"
    SERVO_WARNING = "#ffc107"
    SERVO_DANGER = "#ff1744"


# Font definitions
class Fonts:
    """Font constants for the application."""
    
    FAMILY = "Consolas, Monaco, Courier New, monospace"
    SIZE_SMALL = 8
    SIZE_NORMAL = 9
    SIZE_LARGE = 10
    SIZE_HEADER = 11


# Tab indices
class TabIndex:
    """Tab index constants."""
    
    DASHBOARD = 0
    CONTROL = 1
    ANALYSIS = 2
    CONNECTION = 3
    DIAGNOSTICS = 4