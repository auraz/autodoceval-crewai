from typing import Optional

from crewai import Task

from .base import BaseAgent, EvaluationResult


class DocumentEvaluator(BaseAgent):
    """Document evaluation agent using CrewAI."""

    def __init__(self):
        super().__init__(
            role="Document Quality Evaluator",
            goal="Evaluate document clarity and provide constructive feedback",
            backstory="You are an expert technical writer with years of experience evaluating documentation quality",
        )

    def create_task(self, content: str, **kwargs) -> Task:
        """Create evaluation task for the given content."""
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

    def save_evaluation(self, score: float, feedback: str, output_dir, doc_name: str, input_content: Optional[str] = None) -> None:
        """Save evaluation results using base class method."""
        results = {"score": f"{score:.1f}%", "feedback": feedback}
        metadata = {"input_length": len(input_content)} if input_content else {}
        super().save_results(results, output_dir, doc_name, **metadata)
