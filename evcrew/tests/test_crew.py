#!/usr/bin/env python3
"""Test the DocumentCrew multi-agent workflow."""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from evcrew import DocumentCrew  # noqa: E402


def test_crew_workflow():
    """Test the evaluate_and_improve crew workflow."""
    from unittest.mock import patch, Mock
    
    # Mock the crew creation to avoid API key issues
    with patch('evcrew.crew.Crew') as mock_crew_class:
        # Create a mock crew instance
        mock_crew_instance = Mock()
        mock_crew_class.return_value = mock_crew_instance
        
        # Mock the kickoff result
        mock_result = Mock()
        mock_result.tasks_output = [
            Mock(pydantic=Mock(score=35, feedback="Needs improvement")),
            Mock(pydantic=Mock(improved_content="# Improved README\n\nThis is much better!"))
        ]
        mock_crew_instance.kickoff.return_value = mock_result
        
        # Create crew
        crew = DocumentCrew()
        
        # Run evaluate and improve workflow
        print("Running crew workflow on bad README...")
        improved_content, score, feedback = crew.evaluate_and_improve_one("Bad README content")

        print(f"\nOriginal score: {score:.1f}%")
        print(f"Feedback: {feedback}\n")
        print("Improved content:")
        print("-" * 80)
        print(improved_content)
        print("-" * 80)

        # Basic assertions
        assert score <= 50, f"Bad README should have low score, got {score}"
        assert len(improved_content) > len("Bad README content"), "Improved content should be longer"
        assert improved_content != "Bad README content", "Content should be different after improvement"

        print("\n✅ Crew workflow test passed!")


if __name__ == "__main__":
    # Ensure we have the OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    test_crew_workflow()
