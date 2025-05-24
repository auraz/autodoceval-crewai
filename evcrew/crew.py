"""Crew-based workflows for document evaluation and improvement."""

from pathlib import Path
from typing import Optional

from crewai import Crew, Process

from .agents import DocumentEvaluator, DocumentImprover
from .process import DocumentIterator
from .tracking import IterationTracker
from .utils import read_file, write_file

__all__ = ["DocumentCrew"]


class DocumentCrew:
    """Crew for multi-agent document workflows."""

    def __init__(self):
        self.evaluator = DocumentEvaluator()
        self.improver = DocumentImprover()
        self.crew = self._create_crew()

    def _create_crew(self) -> Crew:
        """Create the crew instance with both agents."""
        return Crew(
            agents=[self.evaluator.agent, self.improver.agent],
            tasks=[],  # Tasks will be set before kickoff
            process=Process.sequential,
            memory=True,
            embedder={"provider": "openai", "config": {"model": "text-embedding-3-small"}},
            verbose=False,
        )

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
    ) -> tuple[str, IterationTracker, str]:
        """Auto-improve document until target score or max iterations reached, returns (final_doc, tracker, status)."""
        tracker = IterationTracker(doc_name, input_path or "unknown")
        iterator = DocumentIterator(self.evaluator, self.improver, content, max_iterations, target_score)
        
        status = "unknown"
        try:
            for iteration_num, doc_content, score, feedback in iterator:
                if iteration_num == 0:
                    print("  📊 Initial evaluation...", end="", flush=True)
                    print(f" Score: {score:.1f}%")
                    tracker.add_iteration(0, score, feedback, input_path, doc_content)
                else:
                    print(f"  📝 Iteration {iteration_num}/{max_iterations}...", end="", flush=True)
                    tracker.add_iteration(iteration_num, score, feedback, None, doc_content)
                    improvement = tracker.iterations[-1].improvement_delta or 0
                    print(f" Score: {score:.1f}% ({improvement:+.1f}%)")
                    
        except StopIteration as e:
            reason = str(e)
            if "Target score met on initial evaluation" in reason:
                status = "target_met_original"
                print(f"✅ Target score already met! Score: {iterator.get_final_score():.1f}%")
            elif "Target score reached" in reason:
                status = "target_reached"
                print(f"✅ Target score reached! Final score: {iterator.get_final_score():.1f}%")
            elif "Max iterations reached" in reason:
                status = "max_iterations_reached"
                print(f"⚠️  Max iterations reached. Final score: {iterator.get_final_score():.1f}%")

        tracker.save_complete_results(output_dir, status, target_score, max_iterations)
        return iterator.get_final_content(), tracker, status

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
    ) -> tuple[IterationTracker, str]:
        """Auto-improve a document from file, returns (tracker, status)."""
        content = read_file(input_path)
        output_dir = Path(output_dir)

        final_doc, tracker, status = self.auto_improve(content, output_dir, doc_name, max_iterations, target_score, str(input_path))

        # Save final document
        write_file(output_dir / f"{doc_name}_final.md", final_doc)

        return tracker, status
