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
     
    def exec(self, task_desc: str) -> str:
        """Execute task and return response."""
        task = Task(description=task_desc, expected_output="")
        return self.agent.execute_task(task)
    
    @staticmethod
    def truncate(text: str, max_len: int = 100) -> str:
        """Truncate text to max length."""
        return (text[:max_len] + "...") if len(text) > max_len else text


def parse_eval(response: str) -> tuple[float, str]:
    """Parse evaluator JSON response."""
    data = json.loads(response.strip())
    return float(data["score"]), str(data["feedback"])


def parse_improve(response: str) -> str:
    """Parse improver JSON response."""
    data = json.loads(response.strip())
    return str(data["improved_content"])
