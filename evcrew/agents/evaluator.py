import os
from typing import Optional, Tuple

from crewai import Agent, Task

from .base import create_memory_instance, parse_agent_response

class DocumentEvaluator:
    """Document evaluation agent using CrewAI."""
    
    def __init__(self, api_key: Optional[str] = None, memory_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        memory_instance = create_memory_instance(memory_id)
        self.agent = Agent(
            role="Document Quality Evaluator",
            goal="Evaluate document clarity and provide constructive feedback",
            backstory="You are an expert technical writer with years of experience evaluating documentation quality",
            verbose=True,
            llm_model="gpt-4",
            memory=memory_instance,
        )
        self.memory_id = memory_id
        
    def evaluate(self, content: str) -> Tuple[float, str]:
        """Evaluate a document and return a score and feedback string."""
        task_description = (
            "Evaluate the following document for clarity, completeness, and coherence.\n"
            "Score it on a scale from 0.0 to 1.0 where 1.0 is perfect.\n"
            "Provide specific, actionable feedback for improvement.\n\n"
            f"Document:\n{content}\n\n"
            "Your response must be in this format:\n"
            "Score: <score between 0.0 and 1.0>\n"
            "Feedback: <detailed feedback>"
        )
        
        if self.memory_id:
            memory_context = (
                "Before evaluating, review your previous evaluations for similar documents. "
                "Consider patterns you've seen before and maintain consistency in your feedback style. "
                "If you notice this document has improved from previous versions, acknowledge that progress.\n\n"
            )
            task_description = memory_context + task_description
        
        # Create a Task object with the prompt keyword.
        task_instance = Task(description=task_description, expected_output="")
        response = self.agent.execute_task(task_instance)
        score, feedback = parse_agent_response(response)
        
        if self.memory_id and self.agent.memory:
            content_preview = (content[:100] + "...") if len(content) > 100 else content
            memory_entry = f"Document: {content_preview}\nScore: {score}\nFeedback: {feedback[:200]}..."
            self.agent.memory.add(memory_entry)
            
        return score, feedback.strip()
