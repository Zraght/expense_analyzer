"""
Configuration loader — reads config/config.json and merges with hardcoded defaults.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when the configuration file is missing required fields or is malformed."""


class ConfigLoader:
    """
    Load, validate, and expose application configuration.

    Merges a user-supplied JSON file with built-in defaults so that partial
    configs are always safe to use.
    """

    DEFAULTS: dict[str, Any] = {
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "log_to_console": True,
            "log_to_file": True,
            "max_bytes": 10_485_760,
            "backup_count": 5,
        },
        "paths": {
            "default_input": "data/expenses_example.csv",
            "default_output": "output",
            "logs": "logs",
        },
        "visualization": {
            "dpi": 300,
            "figure_size_bar": [12, 6],
            "figure_size_pie": [12, 8],
            "figure_size_line": [14, 6],
            "style": "seaborn-v0_8-darkgrid",
            "color_palette": "husl",
            "show_plots": False,
        },
        "analysis": {
            "date_format": "%Y-%m-%d",
            "output_date_format": "%m/%d/%Y",
            "currency_symbol": "$",
            "anomaly_z_threshold": 2.0,
        },
        "data_validation": {
            "required_columns": ["Date", "Category", "Amount", "Description"],
            "min_amount": 0,
            "max_amount": 1_000_000,
        },
        "output": {
            "timestamp_format": "%Y%m%d_%H%M%S",
            "export_html": True,
        },
    }

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path
        self.config = self._load()
        self._validate()

    def _load(self) -> dict[str, Any]:
        if self.config_path is None:
            logger.debug("No config file specified — using defaults")
            return self._deep_copy(self.DEFAULTS)

        path = Path(self.config_path)
        if not path.exists():
            logger.warning("Config file not found: %s — using defaults", path)
            return self._deep_copy(self.DEFAULTS)

        try:
            with open(path, encoding="utf-8") as f:
                user_config = json.load(f)
            merged = self._merge(self.DEFAULTS, user_config)
            logger.info("Configuration loaded from %s", path)
            return merged
        except json.JSONDecodeError as exc:
            raise ConfigurationError(f"Invalid JSON in {path}: {exc}") from exc

    def _validate(self) -> None:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        level = self.config["logging"]["level"]
        if level not in valid_levels:
            raise ConfigurationError(
                f"Invalid log level '{level}'. Must be one of: {', '.join(valid_levels)}"
            )
        if self.config["visualization"]["dpi"] < 50:
            raise ConfigurationError("visualization.dpi must be >= 50")

    def get(self, *keys: str, default: Any = None) -> Any:
        """Retrieve a nested config value by key path, e.g. ``config.get('logging', 'level')``."""
        node = self.config
        for key in keys:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                return default
        return node

    @staticmethod
    def _merge(base: dict, override: dict) -> dict:
        result = base.copy()
        for k, v in override.items():
            if isinstance(v, dict) and isinstance(result.get(k), dict):
                result[k] = ConfigLoader._merge(result[k], v)
            else:
                result[k] = v
        return result

    @staticmethod
    def _deep_copy(d: dict) -> dict:
        import copy
        return copy.deepcopy(d)


def load_config(config_path: Path | None = None) -> ConfigLoader:
    """Convenience wrapper — returns a ready-to-use :class:`ConfigLoader`."""
    return ConfigLoader(config_path)
