"""Configuration loader for SIRA Console."""

import json
import os
from typing import Any, Dict


class ConfigLoader:
    """Configuration loader class."""

    def __init__(self, config_dir: str = "config"):
        """
        Initialize configuration loader.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir
        self._settings: Dict[str, Any] = {}
        self._servo_config: Dict[str, Any] = {}

    def load_all(self) -> None:
        """Load all configuration files."""
        self._settings = self._load_json("settings.json")
        self._servo_config = self._load_json("servo_config.json")

    def _load_json(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON configuration file.

        Args:
            filename: Name of the JSON file

        Returns:
            Dictionary containing configuration data
        """
        filepath = os.path.join(self.config_dir, filename)
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Configuration file {filepath} not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse {filepath}: {e}")
            return {}

    def get_settings(self) -> Dict[str, Any]:
        """
        Get application settings.

        Returns:
            Settings dictionary
        """
        return self._settings

    def get_servo_config(self) -> Dict[str, Any]:
        """
        Get servo configuration.

        Returns:
            Servo configuration dictionary
        """
        return self._servo_config

    def get_setting(self, *keys: str, default: Any = None) -> Any:
        """
        Get a specific setting value using dot notation.

        Args:
            keys: Nested keys to traverse
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        value = self._settings
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def get_servo_param(self, *keys: str, default: Any = None) -> Any:
        """
        Get a specific servo parameter using dot notation.

        Args:
            keys: Nested keys to traverse
            default: Default value if key not found

        Returns:
            Parameter value or default
        """
        value = self._servo_config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
