# AutoDocEval with CrewAI

Document evaluation and improvement using CrewAI agents with persistent memory capabilities.

## What is CrewAI?

[CrewAI](https://github.com/crewai/crewai) is a framework for orchestrating role-playing autonomous AI agents. In AutoDocEval, we use CrewAI to create specialized agents for document evaluation and improvement, leveraging their collaborative capabilities for more effective documentation enhancement.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/autodoceval-crewai.git
cd autodoceval-crewai

# Create and activate virtual environment (requires Python 3.10+)
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
uv pip install -e .
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=your_api_key_here
```

## Usage

### Using Snakemake Workflows

All document processing is handled through Snakemake workflows:

```bash
# Auto-improve all documents in docs/input/
snakemake --cores 1 all

# Or just evaluate specific documents without improvement
snakemake --cores 1 docs/output/myfile/myfile_score.txt

# Run with custom settings
snakemake --cores 1 all --config max_iterations=5 target_score=80

# Clean outputs
snakemake --cores 1 clean
```

Place your markdown documents in `docs/input/` and the workflow will:
- Evaluate each document and save scores to `docs/output/{name}/{name}_score.txt`
- Generate feedback in `docs/output/{name}/{name}_feedback.txt`
- Create improved versions in `docs/output/{name}/{name}_final.md`

### Python API

For programmatic usage:

```python
from evcrew import evaluate_document, improve_document

# Evaluate a document
with open("docs/example.md", "r") as f:
    content = f.read()
score, feedback = evaluate_document(content)
print(f"Score: {score:.1f}%")
print(f"Feedback: {feedback}")

# Improve a document
improved_content = improve_document(content, feedback)

# Save the improved version
with open("docs/example_improved.md", "w") as f:
    f.write(improved_content)
```

## Architecture

AutoDocEval uses CrewAI agents to evaluate and improve documentation:

### Agents

- **DocumentEvaluator**: Analyzes document clarity, completeness, and coherence
  - Returns scores on a 0-100 scale
  - Provides specific, actionable feedback
  - Maintains consistency across evaluations

- **DocumentImprover**: Revises documents based on evaluation feedback
  - Applies feedback to enhance clarity
  - Preserves document intent and technical accuracy
  - Learns from previous improvements

### Agent System

The system uses specialized agents for document processing:

- **DocumentEvaluator**: Analyzes document clarity and provides structured feedback
- **DocumentImprover**: Transforms documents based on evaluation feedback
- Agents use direct task execution for optimal performance
- Each agent has a specific role, goal, and backstory for consistent results

### Workflow System

The Snakemake workflow handles:
- Batch processing of multiple documents
- Iterative improvement loops
- Progress tracking and reporting
- Automatic file organization

## Configuration

Default values are set in the Snakefile:
- `max_iterations`: 3 (maximum improvement iterations)
- `target_score`: 85 (target quality score, 0-100 scale)

Override via command line:

```bash
snakemake --cores 1 all --config max_iterations=5 target_score=90
```

## Project Structure

```
autodoceval-crewai/
├── evcrew/              # Core package
│   ├── agents/          # Agent implementations
│   │   ├── base.py      # Base agent class
│   │   ├── evaluator.py # Document evaluator
│   │   └── improver.py  # Document improver
│   ├── prompts/         # Agent prompt templates
│   │   ├── evaluator.md # Evaluation prompt
│   │   └── improver.md  # Improvement prompt
│   ├── tests/           # Unit tests
│   │   └── test_evaluator.py
│   ├── __init__.py      # Package exports
│   └── core.py          # Simple API wrappers
├── docs/                # Document storage
│   ├── input/           # Input documents
│   └── output/          # Evaluation results
├── config/              # Configuration files
│   └── CLAUDE.md        # AI assistant instructions
├── Snakefile            # Workflow definitions
├── pyproject.toml       # Package metadata
└── README.md            # This file
```

## Requirements

- Python 3.10+ (3.12 recommended)
- OpenAI API key
- Dependencies installed via `uv pip install -e .`

## License

MIT