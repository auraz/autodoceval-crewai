"""Test document processing iterator."""

import pytest
from pathlib import Path
import tempfile

from evcrew.process import DocumentIterator
from evcrew.agents import DocumentEvaluator, DocumentImprover


class MockEvaluator:
    """Mock evaluator for testing."""
    def __init__(self, scores):
        self.scores = scores
        self.call_count = 0
    
    def execute(self, content):
        score = self.scores[min(self.call_count, len(self.scores) - 1)]
        self.call_count += 1
        return score, f"Feedback for iteration {self.call_count}"


class MockImprover:
    """Mock improver for testing."""
    def __init__(self):
        self.call_count = 0
    
    def execute(self, content, feedback):
        self.call_count += 1
        return f"{content}\nImproved {self.call_count} times"


def test_document_iterator_success():
    """Test iterator reaching target score."""
    evaluator = MockEvaluator([60, 75, 90])  # Reaches target on 3rd iteration
    improver = MockImprover()
    
    iterator = DocumentIterator(
        evaluator, improver, "test_doc", "test.md", 
        "Initial content", target_score=85, max_iterations=5
    )
    
    iterations = list(iterator)
    # Iterator includes initial evaluation + improvements until target reached
    assert len(iterations) == 2  # Initial eval + 2 improvements (target reached at 90)
    assert iterator.final_score == 90
    assert "Improved 2 times" in iterator.final_content


def test_document_iterator_max_iterations():
    """Test iterator hitting max iterations."""
    evaluator = MockEvaluator([60, 65, 70])  # Never reaches target
    improver = MockImprover()
    
    iterator = DocumentIterator(
        evaluator, improver, "test_doc", "test.md",
        "Initial content", target_score=85, max_iterations=2
    )
    
    iterations = list(iterator)
    # Initial eval + 2 improvements (max iterations)
    assert len(iterations) == 3
    assert iterator.final_score == 70
    assert "Improved 2 times" in iterator.final_content


def test_document_iterator_already_good():
    """Test iterator when initial score exceeds target."""
    evaluator = MockEvaluator([95])  # Already exceeds target
    improver = MockImprover()
    
    iterator = DocumentIterator(
        evaluator, improver, "test_doc", "test.md",
        "Great content", target_score=85, max_iterations=5
    )
    
    try:
        list(iterator)
    except StopIteration:
        pass
    
    assert len(iterator._iterations) == 1
    assert iterator.final_score == 95
    assert iterator.final_content == "Great content"  # No improvements made


def test_document_iterator_save_results():
    """Test saving iteration results."""
    with tempfile.TemporaryDirectory() as temp_dir:
        evaluator = MockEvaluator([60, 90])
        improver = MockImprover()
        
        iterator = DocumentIterator(
            evaluator, improver, "test_doc", "test.md",
            "Initial content", target_score=85, max_iterations=5
        )
        
        # Run iterations
        list(iterator)
        
        # Save results
        output_dir = Path(temp_dir)
        iterator.save_results(output_dir, "success")
        
        # Check saved files
        results_file = output_dir / "test_doc_results.json"
        assert results_file.exists()
        
        content = results_file.read_text()
        assert "test_doc" in content
        assert "60" in str(content)  # Initial score
        assert "90" in str(content)  # Final score
        assert "success" in content


def test_document_iterator_no_improvement():
    """Test iterator when score doesn't improve."""
    evaluator = MockEvaluator([60, 60, 60])  # No improvement
    improver = MockImprover()
    
    iterator = DocumentIterator(
        evaluator, improver, "test_doc", "test.md",
        "Initial content", target_score=85, max_iterations=2
    )
    
    iterations = list(iterator)
    assert len(iterations) == 3  # Initial eval + 2 improvements
    assert iterator.final_score == 60
    assert iterator.total_improvement == 0