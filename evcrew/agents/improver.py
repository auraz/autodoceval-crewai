from .base import BaseAgent, ImprovementResult


class DocumentImprover(BaseAgent):
    """Document improvement agent using CrewAI."""

    def __init__(self):
        super().__init__(
            role="Documentation Improver",
            goal="Transform documents into clear, comprehensive, and well-structured content",
            backstory="You are a senior technical writer who specializes in improving documentation",
        )
    
    def create_task(self, content: str, feedback: str = None):
        """Create improvement task for the given content."""
        from crewai import Task
        
        prompt_path = self.prompts_dir / "improver.md"
        # If feedback is provided, use it; otherwise it will come from context
        if feedback:
            description = prompt_path.read_text().format(content=content, feedback=feedback)
        else:
            description = f"Improve the document based on the evaluation feedback:\n\n{content}"
        
        return Task(
            description=description,
            expected_output="Improved version of the document",
            agent=self.agent,
            output_pydantic=ImprovementResult
        )

    def execute(self, content: str, feedback: str) -> str:
        """Execute document improvement based on feedback."""
        prompt_path = self.prompts_dir / "improver.md"
        prompt_template = prompt_path.read_text()
        task_description = prompt_template.format(content=content, feedback=feedback)
        
        result = super().execute(task_description, ImprovementResult)
        return result.improved_content
