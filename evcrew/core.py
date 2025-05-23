"""Simple agent wrappers for backward compatibility."""

from .agents import DocumentEvaluator, DocumentImprover

__all__ = ["evaluate_document", "improve_document"]


def evaluate_document(doc_content: str, memory_id: str) -> tuple[float, str]:
    """Evaluate document for clarity and return score with reasoning."""
    evaluator = DocumentEvaluator(memory_id)
    return evaluator.evaluate(doc_content)


def improve_document(doc_content: str, feedback: str, memory_id: str, previous_score: float | None = None) -> str:
    """Generate improved document based on evaluation feedback."""
    improver = DocumentImprover(memory_id)
    return improver.improve(doc_content, feedback)