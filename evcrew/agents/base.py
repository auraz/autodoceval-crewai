import json
import os
from contextlib import suppress
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
    
    def execute_task(self, task_description: str) -> str:
        """Execute a task and return the agent's response."""
        task_instance = Task(description=task_description, expected_output="")
        return self.agent.execute_task(task_instance)
    
    def add_memory_entry(self, entry: str) -> None:
        """Add an entry to agent's memory."""
        self.agent.memory.add(entry)
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text to specified length with ellipsis."""
        return (text[:max_length] + "...") if len(text) > max_length else text


def parse_agent_response(response: str) -> tuple[float, str]:
    """Parse JSON agent response to extract score and feedback."""
    try:
        data = json.loads(response.strip())
        score = float(data.get("score", 0.0))
        feedback = str(data.get("feedback", ""))
        return score, feedback
    except (json.JSONDecodeError, ValueError, TypeError):
        # Fallback to old format for compatibility
        lines = response.splitlines()
        score = 0.0
        feedback_lines = []
        
        for i, line in enumerate(lines):
            if line.startswith("Score:"):
                with suppress(ValueError):
                    score = float(line[len("Score:"):].strip())
            elif line.startswith("Feedback:"):
                feedback_lines = [line[len("Feedback:"):].strip()]
                feedback_lines.extend(line.strip() for line in lines[i + 1:] if line.strip())
                break
        
        return score, "\n".join(feedback_lines)


def parse_improver_response(response: str) -> str:
    """Parse JSON improver response to extract improved content."""
    try:
        data = json.loads(response.strip())
        return str(data.get("improved_content", response))
    except (json.JSONDecodeError, ValueError, TypeError):
        # Fallback to raw response if not JSON
        return response.strip()
