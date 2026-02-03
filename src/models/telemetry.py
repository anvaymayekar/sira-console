"""Telemetry model for SIRA Console."""

from dataclasses import dataclass
from datetime import datetime
from typing import List
from src.utils.constants import LogLevel


@dataclass
class TelemetryEntry:
    """Single telemetry log entry."""

    timestamp: datetime
    level: LogLevel
    message: str

    def format_timestamp(self) -> str:
        """
        Format timestamp for display.

        Returns:
            Formatted timestamp string
        """
        return self.timestamp.strftime("%H:%M:%S.%f")[:-3]

    def to_string(self) -> str:
        """
        Convert entry to formatted string.

        Returns:
            Formatted log entry
        """
        return f"[{self.format_timestamp()}] {self.level.value}: {self.message}"


class TelemetryLog:
    """Telemetry log manager."""

    def __init__(self, max_entries: int = 1000):
        """
        Initialize telemetry log.

        Args:
            max_entries: Maximum number of log entries to keep
        """
        self.max_entries = max_entries
        self._entries: List[TelemetryEntry] = []

    def add_entry(self, level: LogLevel, message: str) -> None:
        """
        Add a new log entry.

        Args:
            level: Log level
            message: Log message
        """
        entry = TelemetryEntry(timestamp=datetime.now(), level=level, message=message)
        self._entries.append(entry)

        # Trim old entries if exceeding max
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]

    def get_entries(self) -> List[TelemetryEntry]:
        """
        Get all log entries.

        Returns:
            List of telemetry entries
        """
        return self._entries

    def clear(self) -> None:
        """Clear all log entries."""
        self._entries.clear()

    def search(self, query: str) -> List[TelemetryEntry]:
        """
        Search log entries for a query string.

        Args:
            query: Search query

        Returns:
            List of matching entries
        """
        query_lower = query.lower()
        return [
            entry for entry in self._entries if query_lower in entry.message.lower()
        ]

    def info(self, message: str) -> None:
        """Add INFO level log entry."""
        self.add_entry(LogLevel.INFO, message)

    def warning(self, message: str) -> None:
        """Add WARNING level log entry."""
        self.add_entry(LogLevel.WARNING, message)

    def error(self, message: str) -> None:
        """Add ERROR level log entry."""
        self.add_entry(LogLevel.ERROR, message)
