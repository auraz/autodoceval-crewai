"""Test save methods for agents."""

import json
import tempfile
from pathlib import Path

from evcrew.agents import DocumentEvaluator, DocumentImprover


def test_evaluator_save():
    """Test DocumentEvaluator save method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        evaluator = DocumentEvaluator()
        output_dir = Path(temp_dir)
        
        # Test saving evaluation results
        evaluator.save(
            score=85,
            feedback="Good documentation with clear examples",
            content="# Test Doc\nThis is a test document.",
            output_dir=output_dir,
            doc_name="test_doc",
            input_path="test.md"
        )
        
        # Check that files were created
        eval_file = output_dir / "test_doc_evaluation.json"
        assert eval_file.exists()
        
        # Verify content
        data = json.loads(eval_file.read_text())
        assert data["document"] == "test_doc"
        assert data["evaluation"]["score"] == 85
        assert data["evaluation"]["feedback"] == "Good documentation with clear examples"
        assert data["input_path"] == "test.md"


def test_improver_save():
    """Test DocumentImprover save method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        improver = DocumentImprover()
        output_dir = Path(temp_dir)
        
        # Test saving improvement results
        improver.save(
            original_content="# Test Doc",
            improved_content="# Test Doc\n\nThis is an improved document with examples.",
            score=90,
            feedback="Added examples and improved structure",
            output_dir=output_dir,
            doc_name="test_doc",
            input_path="test.md"
        )
        
        # Check that files were created
        improved_file = output_dir / "test_doc_improved.json"
        assert improved_file.exists()
        
        # Verify JSON content
        data = json.loads(improved_file.read_text())
        assert data["document"] == "test_doc"
        assert data["improved"]["score"] == 90
        assert "This is an improved document with examples" in data["improved"]["content"]
        
        # Check markdown file
        md_file = output_dir / "test_doc_improved.md"
        assert md_file.exists()
        assert "This is an improved document with examples" in md_file.read_text()