import json
import os
from datetime import datetime
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from pydantic import BaseModel


class EvaluationResult(BaseModel):
    """Structured output for document evaluation."""
    score: float
    feedback: str

class ImprovementResult(BaseModel):
    """Structured output for document improvement."""
    improved_content: str


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
            verbose=False,
            llm_model="gpt-4",
        )
        self.memory_dir = Path("docs") / "memory" / memory_id
        self.memory_dir.mkdir(parents=True, exist_ok=True)
     
    def exec(self, task_desc: str, output_model: type[BaseModel] | None = None) -> BaseModel | str:
        """Execute task and return response using a crew with memory."""
        if output_model:
            task = Task(
                description=task_desc, 
                expected_output="Structured output",
                agent=self.agent,
                output_pydantic=output_model
            )
        else:
            task = Task(description=task_desc, expected_output="", agent=self.agent)
        
        crew = Crew(
            agents=[self.agent], 
            tasks=[task], 
            process=Process.sequential,
            memory=True,
            embedder={
                "provider": "openai",
                "config": {"model": "text-embedding-3-small"}
            },
            verbose=False
        )
        result = crew.kickoff()
        
        if output_model:
            return result.tasks_output[0].pydantic
        return str(result.raw)
    
    def _save_memory(self, entry: str) -> None:
        """Save memory entry to MD file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.memory_dir / f"{timestamp}.md"
        filename.write_text(entry)


