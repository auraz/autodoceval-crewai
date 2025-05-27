"""Test DocumentCrew methods."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from evcrew.crew import DocumentCrew


def mock_crew(test_func):
    """Decorator to mock CrewAI Crew class to avoid API key issues."""
    def wrapper(*args, **kwargs):
        with patch('evcrew.crew.Crew') as mock_crew_class:
            mock_crew_instance = Mock()
            mock_crew_class.return_value = mock_crew_instance
            return test_func(*args, **kwargs)
    return wrapper


class MockAgent:
    """Mock agent for testing."""
    def __init__(self, name):
        self.name = name


class MockTask:
    """Mock task for testing."""
    def __init__(self):
        self.context = []
        self.pydantic = None


@mock_crew
def test_document_crew_init():
    """Test DocumentCrew initialization."""
    crew = DocumentCrew(target_score=90, max_iterations=3)
    assert crew.target_score == 90
    assert crew.max_iterations == 3
    assert crew.evaluator is not None
    assert crew.improver is not None
    assert crew.crew is not None


@mock_crew
def test_document_crew_with_extra_prompts():
    """Test DocumentCrew with extra prompts."""
    crew = DocumentCrew(
        evaluator_extra_prompt="Focus on clarity",
        improver_extra_prompt="Add examples"
    )
    assert crew.evaluator.extra_prompt == "Focus on clarity"
    assert crew.improver.extra_prompt == "Add examples"


@mock_crew
@patch('evcrew.agents.evaluator.DocumentEvaluator.execute')
def test_evaluate_one(mock_execute):
    """Test evaluate_one method."""
    mock_execute.return_value = (85, "Good documentation")
    
    crew = DocumentCrew()
    score, feedback = crew.evaluate_one("# Test Doc")
    
    assert score == 85
    assert feedback == "Good documentation"
    mock_execute.assert_called_once_with("# Test Doc")


@mock_crew
@patch('evcrew.agents.improver.DocumentImprover.execute')
def test_improve_one(mock_execute):
    """Test improve_one method."""
    mock_execute.return_value = "# Improved Doc"
    
    crew = DocumentCrew()
    improved = crew.improve_one("# Test Doc", "Add examples")
    
    assert improved == "# Improved Doc"
    mock_execute.assert_called_once_with("# Test Doc", "Add examples")


@patch('evcrew.agents.evaluator.DocumentEvaluator.create_task')
@patch('evcrew.agents.improver.DocumentImprover.create_task')
def test_evaluate_and_improve_one(mock_improve_task, mock_eval_task):
    """Test evaluate_and_improve_one method."""
    # Setup mocks
    eval_task = MockTask()
    improve_task = MockTask()
    mock_eval_task.return_value = eval_task
    mock_improve_task.return_value = improve_task
    
    with patch('evcrew.crew.Crew') as mock_crew_class:
        # Create a properly configured mock crew instance
        mock_crew_instance = Mock()
        mock_crew_class.return_value = mock_crew_instance
        
        # Mock kickoff result
        mock_result = Mock()
        mock_result.tasks_output = [
            Mock(pydantic=Mock(score=85, feedback="Good")),
            Mock(pydantic=Mock(improved_content="# Better Doc"))
        ]
        mock_crew_instance.kickoff.return_value = mock_result
        
        crew = DocumentCrew()
        improved, score, feedback = crew.evaluate_and_improve_one("# Test Doc", "test")
    
    assert improved == "# Better Doc"
    assert score == 85
    assert feedback == "Good"
    assert improve_task.context == [eval_task]


@mock_crew
def test_auto_improve_one():
    """Test auto_improve_one method with mocked agents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        crew = DocumentCrew()
        
        # Mock the evaluator and improver execute methods
        with patch.object(crew.evaluator, 'execute', side_effect=[(60, "Initial feedback"), (85, "Good!")]), \
             patch.object(crew.improver, 'execute', return_value="# Improved Doc"):
                result = crew.auto_improve_one("# Test Doc", temp_dir, "test", "test.md")
                
                # Check that iterator was returned
                assert hasattr(result, 'final_content')
                assert hasattr(result, 'final_score')
                assert result.final_score == 85
                
                # Check files were created
                final_file = Path(temp_dir) / "test_final.md"
                assert final_file.exists()
                
                results_file = Path(temp_dir) / "test_results.json"
                assert results_file.exists()