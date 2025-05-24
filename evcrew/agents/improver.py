from .base import BaseAgent, ImprovementResult


class DocumentImprover(BaseAgent):
    """Document improvement agent using CrewAI."""

    def __init__(self, memory_id: str):
        super().__init__(
            memory_id=memory_id,
            role="Documentation Improver",
            goal="Transform documents into clear, comprehensive, and well-structured content",
            backstory="You are a senior technical writer who specializes in improving documentation",
        )

    def improve(self, content: str, feedback: str) -> str:
        """Generate an improved document based on feedback."""
        prompt_path = self.prompts_dir / "improver.md"
        prompt_template = prompt_path.read_text()
        task_description = prompt_template.format(content=content, feedback=feedback)
        
        result = self.exec(task_description, ImprovementResult)
        
        memory_entry = f"Original: {content}\nImproved: {result.improved_content}\nBased on feedback: {feedback}"
        self._save_memory(memory_entry)

        return result.improved_content
