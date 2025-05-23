#!/usr/bin/env python3
"""
Memory Demo for AutoDocEval with CrewAI

This script demonstrates how to use persistent memory capabilities in
the CrewAI implementation of AutoDocEval for document evaluation and improvement.
"""

from pathlib import Path

# Import AutoDocEval CrewAI modules
from evcrew import evaluate_document, improve_document


# Utility functions
def format_percentage(value: float) -> str:
    """Format float as percentage string."""
    return f"{value * 100:.1f}%"

def read_file(file_path: str) -> str:
    """Read file and return its contents."""
    return Path(file_path).read_text(encoding="utf-8")

def write_file(file_path: str, content: str) -> None:
    """Write content to file, creating directories if needed."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

# ===============================================================
# Create sample documents with different levels of quality
# ===============================================================

# Create a directory for the examples
EXAMPLES_DIR = Path("memory_examples")
EXAMPLES_DIR.mkdir(exist_ok=True)

# Poor quality document
POOR_QUALITY_DOC = """
# API Documentation

This docs explains API. You can use it to get data.

## Endpoints

/users - Gets user data
/items - Gets items

## Authentication

Use token in header.

## Examples

Use curl to call the API.
"""

# Medium quality document
MEDIUM_QUALITY_DOC = """
# API Documentation

This documentation explains how to use the REST API for data retrieval.

## Authentication

Authentication is required for all endpoints. Include a token in the Authorization header.

## Endpoints

### /users
Gets user data in JSON format.
Parameters: id (optional) - Filter by user ID

### /items
Retrieves items from the database.
Parameters:
- type: Filter by item type
- sort: Sort order (asc or desc)

## Examples

```
curl -H "Authorization: Bearer TOKEN" https://api.example.com/users
```
"""

# High quality document
HIGH_QUALITY_DOC = """
# API Documentation

This comprehensive guide explains how to use the REST API for data retrieval and manipulation.

## Authentication

Authentication is required for all API endpoints. Include your API token in the Authorization header:
```
Authorization: Bearer YOUR_API_TOKEN
```

You can obtain an API token by registering at https://api.example.com/register.

## Rate Limiting

The API is rate limited to 100 requests per minute. If you exceed this limit, you'll receive a 429 Too Many Requests response.

## Endpoints

### GET /users

Retrieves user data in JSON format.

