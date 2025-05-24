from .base import BaseAgent, EvaluationResult


class DocumentEvaluator(BaseAgent):
    """Document evaluation agent using CrewAI."""

    def __init__(self, memory_id: str):
        super().__init__(
            memory_id=memory_id,
            role="Document Quality Evaluator",
            goal="Evaluate document clarity and provide constructive feedback",
            backstory="You are an expert technical writer with years of experience evaluating documentation quality",
        )

    def evaluate(self, content: str) -> tuple[float, str]:
        """Evaluate a document and return a score and feedback string."""
        prompt_path = self.prompts_dir / "evaluator.md"
        prompt_template = prompt_path.read_text()
        task_description = prompt_template.format(content=content)
        
        result = self.exec(task_description, EvaluationResult)
        return result.score, result.feedback.strip()
