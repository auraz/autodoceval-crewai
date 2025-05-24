"""Crew-based workflows for document evaluation and improvement."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from box import Box
from crewai import Crew, Process

from .agents import DocumentEvaluator, DocumentImprover
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

        print("  📊 Initial evaluation...", end="", flush=True)
        score, feedback = self.evaluator.execute(content)
        print(f" Score: {score:.1f}%")

        tracker.add_iteration(0, score, feedback, input_path)
        self.evaluator.save_results(score, feedback, output_dir, f"{doc_name}_initial", content)

        if score >= target_score:
            print(f"✅ Target score already met! Score: {score:.1f}%")
            tracker.save_to_file(output_dir)
            return content, tracker, "target_met_original"

        current_doc = content
        current_feedback = feedback

        for iteration in range(1, max_iterations + 1):
            print(f"  📝 Iteration {iteration}/{max_iterations}...", end="", flush=True)
            improved_doc = self.improver.execute(current_doc, current_feedback)
            iter_path = output_dir / f"{doc_name}_iter{iteration}.md"
            self.improver.save_results(improved_doc, iter_path)
            score, feedback = self.evaluator.execute(improved_doc)

            tracker.add_iteration(iteration, score, feedback, str(iter_path))
            improvement = tracker.iterations[-1].improvement_delta or 0

            print(f" Score: {score:.1f}% ({improvement:+.1f}%)")

            if score >= target_score:
                break

            current_doc = improved_doc
            current_feedback = feedback

        final_score = tracker.iterations[-1].metrics.score
        if final_score >= target_score:
            status = "target_reached"
            print(f"✅ Target score reached! Final score: {final_score:.1f}%")
        else:
            status = "max_iterations_reached"
            print(f"⚠️  Max iterations reached. Final score: {final_score:.1f}%")

        tracker.save_to_file(output_dir)
        return current_doc, tracker, status

    def evaluate_file(self, input_path: str | Path, output_dir: str | Path, doc_name: str) -> None:
        """Evaluate a document from file and save results."""
        content = read_file(input_path)
        output_dir = Path(output_dir)

        print("  📊 Evaluating...", end="", flush=True)
        score, feedback = self.evaluator.execute(content)
        print(f" Score: {score:.1f}%")

        self.evaluator.save_results(score, feedback, output_dir, doc_name, content)

    def evaluate_and_improve_file(self, input_path: str | Path, output_dir: str | Path, doc_name: str) -> None:
        """Evaluate and improve a document from file, saving all outputs."""
        content = read_file(input_path)
        output_dir = Path(output_dir)

        improved_content, score, feedback = self.evaluate_and_improve(content, doc_name)
        print(f"   Final score: {score:.1f}%")

        # Save outputs
        write_file(output_dir / f"{doc_name}_improved_score.txt", f"{score:.1f}%")
        write_file(output_dir / f"{doc_name}_improved_feedback.txt", feedback)
        write_file(output_dir / f"{doc_name}_improved.md", improved_content)

        # Save metadata
        metadata = Box(
            {
                "document": doc_name,
                "timestamp": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
                "score": score,
                "feedback": feedback,
                "input_file": str(input_path),
                "method": "evaluate_and_improve",
            }
        )
        write_file(output_dir / f"{doc_name}_improved_metadata.json", json.dumps(metadata.to_dict(), indent=2))

    def auto_improve_file(
        self, input_path: str | Path, output_dir: str | Path, doc_name: str, max_iterations: int = 2, target_score: float = 85
    ) -> tuple[IterationTracker, str]:
        """Auto-improve a document from file, returns (tracker, status)."""
        content = read_file(input_path)
        output_dir = Path(output_dir)

        final_doc, tracker, status = self.auto_improve(content, output_dir, doc_name, max_iterations, target_score, str(input_path))

        # Save final document
        write_file(output_dir / f"{doc_name}_final.md", final_doc)

        # Save metadata
        tracker.save_metadata(output_dir, status, target_score, max_iterations)

        return tracker, status
