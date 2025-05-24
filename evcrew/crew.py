"""Crew-based workflows for document evaluation and improvement."""

from pathlib import Path
from typing import Optional

from crewai import Crew, Process

from .agents import DocumentEvaluator, DocumentImprover
from .process import DocumentIterator
from .utils import read_file, write_file

__all__ = ["DocumentCrew"]


class DocumentCrew:
    """Crew for multi-agent document workflows."""

    def __init__(self):
        self.evaluator = DocumentEvaluator()
        self.improver = DocumentImprover()
        self.crew = Crew(
            agents=[self.evaluator.agent, self.improver.agent],
            tasks=[],  # Tasks will be set before kickoff
            process=Process.sequential,
            memory=True,
            embedder={"provider": "openai", "config": {"model": "text-embedding-3-small"}},
            verbose=False,
        )

    def evaluate_one(self, content: str) -> tuple[float, str]:
        """Evaluate a single document and return (score, feedback)."""
        return self.evaluator.execute(content)
    
    def improve_one(self, content: str, feedback: str) -> str:
        """Improve a single document based on feedback and return improved content."""
        return self.improver.execute(content, feedback)

    def evaluate_and_improve(self, content: str, doc_name: str = "document") -> tuple[str, float, str]:
        """Evaluate a document and improve it in one workflow returning (improved_content, score, feedback)."""
        eval_task = self.evaluator.create_task(content, doc_name=doc_name)
        improve_task = self.improver.create_task(content, doc_name=doc_name)  # Feedback will come from context
        improve_task.context = [eval_task]
        
        # Update crew with new tasks
        self.crew.tasks = [eval_task, improve_task]
        
        result = self.crew.kickoff()
        eval_result = result.tasks_output[0].pydantic
        improve_result = result.tasks_output[1].pydantic

        return improve_result.improved_content, eval_result.score, eval_result.feedback

    def auto_improve(
        self, content: str, output_dir: Path, doc_name: str, max_iterations: int = 2, target_score: float = 85, input_path: Optional[str] = None
    ) -> tuple[str, DocumentIterator, str]:
        """Auto-improve document until target score or max iterations reached, returns (final_doc, iterator, status)."""
        iterator = DocumentIterator(
            self.evaluator, self.improver, doc_name, input_path or "unknown", 
            content, max_iterations, target_score
        )
        
        status = "unknown"
        try:
            for iter_data in iterator:
                if iter_data.iteration == 0:
                    print("  📊 Initial evaluation...", end="", flush=True)
                    print(f" Score: {iter_data.score:.1f}%")
                else:
                    print(f"  📝 Iteration {iter_data.iteration}/{max_iterations}...", end="", flush=True)
                    print(f" Score: {iter_data.score:.1f}% ({iter_data.improvement_delta:+.1f}%)")
                    
        except StopIteration as e:
            status = str(e)
            if status == "target_met_original":
                print(f"✅ Target score already met! Score: {iterator.final_score:.1f}%")
            elif status == "target_reached":
                print(f"✅ Target score reached! Final score: {iterator.final_score:.1f}%")
            elif status == "max_iterations_reached":
                print(f"⚠️  Max iterations reached. Final score: {iterator.final_score:.1f}%")

        iterator.save_results(output_dir, status)
        return iterator.final_content, iterator, status

    def evaluate_file(self, input_path: str | Path, output_dir: str | Path, doc_name: str) -> None:
        """Evaluate a document from file and save results."""
        content = read_file(input_path)
        
        print("  📊 Evaluating...", end="", flush=True)
        score, feedback = self.evaluator.execute(content)
        print(f" Score: {score:.1f}%")

        # Let evaluator handle saving
        self.evaluator.save(score, feedback, content, output_dir, doc_name, input_path)

    def evaluate_and_improve_file(self, input_path: str | Path, output_dir: str | Path, doc_name: str) -> None:
        """Evaluate and improve a document from file, saving all outputs."""
        content = read_file(input_path)

        improved_content, score, feedback = self.evaluate_and_improve(content, doc_name)
        print(f"   Final score: {score:.1f}%")

        # Let improver handle saving
        self.improver.save(content, improved_content, score, feedback, output_dir, doc_name, input_path)

    def auto_improve_file(
        self, input_path: str | Path, output_dir: str | Path, doc_name: str, max_iterations: int = 2, target_score: float = 85
    ) -> tuple[DocumentIterator, str]:
        """Auto-improve a document from file, returns (iterator, status)."""
        content = read_file(input_path)
        output_dir = Path(output_dir)

        final_doc, iterator, status = self.auto_improve(content, output_dir, doc_name, max_iterations, target_score, str(input_path))

        # Save final document
        write_file(output_dir / f"{doc_name}_final.md", final_doc)

        return iterator, status
