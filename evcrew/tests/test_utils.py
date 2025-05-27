"""Test utility functions."""

import os
import tempfile
from pathlib import Path

import pytest

from evcrew.utils import process_file, read_file, write_file


def test_read_file():
    """Test reading files."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content")
        temp_path = f.name
    
    try:
        # Test with string path
        content = read_file(temp_path)
        assert content == "Test content"
        
        # Test with Path object
        content = read_file(Path(temp_path))
        assert content == "Test content"
    finally:
        os.unlink(temp_path)


def test_read_file_not_found():
    """Test reading non-existent file."""
    with pytest.raises(FileNotFoundError):
        read_file("/non/existent/file.txt")


def test_write_file():
    """Test writing files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "test.txt"
        
        # Test writing with string path
        write_file(str(file_path), "Test content")
        assert file_path.read_text() == "Test content"
        
        # Test writing with Path object
        write_file(file_path, "Updated content")
        assert file_path.read_text() == "Updated content"


def test_write_file_creates_directories():
    """Test that write_file creates parent directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test creating nested directories
        file_path = Path(temp_dir) / "a" / "b" / "c" / "test.txt"
        write_file(file_path, "Test content")
        assert file_path.exists()
        assert file_path.read_text() == "Test content"


def test_process_file():
    """Test process_file utility."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content")
        temp_path = f.name
    
    try:
        # Define a simple processor
        def uppercase_processor(content: str, **kwargs) -> str:
            return content.upper()
        
        # Test process_file
        result = process_file(uppercase_processor, temp_path)
        assert result == "TEST CONTENT"
        
        # Test with kwargs
        def prefix_processor(content: str, prefix: str = "") -> str:
            return f"{prefix}{content}"
        
        result = process_file(prefix_processor, temp_path, prefix="PREFIX: ")
        assert result == "PREFIX: Test content"
    finally:
        os.unlink(temp_path)