**Parameters:**
- `id` (optional): Filter by user ID
- `limit` (optional): Maximum number of results (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "users": [
    {
      "id": 123,
      "name": "John Doe",
      "email": "john@example.com"
    }
  ],
  "total": 1
}
```

### GET /items

Retrieves items from the database.

**Parameters:**
- `type` (optional): Filter by item type (e.g., "book", "electronics")
- `sort` (optional): Sort order, either "asc" or "desc" (default: "asc")
- `limit` (optional): Maximum number of results (default: 20, max: 100)

**Response:**
```json
{
  "items": [
    {
      "id": 456,
      "name": "Sample Item",
      "price": 19.99,
      "type": "book"
    }
  ],
  "total": 1
}
```

## Error Handling

All errors are returned with appropriate HTTP status codes and a JSON response body:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Examples

Retrieve all users:
```
curl -H "Authorization: Bearer TOKEN" https://api.example.com/users
```

Retrieve a specific user:
```
curl -H "Authorization: Bearer TOKEN" https://api.example.com/users?id=123
```

Retrieve items of type "book":
```
curl -H "Authorization: Bearer TOKEN" https://api.example.com/items?type=book
```
"""

# Write sample documents to files
write_file(EXAMPLES_DIR / "poor_doc.md", POOR_QUALITY_DOC)
write_file(EXAMPLES_DIR / "medium_doc.md", MEDIUM_QUALITY_DOC)
write_file(EXAMPLES_DIR / "high_doc.md", HIGH_QUALITY_DOC)

print("=" * 80)
print("📚 Sample documents created in the memory_examples directory")
print("=" * 80)

# ===============================================================
# Evaluate documents with and without memory
# ===============================================================


# Define memory ID for this demo
MEMORY_ID = "api_docs_memory"

print("\n\n" + "=" * 80)
print("🧪 Experiment 1: Simple Document Evaluation with Memory")
print("=" * 80)

print("\n1️⃣ First evaluation (poor quality document):")
poor_doc = read_file(EXAMPLES_DIR / "poor_doc.md")

# Evaluate with memory
print("\n📝 Evaluating with memory...")
score1, feedback1 = evaluate_document(poor_doc, memory_id=MEMORY_ID)
print(f"Score: {format_percentage(score1)}")
print(f"Feedback sample: {feedback1[:100]}...")

print("\n2️⃣ Second evaluation (medium quality document):")
medium_doc = read_file(EXAMPLES_DIR / "medium_doc.md")

# Evaluate with the same memory
print("\n📝 Evaluating with memory (using previous experience)...")
score2, feedback2 = evaluate_document(medium_doc, memory_id=MEMORY_ID)
print(f"Score: {format_percentage(score2)}")
print(f"Feedback sample: {feedback2[:100]}...")

print("\n3️⃣ Third evaluation (high quality document):")
high_doc = read_file(EXAMPLES_DIR / "high_doc.md")

# Evaluate with the same memory
print("\n📝 Evaluating with memory (using accumulated experience)...")
score3, feedback3 = evaluate_document(high_doc, memory_id=MEMORY_ID)
print(f"Score: {format_percentage(score3)}")
print(f"Feedback sample: {feedback3[:100]}...")

# ===============================================================
# Demonstrate memory in document improvement
# ===============================================================

print("\n\n" + "=" * 80)
print("🧪 Experiment 2: Document Improvement with Memory")
print("=" * 80)

# Improve the poor document with memory
print("\n1️⃣ Improving poor document with memory...")
improved_poor = improve_document(poor_doc, feedback1, memory_id=MEMORY_ID)
write_file(EXAMPLES_DIR / "poor_improved_with_memory.md", improved_poor)

# Evaluate the improved document
print("\n📊 Evaluating the memory-improved document...")
improved_score, improved_feedback = evaluate_document(improved_poor, memory_id=MEMORY_ID)
print(f"Original score: {format_percentage(score1)}")
print(f"Improved score: {format_percentage(improved_score)}")
print(f"Improvement: {format_percentage(improved_score - score1)}")

# Now improve without memory for comparison
print("\n2️⃣ Improving poor document without memory (for comparison)...")
improved_poor_no_memory = improve_document(poor_doc, feedback1)
write_file(EXAMPLES_DIR / "poor_improved_no_memory.md", improved_poor_no_memory)

# Evaluate the improved document (without memory)
print("\n📊 Evaluating the non-memory improved document...")
improved_score_no_memory, _ = evaluate_document(improved_poor_no_memory)
print(f"Original score: {format_percentage(score1)}")
print(f"Improved score (no memory): {format_percentage(improved_score_no_memory)}")
print(f"Improvement: {format_percentage(improved_score_no_memory - score1)}")

# ===============================================================
# Demonstrate memory across different documents
# ===============================================================

print("\n\n" + "=" * 80)
print("🧪 Experiment 3: Memory Across Related Documents")
print("=" * 80)

# Create a related document
RELATED_DOC = """
# Authentication API

This document explains how to authenticate with our API.

## Getting a Token

Register at our website to get a token.

## Using the Token

Put the token in the header.

## Token Expiration

Tokens expire after 24 hours.
"""

write_file(EXAMPLES_DIR / "auth_doc.md", RELATED_DOC)
auth_doc = read_file(EXAMPLES_DIR / "auth_doc.md")

# First evaluate with a new memory ID
print("\n1️⃣ Evaluating authentication document with fresh memory...")
new_memory_id = "fresh_memory"
auth_score_fresh, auth_feedback_fresh = evaluate_document(auth_doc, memory_id=new_memory_id)
print(f"Score with fresh memory: {format_percentage(auth_score_fresh)}")
print(f"Feedback sample: {auth_feedback_fresh[:100]}...")

# Now evaluate with our existing API docs memory
print("\n2️⃣ Evaluating authentication document with existing API docs memory...")
auth_score_shared, auth_feedback_shared = evaluate_document(auth_doc, memory_id=MEMORY_ID)
print(f"Score with shared memory: {format_percentage(auth_score_shared)}")
print(f"Feedback sample: {auth_feedback_shared[:100]}...")

# Improve using the shared memory
print("\n3️⃣ Improving authentication document with shared memory...")
improved_auth = improve_document(auth_doc, auth_feedback_shared, memory_id=MEMORY_ID)
write_file(EXAMPLES_DIR / "auth_improved.md", improved_auth)

# ===============================================================
# Conclusion
# ===============================================================

print("\n\n" + "=" * 80)
print("🎯 Memory Demo Results")
print("=" * 80)

print("""
This demo has illustrated the benefits of persistent memory in document evaluation
and improvement:

1. The agent learned from multiple document evaluations, developing a consistent
   evaluation style and criteria across documents.

2. Document improvements benefited from accumulated knowledge about API documentation
   best practices.

3. The memory-enabled agent could recognize relationships between different but related
   documents (main API docs vs. authentication docs).

All improved documents and evaluation results are saved in the memory_examples directory.
You can examine them to see the differences in quality and consistency.
""")

print("\n✅ Memory demo completed successfully!")
