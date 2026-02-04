"""
Test configuration loader module.

This module contains unit tests for the configuration loading functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from utils.config_loader import ConfigLoader, load_config, ConfigurationError


class TestConfigLoader:
    """Test suite for ConfigLoader class."""
    
    def test_default_config_loading(self):
        """Test loading with no config file uses defaults."""
        config = ConfigLoader()
        assert config.get('logging', 'level') == 'INFO'
        assert config.get('paths', 'default_output') == 'output'
    
    def test_valid_config_file_loading(self):
        """Test loading a valid configuration file."""
        test_config = {
            "logging": {"level": "DEBUG"},
            "paths": {"default_output": "custom_output"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            temp_path = f.name
        
        try:
            config = ConfigLoader(temp_path)
            assert config.get('logging', 'level') == 'DEBUG'
            assert config.get('paths', 'default_output') == 'custom_output'
        finally:
            Path(temp_path).unlink()
    
    def test_invalid_json_raises_error(self):
        """Test that invalid JSON raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            with pytest.raises(ConfigurationError):
                ConfigLoader(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_missing_file_uses_defaults(self):
        """Test that missing file falls back to defaults."""
        config = ConfigLoader('nonexistent_config.json')
        assert config.get('logging', 'level') == 'INFO'
    
    def test_invalid_log_level_raises_error(self):
        """Test that invalid logging level raises ConfigurationError."""
        test_config = {
            "logging": {"level": "INVALID_LEVEL"},
            "paths": {},
            "visualization": {},
            "analysis": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ConfigurationError):
                ConfigLoader(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_get_nested_values(self):
        """Test getting nested configuration values."""
        config = ConfigLoader()
        dpi = config.get('visualization', 'dpi')
        assert dpi == 300
    
    def test_get_with_default(self):
        """Test getting values with default fallback."""
        config = ConfigLoader()
        value = config.get('nonexistent', 'key', default='default_value')
        assert value == 'default_value'
    
    def test_get_all(self):
        """Test getting complete configuration."""
        config = ConfigLoader()
        all_config = config.get_all()
        assert 'logging' in all_config
        assert 'paths' in all_config
        assert 'visualization' in all_config
    
    def test_config_merge(self):
        """Test that loaded config merges with defaults."""
        test_config = {
            "logging": {"level": "ERROR"}
            # Other sections missing - should be filled from defaults
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            temp_path = f.name
        
        try:
            config = ConfigLoader(temp_path)
            # Should have custom value
            assert config.get('logging', 'level') == 'ERROR'
            # Should have default value
            assert config.get('paths', 'default_output') == 'output'
        finally:
            Path(temp_path).unlink()
    
    def test_load_config_convenience_function(self):
        """Test the convenience load_config function."""
        config = load_config()
        assert isinstance(config, ConfigLoader)
        assert config.get('logging', 'level') == 'INFO'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
