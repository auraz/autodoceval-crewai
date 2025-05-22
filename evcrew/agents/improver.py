import os
from typing import Optional

from crewai import Agent, Task

from .base import create_memory_instance

class DocumentImprover:
    """Document improvement agent using CrewAI."""
    
    def __init__(self, api_key: Optional[str] = None, memory_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        memory_instance = create_memory_instance(memory_id)
        self.agent = Agent(
            role="Documentation Improver",
            goal="Transform documents into clear, comprehensive, and well-structured content",
            backstory="You are a senior technical writer who specializes in improving documentation",
            verbose=True,
            llm_model="gpt-4",
            memory=memory_instance,
        )
        self.memory_id = memory_id
        
    def improve(self, content: str, feedback: str) -> str:
        """Generate an improved document based on feedback."""
        task_description = (
            "Improve the following document based on the provided feedback.\n"
            "Make the document more clear, complete, and coherent.\n\n"
            f"Original Document:\n{content}\n\n"
            f"Feedback:\n{feedback}\n\n"
            "Provide only the improved document as your response, without any additional commentary."
        )
        
        if self.memory_id:
            memory_context = (
                "Before improving this document, review your memory of previous document improvements. "
                "Consider what techniques worked well in past improvements, "
                "maintain a consistent style and terminology, and address recurring issues.\n\n"
            )
            task_description = memory_context + task_description
        
        # Create a Task object with the prompt keyword.
        task_instance = Task(description=task_description, expected_output="")
        result = self.agent.execute_task(task_instance)
        
        if self.memory_id and self.agent.memory:
            content_preview = (content[:100] + "...") if len(content) > 100 else content
            improved_preview = (result[:100] + "...") if len(result) > 100 else result
            memory_entry = f"Original: {content_preview}\nImproved: {improved_preview}\nBased on feedback: {feedback[:200]}..."
            self.agent.memory.add(memory_entry)
            
        return result.strip()
