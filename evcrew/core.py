"""Simple agent wrappers for backward compatibility."""

from .agents import DocumentEvaluator, DocumentImprover

__all__ = ["evaluate_document", "improve_document"]


def evaluate_document(doc_content: str) -> tuple[float, str]:
    """Evaluate document for clarity and return score with reasoning."""
    evaluator = DocumentEvaluator()
    return evaluator.execute(doc_content)


def improve_document(doc_content: str, feedback: str) -> str:
    """Generate improved document based on evaluation feedback."""
    improver = DocumentImprover()
    return improver.execute(doc_content, feedback)