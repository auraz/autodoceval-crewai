"""Crew-based workflows for document evaluation and improvement."""

from crewai import Crew, Process

from .agents import DocumentEvaluator, DocumentImprover

__all__ = ["DocumentCrew"]


class DocumentCrew:
    """Crew for multi-agent document workflows."""

    def __init__(self):
        self.evaluator = DocumentEvaluator()
        self.improver = DocumentImprover()

    def evaluate_and_improve(self, content: str) -> tuple[str, float, str]:
        """Evaluate a document and improve it in one workflow returning (improved_content, score, feedback)."""
        eval_task = self.evaluator.create_task(content)
        improve_task = self.improver.create_task(content)  # Feedback will come from context
        improve_task.context = [eval_task]
        crew = Crew(
            agents=[self.evaluator.agent, self.improver.agent],
            tasks=[eval_task, improve_task],
            process=Process.sequential,
            memory=True,
            embedder={"provider": "openai", "config": {"model": "text-embedding-3-small"}},
            verbose=False,
        )
        result = crew.kickoff()
        eval_result = result.tasks_output[0].pydantic
        improve_result = result.tasks_output[1].pydantic

        return improve_result.improved_content, eval_result.score, eval_result.feedback
