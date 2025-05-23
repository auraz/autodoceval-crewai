#!/usr/bin/env python3
"""Simple test of document evaluation without Snakemake."""

import os
from pathlib import Path

# Set API key if not already set
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable not set")
    exit(1)

# Read test document
doc_path = Path("docs/input/bad_readme.md")
if not doc_path.exists():
    print(f"Error: {doc_path} not found")
    exit(1)

content = doc_path.read_text()
print(f"Testing with document: {doc_path}")
print(f"Content preview: {content[:100]}...")
print("\nNote: Full evaluation requires Python 3.10+ due to CrewAI dependencies.")