"""
Configuration loader module.

This module handles loading and validation of configuration files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass


class ConfigLoader:
    """
    Configuration loader and validator.
    
    Loads configuration from JSON files and provides fallback defaults.
    """
    
    DEFAULT_CONFIG = {
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "log_to_console": True,
            "log_to_file": True,
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "paths": {
            "default_input": "data/expenses_example.csv",
            "default_output": "output",
            "logs": "logs"
        },
        "visualization": {
            "dpi": 300,
            "figure_size_bar": [12, 6],
            "figure_size_pie": [12, 8],
            "figure_size_line": [14, 6],
            "style": "seaborn-v0_8-darkgrid",
            "color_palette": "husl",
            "save_format": "png",
            "show_plots": False
        },
        "analysis": {
            "date_format": "%Y-%m-%d",
            "output_date_format": "%m/%d/%Y",
            "currency_symbol": "$",
            "decimal_places": 2
        },
        "data_validation": {
            "required_columns": ["Date", "Category", "Amount", "Description"],
            "allow_missing_description": True,
            "min_amount": 0,
            "max_amount": 1000000
        },
        "output": {
            "file_naming": {
                "use_timestamp": True,
                "timestamp_format": "%Y%m%d_%H%M%S"
            }
        }
    }
    
    def __init__(self, config_path: Path = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Path to the configuration file. If None, uses defaults.
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.
        
        Returns:
            Configuration dictionary.
            
        Raises:
            ConfigurationError: If the configuration file is invalid.
        """
        if self.config_path is None:
            logger.info("No configuration file specified, using defaults")
            return self.DEFAULT_CONFIG.copy()
        
        config_path = Path(self.config_path)
        
        if not config_path.exists():
            logger.warning(
                f"Configuration file not found: {config_path}. Using defaults."
            )
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            config = self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            logger.info(f"Configuration loaded from: {config_path}")
            return config
            
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in configuration file: {config_path}\n"
                f"Error: {str(e)}"
            )
        except Exception as e:
            raise ConfigurationError(
                f"Error loading configuration file: {str(e)}"
            )
    
    def _merge_configs(
        self, 
        default: Dict[str, Any], 
        loaded: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge loaded configuration with defaults.
        
        Args:
            default: Default configuration dictionary.
            loaded: Loaded configuration dictionary.
            
        Returns:
            Merged configuration dictionary.
        """
        merged = default.copy()
        
        for key, value in loaded.items():
            if isinstance(value, dict) and key in merged:
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _validate_config(self) -> None:
        """
        Validate the configuration structure.
        
        Raises:
            ConfigurationError: If the configuration is invalid.
        """
        required_sections = ['logging', 'paths', 'visualization', 'analysis']
        
        for section in required_sections:
            if section not in self.config:
                raise ConfigurationError(
                    f"Missing required configuration section: {section}"
                )
        
        # Validate logging level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        log_level = self.config['logging']['level']
        if log_level not in valid_levels:
            raise ConfigurationError(
                f"Invalid logging level: {log_level}. "
                f"Must be one of: {', '.join(valid_levels)}"
            )
        
        # Validate visualization DPI
        if self.config['visualization']['dpi'] < 50:
            raise ConfigurationError(
                f"Invalid DPI value: {self.config['visualization']['dpi']}. "
                "Must be at least 50."
            )
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            *keys: Keys to traverse the configuration dictionary.
            default: Default value if key path doesn't exist.
            
        Returns:
            Configuration value or default.
            
        Example:
            >>> config = ConfigLoader()
            >>> dpi = config.get('visualization', 'dpi')
            >>> level = config.get('logging', 'level', default='INFO')
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get the complete configuration dictionary.
        
        Returns:
            Complete configuration dictionary.
        """
        return self.config.copy()


# Convenience function for quick configuration loading
def load_config(config_path: Path = None) -> ConfigLoader:
    """
    Load configuration from a file.
    
    Args:
        config_path: Path to configuration file. If None, uses defaults.
        
    Returns:
        ConfigLoader instance.
        
    Example:
        >>> config = load_config('config/config.json')
        >>> log_level = config.get('logging', 'level')
    """
    return ConfigLoader(config_path)
