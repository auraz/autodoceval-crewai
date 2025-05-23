"""File handling utilities for AutoDocEval."""

import os


def read_file(file_path: str) -> str:
    """Reads a file and returns its contents."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    """Writes content to a file, creating directories if needed."""
    # Create directories if they don't exist
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def get_file_extension(file_path: str) -> str:
    """Gets the extension of a file."""
    _, ext = os.path.splitext(file_path)
    return ext
