import os
from pathlib import Path

from crewai import Agent, Task
from pydantic import BaseModel


class EvaluationResult(BaseModel):
    """Structured output for document evaluation."""

    score: float
    feedback: str


class ImprovementResult(BaseModel):
    """Structured output for document improvement."""

    improved_content: str


class BaseAgent:
    """Base class for CrewAI agents with common initialization and task execution."""

    def __init__(self, role: str, goal: str, backstory: str):
        """Initialize base agent with CrewAI configuration."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.prompts_dir = Path(__file__).parent / "prompts"
        self.agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=False,
            llm_model="gpt-4",
        )

    def execute(self, task_desc: str, output_model: type[BaseModel]) -> BaseModel:
        """Execute a single task and return structured response."""
        task = Task(description=task_desc, expected_output="Structured output", agent=self.agent, output_pydantic=output_model)
        return task.execute_sync().pydantic
