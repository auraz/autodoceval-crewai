import json
from datetime import datetime
from pathlib import Path

from .base import BaseAgent, EvaluationResult


class DocumentEvaluator(BaseAgent):
    """Document evaluation agent using CrewAI."""

    def __init__(self):
        super().__init__(
            role="Document Quality Evaluator",
            goal="Evaluate document clarity and provide constructive feedback",
            backstory="You are an expert technical writer with years of experience evaluating documentation quality",
        )

    def create_task(self, content: str):
        """Create evaluation task for the given content."""
        from crewai import Task

        prompt_path = self.prompts_dir / "evaluator.md"
        description = prompt_path.read_text().format(content=content)

        return Task(description=description, expected_output="Document evaluation with score and feedback", agent=self.agent, output_pydantic=EvaluationResult)

    def execute(self, content: str) -> tuple[float, str]:
        """Execute document evaluation and return a score and feedback string."""
        prompt_path = self.prompts_dir / "evaluator.md"
        prompt_template = prompt_path.read_text()
        task_description = prompt_template.format(content=content)

        result = super().execute(task_description, EvaluationResult)
        return result.score, result.feedback.strip()

    def save_results(self, score: float, feedback: str, output_dir: Path, doc_name: str, input_content: str = None) -> None:
        """Save evaluation results to disk with metadata."""
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        # Save score and feedback
        (output_dir / f"{doc_name}_score.txt").write_text(f"{score:.1f}%")
        (output_dir / f"{doc_name}_feedback.txt").write_text(feedback)

        # Save metadata
        metadata = {"document": doc_name, "timestamp": timestamp, "score": score, "feedback": feedback}
        if input_content:
            metadata["input_length"] = len(input_content)
        (output_dir / f"{doc_name}_metadata.json").write_text(json.dumps(metadata, indent=2))
