"""Test base agent functionality."""

from unittest.mock import Mock, patch

import pytest
from crewai import Task

from evcrew.agents.base import BaseAgent, EvaluationResult


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""
    
    def create_task(self, content: str, **kwargs) -> Task:
        """Create a test task."""
        return Task(
            description="Test task",
            expected_output="Test output",
            agent=self.agent
        )
    
    def save(self, *args, **kwargs) -> None:
        """Save test results."""
        pass


def test_base_agent_execute():
    """Test BaseAgent execute method."""
    with patch('evcrew.agents.base.Task') as mock_task_class:
        # Create mock task instance
        mock_task = Mock()
        mock_result = Mock()
        mock_result.pydantic = EvaluationResult(score=85, feedback="Good")
        mock_task.execute_sync.return_value = mock_result
        mock_task_class.return_value = mock_task
        
        # Create agent and execute
        agent = ConcreteAgent("Test Role", "Test Goal", "Test Backstory")
        result = agent.execute("Test description", EvaluationResult)
        
        # Verify
        assert isinstance(result, EvaluationResult)
        assert result.score == 85
        assert result.feedback == "Good"
        mock_task_class.assert_called_once()
        mock_task.execute_sync.assert_called_once()


def test_base_agent_abstract_methods():
    """Test that BaseAgent cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseAgent("role", "goal", "backstory")


def test_concrete_agent_methods():
    """Test concrete agent implementation."""
    agent = ConcreteAgent("Test Role", "Test Goal", "Test Backstory")
    
    # Test create_task
    task = agent.create_task("Test content")
    assert isinstance(task, Task)
    assert task.description == "Test task"
    
    # Test save (should not raise)
    agent.save("test", "data")