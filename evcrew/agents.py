"""Defines CrewAI agents for document evaluation and improvement."""

import os
from typing import Dict, Optional, Tuple

from crewai import Agent                                                               from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory       
from openai import OpenAI
from pydantic import BaseModel

class AgentResult(BaseModel):
    """Result from agent execution."""
    score: float = 0.0
    content: str = ""
    feedback: str = ""

class DocumentEvaluator:
    """Document evaluation agent using CrewAI."""
    
    def __init__(self, api_key: str = None, memory_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Create a memory instance if memory_id is provided
        memory = None
        if memory_id:
            memory = CrewMemory(memory_id=memory_id)
            
        self.agent = Agent(
            role="Document Quality Evaluator",
            goal="Evaluate document clarity and provide constructive feedback",
            backstory="You are an expert technical writer with years of experience evaluating documentation quality",
            verbose=True,
            llm_model="gpt-4",
            memory=memory
        )
        self.memory_id = memory_id
        
    def evaluate(self, content: str) -> Tuple[float, str]:
        """Evaluate document and return score and feedback."""
        task_description = f"""
        Evaluate the following document for clarity, completeness, and coherence.
        Score it on a scale from 0.0 to 1.0 where 1.0 is perfect.
        Provide specific, actionable feedback for improvement.
        
        Document:
        {content}
        
        Your response must be in this format:
        Score: <score between 0.0 and 1.0>
        Feedback: <detailed feedback>
        """
        
        # If we have memory, check if we've seen similar content before
        memory_context = ""
        if self.memory_id:
            memory_context = f"""
            Before evaluating, review your previous evaluations for similar documents.
            Consider patterns you've seen before and maintain consistency in your feedback style.
            If you notice this document has improved from previous versions, acknowledge that progress.
            """
            task_description = memory_context + task_description
        
        result = self.agent.execute_task(task_description)
        
        # Parse the result string into score and feedback
        lines = result.split("\n")
        score = 0.0
        feedback = ""
        
        for line in lines:
            if line.startswith("Score:"):
                try:
                    score = float(line.replace("Score:", "").strip())
                except ValueError:
                    score = 0.0
            elif line.startswith("Feedback:"):
                feedback = line.replace("Feedback:", "").strip()
            else:
                feedback += line + "\n"
        
        # Store the evaluation in memory if memory is enabled
        if self.memory_id:
            # Create a summary of the content and feedback to store in memory
            content_preview = content[:100] + "..." if len(content) > 100 else content
            memory_entry = f"Document: {content_preview}\nScore: {score}\nFeedback: {feedback[:200]}..."
            self.agent.memory.add(memory_entry)
                
        return score, feedback.strip()

class DocumentImprover:
    """Document improvement agent using CrewAI."""
    
    def __init__(self, api_key: str = None, memory_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Create a memory instance if memory_id is provided
        memory = None
        if memory_id:
            memory = CrewMemory(memory_id=memory_id)
            
        self.agent = Agent(
            role="Documentation Improver",
            goal="Transform documents into clear, comprehensive, and well-structured content",
            backstory="You are a senior technical writer who specializes in improving documentation",
            verbose=True,
            llm_model="gpt-4",
            memory=memory
        )
        self.memory_id = memory_id
        
    def improve(self, content: str, feedback: str) -> str:
        """Improve document based on feedback."""
        task_description = f"""
        Improve the following document based on the provided feedback.
        Make the document more clear, complete, and coherent.
        
        Original Document:
        {content}
        
        Feedback:
        {feedback}
        
        Provide only the improved document as your response, without any additional commentary.
        """
        
        # If we have memory, add context from previous improvements
        if self.memory_id:
            memory_context = f"""
            Before improving this document, review your memory of previous document improvements.
            Consider what techniques worked well in past improvements.
            Maintain a consistent style and terminology across improvements.
            Pay attention to patterns of issues you've addressed before.
            """
            task_description = memory_context + task_description
        
        result = self.agent.execute_task(task_description)
        
        # Store the improvement in memory if memory is enabled
        if self.memory_id:
            # Create a summary of the content and improvements made to store in memory
            content_preview = content[:100] + "..." if len(content) > 100 else content
            improved_preview = result[:100] + "..." if len(result) > 100 else result
            memory_entry = f"Original: {content_preview}\nImproved: {improved_preview}\nBased on feedback: {feedback[:200]}..."
            self.agent.memory.add(memory_entry)
            
        return result.strip()

import os
from typing import Optional, Tuple

from pydantic import BaseModel
from crewai import Agent, Task  # Import Task to wrap task descriptions

try:
    # Best practice: import the memory abstraction from crewai.memory if available.
    from crewai.memory import Memory as CrewMemory
except ImportError:
    CrewMemory = None  # Memory is optional if not available

class AgentResult(BaseModel):
    """Result from agent execution."""
    score: float = 0.0
    content: str = ""
    feedback: str = ""

def create_memory_instance(memory_id: Optional[str]) -> Optional[CrewMemory]:
    """Return a memory instance if a memory_id is provided and CrewMemory is available."""
    if memory_id and CrewMemory:
        return CrewMemory(memory_id=memory_id)
    return None

def parse_agent_response(response: str) -> Tuple[float, str]:
    """
    Parse the agent response expecting the following format:
    
      Score: <score between 0.0 and 1.0>
      Feedback: <detailed feedback>
      
    Returns a tuple with the score and the feedback.
    """
    lines = response.splitlines()
    score = 0.0
    feedback_lines = []
    for line in lines:
        if line.startswith("Score:"):
            try:
                score = float(line[len("Score:"):].strip())
            except ValueError:
                score = 0.0
        elif line.startswith("Feedback:"):
            feedback_lines.append(line[len("Feedback:"):].strip())
        else:
            # Append additional text once feedback has started
            if feedback_lines:
                feedback_lines.append(line.strip())
    feedback = "\n".join(feedback_lines)
    return score, feedback

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
