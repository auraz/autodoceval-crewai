from typing import Optional

from .base import BaseAgent, parse_agent_response


class DocumentEvaluator(BaseAgent):
    """Document evaluation agent using CrewAI."""

    def __init__(self, memory_id: str, api_key: Optional[str] = None):
        super().__init__(
            memory_id=memory_id,
            role="Document Quality Evaluator",
            goal="Evaluate document clarity and provide constructive feedback",
            backstory="You are an expert technical writer with years of experience evaluating documentation quality",
            api_key=api_key,
        )

    def evaluate(self, content: str) -> tuple[float, str]:
        """Evaluate a document and return a score and feedback string."""
        task_description = (
            "Evaluate the following document for clarity, completeness, and coherence.\n"
            "Score it on a scale from 0.0 to 1.0 where 1.0 is perfect.\n"
            "Provide specific, actionable feedback for improvement.\n\n"
            f"Document:\n{content}\n\n"
            "Your response MUST be valid JSON in this exact format:\n"
            '{"score": <number between 0.0 and 1.0>, "feedback": "<detailed feedback>"}'
        )

        memory_context = "Before evaluating, review your previous evaluations for similar documents. Maintain consistency in feedback style and acknowledge progress compared to earlier versions.\n\n"
        task_description = memory_context + task_description
        
        response = self.execute_task(task_description)
        score, feedback = parse_agent_response(response)

        content_preview = self.truncate_text(content)
        feedback_preview = self.truncate_text(feedback, 200)
        memory_entry = f"Document: {content_preview}\nScore: {score}\nFeedback: {feedback_preview}..."
        self.add_memory_entry(memory_entry)

        return score, feedback.strip()
