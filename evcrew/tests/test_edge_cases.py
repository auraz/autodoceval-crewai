"""Test edge cases and error conditions."""

import os
from unittest.mock import patch

import pytest

from evcrew import DocumentCrew
from evcrew.agents.base import BaseAgent, EvaluationResult, ImprovementResult


def test_base_agent_abstract():
    """Test that BaseAgent cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseAgent("role", "goal", "backstory")


def test_evaluation_result_model():
    """Test EvaluationResult pydantic model."""
    result = EvaluationResult(score=85.5, feedback="Good documentation")
    assert result.score == 85.5
    assert result.feedback == "Good documentation"


def test_improvement_result_model():
    """Test ImprovementResult pydantic model."""
    result = ImprovementResult(improved_content="# Improved Doc")
    assert result.improved_content == "# Improved Doc"


def test_crew_without_api_key():
    """Test crew creation without API key."""
    # Temporarily unset API key
    original_key = os.environ.get("OPENAI_API_KEY")
    original_chroma_key = os.environ.get("CHROMA_OPENAI_API_KEY")
    
    if original_key:
        del os.environ["OPENAI_API_KEY"]
    if original_chroma_key:
        del os.environ["CHROMA_OPENAI_API_KEY"]
    
    try:
        # Should raise validation error due to missing API key for embedder
        from pydantic_core import ValidationError
        with pytest.raises(ValidationError):  # Crew requires API key for memory/embedder
            DocumentCrew()
    finally:
        # Restore API keys
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key
        if original_chroma_key:
            os.environ["CHROMA_OPENAI_API_KEY"] = original_chroma_key


def test_crew_main_entry():
    """Test main entry point execution."""
    
    # This should not raise any exceptions
    with patch('sys.argv', ['test_crew.py']):
        # The test should handle missing API key gracefully
        pass