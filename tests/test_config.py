"""
Tests for the configuration loader (utils/config_loader.py).
"""

import json
from pathlib import Path

import pytest

from utils.config_loader import ConfigLoader, ConfigurationError, load_config


class TestConfigLoaderDefaults:
    def test_loads_without_file(self):
        config = ConfigLoader()
        assert config.config is not None

    def test_default_log_level(self):
        config = ConfigLoader()
        assert config.get("logging", "level") == "INFO"

    def test_default_dpi(self):
        config = ConfigLoader()
        assert config.get("visualization", "dpi") == 300

    def test_required_columns_present(self):
        config = ConfigLoader()
        cols = config.get("data_validation", "required_columns")
        assert isinstance(cols, list)
        assert "Date" in cols
        assert "Amount" in cols

    def test_get_missing_key_returns_default(self):
        config = ConfigLoader()
        result = config.get("nonexistent", "key", default="fallback")
        assert result == "fallback"


class TestConfigLoaderFromFile:
    def test_loads_valid_file(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps({"logging": {"level": "DEBUG"}}))
        config = ConfigLoader(cfg_file)
        assert config.get("logging", "level") == "DEBUG"

    def test_merges_with_defaults(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps({"logging": {"level": "DEBUG"}}))
        config = ConfigLoader(cfg_file)
        # DPI not in user file — should still have the default
        assert config.get("visualization", "dpi") == 300

    def test_missing_file_falls_back_to_defaults(self, tmp_path):
        config = ConfigLoader(tmp_path / "nonexistent.json")
        assert config.get("logging", "level") == "INFO"

    def test_invalid_json_raises(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{ not valid json }")
        with pytest.raises(ConfigurationError, match="Invalid JSON"):
            ConfigLoader(bad_file)

    def test_invalid_log_level_raises(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps({"logging": {"level": "VERBOSE"}}))
        with pytest.raises(ConfigurationError, match="Invalid log level"):
            ConfigLoader(cfg_file)

    def test_low_dpi_raises(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps({"visualization": {"dpi": 10}}))
        with pytest.raises(ConfigurationError, match="dpi"):
            ConfigLoader(cfg_file)


class TestLoadConfigConvenience:
    def test_returns_config_loader(self):
        config = load_config()
        assert isinstance(config, ConfigLoader)

    def test_with_path(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps({"logging": {"level": "WARNING"}}))
        config = load_config(cfg_file)
        assert config.get("logging", "level") == "WARNING"
