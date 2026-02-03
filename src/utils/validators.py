"""Validation utilities for SIRA Console."""

from typing import Any


def validate_angle(angle: float, min_angle: float, max_angle: float) -> float:
    """
    Validate and clamp angle to valid range.

    Args:
        angle: Angle to validate
        min_angle: Minimum allowed angle
        max_angle: Maximum allowed angle

    Returns:
        Clamped angle value
    """
    return max(min_angle, min(max_angle, angle))


def validate_resolution(resolution: str) -> bool:
    """
    Validate resolution string format.

    Args:
        resolution: Resolution string in format "WIDTHxHEIGHT"

    Returns:
        True if valid, False otherwise
    """
    try:
        parts = resolution.lower().split("x")
        if len(parts) != 2:
            return False
        width, height = int(parts[0]), int(parts[1])
        return width > 0 and height > 0
    except (ValueError, AttributeError):
        return False


def validate_config_value(value: Any, expected_type: type) -> bool:
    """
    Validate configuration value type.

    Args:
        value: Value to validate
        expected_type: Expected type

    Returns:
        True if valid, False otherwise
    """
    return isinstance(value, expected_type)
