from typing import Optional

from .base import BaseAgent, parse_improver_response


class DocumentImprover(BaseAgent):
    """Document improvement agent using CrewAI."""

    def __init__(self, memory_id: str, api_key: Optional[str] = None):
        super().__init__(
            memory_id=memory_id,
            role="Documentation Improver",
            goal="Transform documents into clear, comprehensive, and well-structured content",
            backstory="You are a senior technical writer who specializes in improving documentation",
            api_key=api_key,
        )

    def improve(self, content: str, feedback: str) -> str:
        """Generate an improved document based on feedback."""
        task_description = (
            "Improve the following document based on the provided feedback.\n"
            "Make the document more clear, complete, and coherent.\n\n"
            f"Original Document:\n{content}\n\n"
            f"Feedback:\n{feedback}\n\n"
            "Your response MUST be valid JSON in this exact format:\n"
            '{"improved_content": "<the complete improved document>"}'
        )

        memory_guidance = "Before improving this document, review your memory of previous document improvements. Reuse effective techniques, keep consistent style/terminology, and address recurring issues.\n\n"
        task_description = memory_guidance + task_description
        
        response = self.execute_task(task_description)
        result = parse_improver_response(response)

        content_preview = self.truncate_text(content)
        improved_preview = self.truncate_text(result)
        feedback_preview = self.truncate_text(feedback, 200)
        memory_entry = f"Original: {content_preview}\nImproved: {improved_preview}\nBased on feedback: {feedback_preview}..."
        self.add_memory_entry(memory_entry)

        return result
