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

# Just evaluate all documents without improvement
snakemake --cores 1 evaluate

# Evaluate and improve in one step (uses memory for context)
snakemake --cores 1 docs/output/myfile/myfile_improved.md

# Run auto-improve with custom settings
snakemake --cores 1 all --config max_iterations=5 target_score=80

# Clean outputs
snakemake --cores 1 clean
```

Place your markdown documents in `docs/input/` and the workflow will:
- **evaluate rule**: Evaluate documents and save scores/feedback
- **evaluate_and_improve rule**: Evaluate and improve in one workflow (with memory context)
- **auto_improve rule**: Iteratively improve until target score reached
- Outputs saved to `docs/output/{name}/` with appropriate suffixes

### Python API

For programmatic usage:

```python
from evcrew import DocumentCrew

# Create crew instance
crew = DocumentCrew()

# Evaluate a document
with open("docs/example.md", "r") as f:
    content = f.read()
score, feedback = crew.evaluator.execute(content)
print(f"Score: {score:.1f}%")
print(f"Feedback: {feedback}")

# Improve a document
improved_content = crew.improver.execute(content, feedback)

# Or use the combined workflow
improved_content, score, feedback = crew.evaluate_and_improve(content)

# Or use auto-improvement
from pathlib import Path
output_dir = Path("docs/output/example")
final_doc, history = crew.auto_improve(content, output_dir, "example", max_iterations=5, target_score=90)

# Save the improved version
with open("docs/example_improved.md", "w") as f:
    f.write(improved_content)
```

## Architecture

AutoDocEval uses CrewAI agents to evaluate and improve documentation:

### Iteration Tracking

The system includes a comprehensive iteration tracking system that captures:
- Document metadata (ID, path, timestamps)
- Quality metrics for each iteration (scores, feedback)
- Improvement deltas between iterations
- File paths for each improved version
- Total duration and iteration count

Tracking data is saved as JSON files for analysis and monitoring.

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

- **BaseAgent**: Abstract base class with common functionality
  - `create_task()`: Abstract method for creating agent-specific tasks
  - `save_results()`: Generic method for saving results with metadata
- **DocumentEvaluator**: Analyzes document clarity and provides structured feedback
  - Implements `create_task()` for evaluation tasks
  - `save_results()`: Saves evaluation scores and feedback using base class functionality
- **DocumentImprover**: Transforms documents based on evaluation feedback
  - Implements `create_task()` for improvement tasks
  - `save_results()`: Saves improved documents to disk
- **DocumentCrew**: Orchestrates multi-agent workflows
  - `evaluate_and_improve()`: Combined evaluation and improvement with memory
  - `auto_improve()`: Iterative improvement until target score reached
- Agents handle their own file I/O for better encapsulation

### Workflow System

The Snakemake workflow handles:
- Batch processing of multiple documents
- Iterative improvement loops
- Progress tracking and reporting
- Automatic file organization

## Configuration

Default values are set in the Snakefile:
- `max_iterations`: 2 (maximum improvement iterations)
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
│   │   ├── improver.py  # Document improver
│   │   └── prompts/     # Agent prompt templates
│   │       ├── evaluator.md     # Evaluation prompt
│   │       ├── improver.md      # Improvement prompt
│   │       └── improver_task.md # Improvement task prompt
│   ├── tests/           # Unit tests
│   │   ├── test_crew.py     # Crew tests
│   │   └── test_evaluator.py # Evaluator tests
│   ├── __init__.py      # Package exports
│   └── crew.py          # DocumentCrew workflow class
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