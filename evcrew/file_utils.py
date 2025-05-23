"""File handling utilities for AutoDocEval."""

import os


def read_file(file_path: str) -> str:
    """Read file and return its contents."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    """Write content to file, creating directories if needed."""
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def get_file_extension(file_path: str) -> str:
    """Get file extension from path."""
    _, ext = os.path.splitext(file_path)
    return ext


def format_percentage(value: float) -> str:
    """Format float as percentage string."""
    return f"{value * 100:.1f}%"
