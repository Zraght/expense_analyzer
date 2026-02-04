"""
Path management utilities.

This module provides cross-platform path handling using pathlib.
"""

import logging
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)


class PathManager:
    """
    Cross-platform path management utility.
    
    Provides methods for safe path operations and directory creation.
    """
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            path: Directory path to ensure exists.
            
        Returns:
            Path object pointing to the directory.
            
        Raises:
            OSError: If directory cannot be created.
            
        Example:
            >>> output_dir = PathManager.ensure_directory("output")
            >>> print(output_dir)
        """
        path = Path(path)
        
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {path}")
            return path
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {str(e)}")
            raise OSError(f"Cannot create directory {path}: {str(e)}")
    
    @staticmethod
    def validate_file_exists(path: Union[str, Path]) -> Path:
        """
        Validate that a file exists.
        
        Args:
            path: File path to validate.
            
        Returns:
            Path object if file exists.
            
        Raises:
            FileNotFoundError: If file does not exist.
            
        Example:
            >>> csv_path = PathManager.validate_file_exists("data/file.csv")
        """
        path = Path(path)
        
        if not path.exists():
            logger.error(f"File not found: {path}")
            raise FileNotFoundError(f"File not found: {path}")
        
        if not path.is_file():
            logger.error(f"Path is not a file: {path}")
            raise ValueError(f"Path is not a file: {path}")
        
        logger.debug(f"File validated: {path}")
        return path
    
    @staticmethod
    def safe_path_join(*parts: Union[str, Path]) -> Path:
        """
        Safely join path components.
        
        Args:
            *parts: Path components to join.
            
        Returns:
            Joined path as Path object.
            
        Example:
            >>> full_path = PathManager.safe_path_join("data", "expenses.csv")
        """
        return Path(*parts)
    
    @staticmethod
    def get_absolute_path(path: Union[str, Path]) -> Path:
        """
        Get absolute path from relative or absolute path.
        
        Args:
            path: Path to convert to absolute.
            
        Returns:
            Absolute path as Path object.
            
        Example:
            >>> abs_path = PathManager.get_absolute_path("data/file.csv")
        """
        return Path(path).resolve()
    
    @staticmethod
    def list_files(
        directory: Union[str, Path], 
        pattern: str = "*",
        recursive: bool = False
    ) -> list[Path]:
        """
        List files in a directory matching a pattern.
        
        Args:
            directory: Directory to search.
            pattern: File pattern to match (e.g., "*.csv").
            recursive: Whether to search recursively.
            
        Returns:
            List of Path objects matching the pattern.
            
        Example:
            >>> csv_files = PathManager.list_files("data", "*.csv")
        """
        directory = Path(directory)
        
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return []
        
        if recursive:
            files = list(directory.rglob(pattern))
        else:
            files = list(directory.glob(pattern))
        
        logger.debug(f"Found {len(files)} files in {directory} matching '{pattern}'")
        return files


def validate_input_path(path: Union[str, Path]) -> Path:
    """
    Validate an input file path.
    
    Args:
        path: Input file path to validate.
        
    Returns:
        Validated Path object.
        
    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If path is not a file.
        
    Example:
        >>> input_path = validate_input_path("data/expenses.csv")
    """
    return PathManager.validate_file_exists(path)


def validate_output_directory(path: Union[str, Path]) -> Path:
    """
    Validate and ensure an output directory exists.
    
    Args:
        path: Output directory path.
        
    Returns:
        Path object for the output directory.
        
    Example:
        >>> output_dir = validate_output_directory("output")
    """
    return PathManager.ensure_directory(path)
