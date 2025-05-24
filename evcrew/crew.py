"""Crew-based workflows for document evaluation and improvement."""

from crewai import Crew, Process, Task

from .agents import DocumentEvaluator, DocumentImprover, EvaluationResult, ImprovementResult

__all__ = ["DocumentCrew", "evaluate_document", "improve_document"]


class DocumentCrew:
    """Crew for multi-agent document workflows."""
    
    def __init__(self):
        self.evaluator = DocumentEvaluator()
        self.improver = DocumentImprover()
    
    def evaluate_and_improve(self, content: str) -> tuple[str, float, str]:
        """Evaluate a document and improve it in one workflow.
        
        Returns:
            tuple: (improved_content, score, feedback)
        """
        # Create tasks using agent methods
        eval_task = self.evaluator.create_task(content)
        improve_task = self.improver.create_task(content)  # Feedback will come from context
        
        # Set task dependencies - improver needs evaluator's output
        improve_task.context = [eval_task]
        
        # Create crew with both agents working together
        crew = Crew(
            agents=[self.evaluator.agent, self.improver.agent],
            tasks=[eval_task, improve_task],
            process=Process.sequential,
            memory=True,
            embedder={
                "provider": "openai",
                "config": {"model": "text-embedding-3-small"}
            },
            verbose=False
        )
        
        # Execute workflow
        result = crew.kickoff()
        
        # Extract results
        eval_result = result.tasks_output[0].pydantic
        improve_result = result.tasks_output[1].pydantic
        
        return improve_result.improved_content, eval_result.score, eval_result.feedback


# Single-agent wrapper functions for backward compatibility
def evaluate_document(doc_content: str) -> tuple[float, str]:
    """Evaluate document for clarity and return score with reasoning."""
    evaluator = DocumentEvaluator()
    return evaluator.execute(doc_content)


def improve_document(doc_content: str, feedback: str) -> str:
    """Generate improved document based on evaluation feedback."""
    improver = DocumentImprover()
    return improver.execute(doc_content, feedback)