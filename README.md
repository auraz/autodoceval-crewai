# AutoDocEval with CrewAI

Document evaluation and improvement in a closed-loop cycle using CrewAI agents with persistent memory capabilities.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/autodoceval-crewai.git
cd autodoceval-crewai

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
uv pip install -e .
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=your_api_key_here
```

## Usage

### Using Snakemake Workflows

```bash
# Initialize project structure
snakemake --cores 1 init

# Evaluate document
snakemake --cores 1 grade --config input_file=docs/example.md

# Improve document
snakemake --cores 1 improve --config input_file=docs/example.md

# Auto-improve with custom settings
snakemake --cores 1 auto_improve --config input_file=docs/example.md max_iterations=5 target_score=0.8

# Clean outputs
snakemake --cores 1 clean
```

### Python API

```python
from autodoceval_crewai import evaluate_document, improve_document, auto_improve_document

# Evaluate a document
with open("docs/example.md", "r") as f:
    content = f.read()
score, feedback = evaluate_document(content)

# Improve a document
improved_content = improve_document(content, feedback)

# Run auto-improvement loop
auto_improve_document("docs/example.md", max_iterations=3, target_score=0.75)

# Use persistent memory with custom ID
score, feedback = evaluate_document(content, memory_id="my-docs-memory")
improved_content = improve_document(content, feedback, memory_id="my-docs-memory")
auto_improve_document("docs/example.md", memory_id="my-docs-memory")
```

## Architecture

AutoDocEval uses CrewAI agents to evaluate and improve documentation quality:

- `DocumentEvaluator`: Agent that analyzes document clarity and provides feedback
- `DocumentImprover`: Agent that revises documents based on evaluation feedback

The system employs a closed-loop approach for iterative improvement until a target quality score is reached.

### Persistent Memory

Memory is always enabled for all agent operations:

- Agents remember previous document evaluations and improvements
- Learn from past experiences for more consistent results
- Recognize patterns across multiple documents
- Share knowledge between evaluation and improvement processes
- Auto-generated memory IDs ensure persistence across sessions

For detailed information on using memory features, see [MEMORY.md](MEMORY.md).

## Project Structure

```
autodoceval-crewai/
├── evcrew/           # Core package
│   ├── agents/       # Agent implementations
│   │   ├── base.py   # Base utilities and types
│   │   ├── evaluator.py  # Document evaluator agent
│   │   └── improver.py   # Document improver agent
│   ├── core.py       # Core API functions
│   └── file_utils.py # File handling utilities
├── docs/             # Input/output documentation
│   ├── input/        # Documents to evaluate
│   └── output/       # Evaluation results and improved documents
├── examples/         # Example scripts
├── Snakefile         # Workflow definitions
├── pyproject.toml    # Package configuration
└── README.md         # This file
```

## License

MIT