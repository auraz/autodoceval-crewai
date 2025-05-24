import os
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
     
    def execute(self, task_desc: str, output_model: type[BaseModel]) -> BaseModel:
        """Execute a single task and return structured response."""
        task = Task(
            description=task_desc, 
            expected_output="Structured output",
            agent=self.agent,
            output_pydantic=output_model
        )
        
        # Single agent crew - simplified for individual tasks
        # Note: For sequential workflows like auto-improve, we execute
        # single-agent tasks one at a time rather than using a multi-agent crew
        crew = Crew(
            agents=[self.agent], 
            tasks=[task],
            verbose=False
        )
        result = crew.kickoff()
        
        return result.tasks_output[0].pydantic


