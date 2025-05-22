# Using CrewAI with AutoDocEval

This guide explains how to use the CrewAI implementation of AutoDocEval for document evaluation and improvement.

## What is CrewAI?

[CrewAI](https://github.com/crewai/crewai) is a framework for orchestrating role-playing autonomous AI agents. In AutoDocEval, we use CrewAI to create specialized agents for document evaluation and improvement, leveraging their collaborative capabilities for more effective documentation enhancement.

## Installation

To use the CrewAI implementation:

```bash
# From the autodoceval directory
cd autodoceval-crewai

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
uv pip install -e .
```

Make sure to set your OpenAI API key:

```bash
export OPENAI_API_KEY=your_api_key_here
```

## Quick Start

The simplest way to get started is to run the provided setup script:

```bash
./setup_and_use_crewai.sh
```

This script:
1. Sets up a virtual environment
2. Installs the necessary dependencies
3. Demonstrates evaluation and improvement of a sample document
4. Shows how to use both the command-line interface and Python API

## Usage Options

### Command Line Interface

The CrewAI implementation provides a CLI similar to the main AutoDocEval:

```bash
# Evaluate document clarity
autodoceval-crewai grade examples/sample_doc.md

# Improve a document (generates sample_doc_improved.md)
autodoceval-crewai improve examples/sample_doc.md

# Run auto-improvement loop (3 iterations max, 70% quality target)
autodoceval-crewai auto-improve examples/sample_doc.md --iterations 3 --target 0.7
```

### Python Library

Import and use the CrewAI implementation in your Python code:

```python
from autodoceval_crewai import evaluate_document, improve_document, auto_improve_document
from autodoceval_crewai.file_utils import read_file, write_file

# Evaluate a document
content = read_file("examples/sample_doc.md")
score, feedback = evaluate_document(content)
print(f"Score: {score * 100:.1f}%")
print(f"Feedback: {feedback}")

# Improve a
