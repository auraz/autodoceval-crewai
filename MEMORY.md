# Persistent Memory in AutoDocEval CrewAI

This guide explains how to use persistent memory capabilities in the CrewAI implementation of AutoDocEval.

## What is Persistent Memory?

The CrewAI agents in AutoDocEval now support persistent memory, which allows the agents to:

- Remember previous document evaluations and improvements
- Learn from past experiences to provide more consistent feedback
- Recognize patterns across multiple documents
- Maintain context between iterations of document improvement

This memory capability enhances the quality and consistency of document evaluation and improvement over time.

## Using Memory with the CLI

### Basic Memory Usage

By default, persistent memory is enabled for all operations. The system generates a unique memory identifier based on the document path:

```bash
# Memory is enabled by default
autodoceval-crewai grade examples/sample_doc.md
autodoceval-crewai improve examples/sample_doc.md
autodoceval-crewai auto-improve examples/sample_doc.md
```

### Custom Memory IDs

You can specify a custom memory ID to explicitly control which memory is used:

```bash
# Use a custom memory ID for related documents
autodoceval-crewai grade examples/api_docs.md --memory-id api-docs-memory
autodoceval-crewai grade examples/api_reference.md --memory-id api-docs-memory

# Improvements will benefit from evaluations of both documents
autodoceval-crewai improve examples/api_docs.md --memory-id api-docs-memory
```

### Disabling Memory

For one-off operations where memory isn't needed, you can disable it:

```bash
# Run without using or updating memory
autodoceval-crewai grade examples/sample_doc.md --no-memory
autodoceval-crewai improve examples/sample_doc.md --no-memory
```

## Using Memory with the Python API

### Basic Memory Usage

```python
from autodoceval_crewai import evaluate_document, improve_document, auto_improve_document
from autodoceval_crewai.file_utils import read_file

# Using default memory (automatically generated ID)
content = read_file("examples/sample_doc.md")
score, feedback = evaluate_document(content, memory_id="my-project-docs")
improved = improve_document(content, feedback, memory_id="my-project-docs")

# Auto-improve with memory
auto_improve_document(
    "examples/sample_doc.md",
    memory_id="my-project-docs",
    persist_memory=True  # This is the default
)
```

### Shared Memory Across Documents

```python
# Using the same memory ID lets agents learn across different documents
api_memory_id = "api-documentation"

# Evaluate different but related documents with shared memory
api_docs = read_file("examples/api_docs.md")
api_ref = read_file("examples/api_reference.md") 

# Both evaluations contribute to the same memory
score1, feedback1 = evaluate_document(api_docs, memory_id=api_memory_id)
score2, feedback2 = evaluate_document(api_ref, memory_id=api_memory_id)

# Improvement benefits from both evaluations
improved_api_docs = improve_document(api_docs, feedback1, memory_id=api_memory_id)
```

### Disabling Memory

```python
# Run without memory for one-off operations
score, feedback = evaluate_document(content, memory_id=None)
improved = improve_document(content, feedback, memory_id=None)

# Explicitly disable memory in auto-improve
auto_improve_document("examples/sample_doc.md", persist_memory=False)
```

## Memory Storage and Management

By default, CrewAI stores memory in a local database in the `.crewai` directory in your home folder. This ensures that memory persists across different runs and sessions.

### Memory Structure

The memory system stores:

- Document evaluation records with scores and feedback summaries
- Document improvement records with before/after examples
- Context from previous operations

### Memory Lifecycle

- Memory is created when you first use a memory ID
- Each operation with the same memory ID builds on previous knowledge
- Memory persists indefinitely unless manually cleared

### Clearing Memory

To clear memory for a specific ID:

```python
from crewai.memory import CrewMemory

# Clear specific memory
memory = CrewMemory(memory_id="my-memory-id")
memory.clear()
```

## Advanced Usage

### Evaluator and Improver Memory Separation

For auto-improvement loops, separate memory IDs are automatically created for the evaluator and improver agents:

- `{memory_id}_evaluator`: Stores evaluation history
- `{memory_id}_improver`: Stores improvement history

This separation allows each agent to specialize in its specific task while still maintaining persistent knowledge.

### Memory for Teams of Specialized Agents

For more complex documentation projects, you can create specialized memory IDs:

```python
# Technical documentation team
tech_docs_evaluator = "tech_docs_evaluator"
tech_docs_improver = "tech_docs_improver"

# Marketing documentation team
marketing_docs_evaluator = "marketing_docs_evaluator"
marketing_docs_improver = "marketing_docs_improver"

# Use appropriate memory for each document type
if is_technical_doc(doc_path):
    auto_improve_document(doc_path, memory_id=tech_docs_evaluator)
else:
    auto_improve_document(doc_path, memory_id=marketing_docs_evaluator)
```

## Benefits of Persistent Memory

1. **Consistency**: Agents maintain a consistent evaluation and improvement approach
2. **Learning**: Performance improves over time as agents learn from previous documents
3. **Specialization**: Memory can be specialized for different document types
4. **Efficiency**: Repeated patterns in documentation issues can be addressed more efficiently

By leveraging persistent memory, your document evaluation and improvement processes will become more effective and consistent over time.