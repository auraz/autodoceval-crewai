import json
import os
from datetime import datetime
from pathlib import Path

from crewai import Agent, Crew, Task
from pydantic import BaseModel


class AgentResult(BaseModel):
    score: float = 0.0
    content: str = ""
    feedback: str = ""


class BaseAgent:
    """Base class for CrewAI agents with common initialization and task execution."""
    
    def __init__(self, memory_id: str, role: str, goal: str, backstory: str):
        """Initialize base agent with CrewAI configuration."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.memory_id = memory_id
        self.prompts_dir = Path(__file__).parent / "prompts"
        self.agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            llm_model="gpt-4",
        )
        self.memory_dir = Path("memory") / memory_id
        self.memory_dir.mkdir(parents=True, exist_ok=True)
     
    def exec(self, task_desc: str) -> str:
        """Execute task and return response using a crew with memory."""
        task = Task(description=task_desc, expected_output="", agent=self.agent)
        crew = Crew(agents=[self.agent], tasks=[task], memory=True, verbose=True)
        result = crew.kickoff()
        return str(result.raw)
    
    def _save_memory(self, entry: str) -> None:
        """Save memory entry to MD file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.memory_dir / f"{timestamp}.md"
        filename.write_text(entry)


def parse_eval(response: str) -> tuple[float, str]:
    """Parse evaluator JSON response."""
    lines = response.strip().split('\n')
    json_line = next((line for line in lines if line.strip().startswith('{')), None)
    if not json_line:
        raise ValueError("No JSON found in response")
    data = json.loads(json_line.strip())
    return float(data["score"]), str(data["feedback"])


def parse_improve(response: str) -> str:
    """Parse improver JSON response."""
    lines = response.strip().split('\n')
    json_line = next((line for line in lines if line.strip().startswith('{')), None)
    if not json_line:
        raise ValueError("No JSON found in response")
    data = json.loads(json_line.strip())
    return str(data["improved_content"])
