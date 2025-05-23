import json
import os
from typing import Optional

from crewai import Agent, Task
from crewai.memory import Memory as CrewMemory
from pydantic import BaseModel


class AgentResult(BaseModel):
    score: float = 0.0
    content: str = ""
    feedback: str = ""


class BaseAgent:
    """Base class for CrewAI agents with common initialization and task execution."""
    
    def __init__(self, memory_id: str, role: str, goal: str, backstory: str, api_key: Optional[str] = None):
        """Initialize base agent with CrewAI configuration."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.memory_id = memory_id
        memory_instance = CrewMemory(memory_id=memory_id)
        self.agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            llm_model="gpt-4",
            memory=memory_instance,
        )
        self.add_memory = self.agent.memory.add  # Direct reference to memory add method
    
    def execute_task(self, task_description: str) -> str:
        """Execute a task and return the agent's response."""
        task_instance = Task(description=task_description, expected_output="")
        return self.agent.execute_task(task_instance)
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text to specified length with ellipsis."""
        return (text[:max_length] + "...") if len(text) > max_length else text


def parse_agent_response(response: str) -> tuple[float, str]:
    """Parse JSON agent response to extract score and feedback."""
    data = json.loads(response.strip())
    score = float(data["score"])
    feedback = str(data["feedback"])
    return score, feedback


def parse_improver_response(response: str) -> str:
    """Parse JSON improver response to extract improved content."""
    data = json.loads(response.strip())
    return str(data["improved_content"])
