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
        # Create evaluation task
        eval_task = Task(
            description=f"""Evaluate the following document for clarity and quality:

{content}

Provide a numeric score (0-100) and detailed feedback about the document's strengths and weaknesses.""",
            expected_output="Document evaluation with score and feedback",
            agent=self.evaluator.agent,
            output_pydantic=EvaluationResult
        )
        
        # Create improvement task that uses evaluation context
        improve_task = Task(
            description=f"""Based on the evaluation feedback from the previous task, improve the following document:

{content}

Use the score and feedback from the evaluation to guide your improvements.""",
            expected_output="Improved version of the document",
            agent=self.improver.agent,
            output_pydantic=ImprovementResult,
            context=[eval_task]  # This makes eval results available to improve task
        )
        
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