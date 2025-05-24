import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from crewai import Agent, Task
from pydantic import BaseModel


class EvaluationResult(BaseModel):
    """Structured output for document evaluation."""

    score: float
    feedback: str


class ImprovementResult(BaseModel):
    """Structured output for document improvement."""

    improved_content: str


class BaseAgent(ABC):
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

    @abstractmethod
    def create_task(self, content: str, **kwargs) -> Task:
        """Create a task for the agent to execute."""
        pass

    def save_results(self, results: dict[str, Any], output_dir: Path, doc_name: str, **metadata: Any) -> None:
        """Save results to disk with metadata."""
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        for key, value in results.items():
            file_path = output_dir / f"{doc_name}_{key}.txt"
            file_path.write_text(str(value))
        meta = {"document": doc_name, "timestamp": timestamp, **results, **metadata}
        metadata_path = output_dir / f"{doc_name}_metadata.json"
        metadata_path.write_text(json.dumps(meta, indent=2))
