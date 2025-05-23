import os

from crewai import Agent, Task
from crewai.memory import Memory as CrewMemory

from .base import parse_improver_response


class DocumentImprover:
    """Document improvement agent using CrewAI."""

    def __init__(self, memory_id: str, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.memory_id = memory_id
        memory_instance = CrewMemory(memory_id=memory_id)
        self.agent = Agent(
            role="Documentation Improver",
            goal="Transform documents into clear, comprehensive, and well-structured content",
            backstory="You are a senior technical writer who specializes in improving documentation",
            verbose=True,
            llm_model="gpt-4",
            memory=memory_instance,
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
        task_instance = Task(description=task_description, expected_output="")  # Create task for agent execution
        response = self.agent.execute_task(task_instance)
        result = parse_improver_response(response)

        if self.agent.memory:
            content_preview = (content[:100] + "...") if len(content) > 100 else content
            improved_preview = (result[:100] + "...") if len(result) > 100 else result
            memory_entry = f"Original: {content_preview}\nImproved: {improved_preview}\nBased on feedback: {feedback[:200]}..."
            self.agent.memory.add(memory_entry)

        return result
