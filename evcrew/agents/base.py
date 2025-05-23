import json
import os
from datetime import datetime
from pathlib import Path
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
        self.memory_dir = Path("memory") / memory_id
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.add_memory = self._save_memory  # Override to save to file
     
    def exec(self, task_desc: str) -> str:
        """Execute task and return response."""
        task = Task(description=task_desc, expected_output="")
        return self.agent.execute_task(task)
    
    def _save_memory(self, entry: str) -> None:
        """Save memory entry to MD file and agent memory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.memory_dir / f"{timestamp}.md"
        filename.write_text(entry)
        self.agent.memory.add(entry)


def parse_eval(response: str) -> tuple[float, str]:
    """Parse evaluator JSON response."""
    data = json.loads(response.strip())
    return float(data["score"]), str(data["feedback"])


def parse_improve(response: str) -> str:
    """Parse improver JSON response."""
    data = json.loads(response.strip())
    return str(data["improved_content"])
