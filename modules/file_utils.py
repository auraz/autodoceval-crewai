"""File handling utilities for AutoDocEval."""

import os
from typing import Optional


def read_file(file_path: str) -> str:
    """Reads a file and returns its contents.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        The contents of the file as a string
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    """Writes content to a file, creating directories if needed.
    
    Args:
        file_path: Path where the file should be written
        content: Content to write to the file
    """
    # Create directories if they don't exist
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def get_file_extension(file_path: str) -> str:
    """Gets the extension of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        The file extension (including the dot) or empty string if no extension
    """
    _, ext = os.path.splitext(file_path)
    return ext