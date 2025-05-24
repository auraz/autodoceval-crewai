"""Document improvement iteration tracking system."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from box import Box


@dataclass
class DocumentInfo:
    """Information about the document being improved."""

    doc_id: str
    path: str
    word_count: int = 0
    last_modified: Optional[str] = None


@dataclass
class IterationInfo:
    """Information about the current iteration."""

    number: int
    parent_launch_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))


@dataclass
class QualityMetrics:
    """Quality metrics for before/after comparison."""

    score: float
    feedback: str
    word_count: int = 0


@dataclass
class IterationResult:
    """Result of a single improvement iteration."""

    iteration: int
    metrics: QualityMetrics
    improved_path: Optional[str] = None
    improvement_delta: Optional[float] = None
    content: Optional[str] = None  # Store the actual content


class IterationTracker:
    """Track document improvement iterations with metadata."""

    def __init__(self, doc_name: str, doc_path: str):
        self.launch_id = f"doc-improve-{doc_name}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        self.doc_info = DocumentInfo(doc_id=doc_name, path=doc_path)
        self.iterations: list[IterationResult] = []
        self.start_time = datetime.utcnow()

    def add_iteration(self, iteration: int, score: float, feedback: str, improved_path: Optional[str] = None, content: Optional[str] = None) -> None:
        """Add iteration result to tracking."""
        metrics = QualityMetrics(score=score, feedback=feedback, word_count=len(content.split()) if content else 0)
        improvement_delta = None

        if self.iterations and iteration > 0:
            improvement_delta = score - self.iterations[-1].metrics.score

        result = IterationResult(iteration=iteration, metrics=metrics, improved_path=improved_path, improvement_delta=improvement_delta, content=content)
        self.iterations.append(result)

    def get_summary(self) -> Box:
        """Get tracking summary as a Box object."""
        if not self.iterations:
            return Box({})

        initial = self.iterations[0]
        final = self.iterations[-1]

        return Box(
            {
                "launch_id": self.launch_id,
                "document": self.doc_info.doc_id,
                "path": self.doc_info.path,
                "iterations_count": len(self.iterations) - 1,  # Exclude initial evaluation
                "initial_score": initial.metrics.score,
                "final_score": final.metrics.score,
                "total_improvement": final.metrics.score - initial.metrics.score,
                "duration_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "iterations": [
                    Box({"number": r.iteration, "score": r.metrics.score, "improvement": r.improvement_delta, "path": r.improved_path}) for r in self.iterations
                ],
            }
        )

    def save_to_file(self, output_dir: Path) -> None:
        """Save tracking data to JSON file."""
        summary = self.get_summary()
        output_path = output_dir / f"{self.doc_info.doc_id}_tracking.json"
        output_path.write_text(json.dumps(summary.to_dict(), indent=2))

    def save_metadata(self, output_dir: Path, status: str, target_score: float, max_iterations: int) -> None:
        """Save comprehensive metadata including status and parameters."""
        summary = self.get_summary()
        summary.status = status
        summary.target_score = target_score
        summary.max_iterations = max_iterations

        output_path = output_dir / f"{self.doc_info.doc_id}_auto_improve_metadata.json"
        output_path.write_text(json.dumps(summary.to_dict(), indent=2))

    def save_complete_results(self, output_dir: Path, status: str, target_score: float, max_iterations: int) -> None:
        """Save all results including content in a single comprehensive JSON file."""
        data = Box({
            "launch_id": self.launch_id,
            "document": self.doc_info.doc_id,
            "input_path": self.doc_info.path,
            "timestamp": self.start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "duration_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "status": status,
            "parameters": {"target_score": target_score, "max_iterations": max_iterations},
            "summary": {
                "iterations_completed": len(self.iterations) - 1,  # Exclude initial
                "initial_score": self.iterations[0].metrics.score if self.iterations else 0,
                "final_score": self.iterations[-1].metrics.score if self.iterations else 0,
                "total_improvement": (self.iterations[-1].metrics.score - self.iterations[0].metrics.score) if len(self.iterations) > 1 else 0,
            },
            "iterations": []
        })
        
        # Add all iteration data including content
        for result in self.iterations:
            iter_data = {
                "iteration": result.iteration,
                "type": "initial_evaluation" if result.iteration == 0 else f"improvement_{result.iteration}",
                "score": result.metrics.score,
                "feedback": result.metrics.feedback,
                "word_count": result.metrics.word_count,
                "improvement_delta": result.improvement_delta,
                "content": result.content
            }
            data.iterations.append(iter_data)
        
        # Save comprehensive results
        output_path = output_dir / f"{self.doc_info.doc_id}_results.json"
        output_path.write_text(json.dumps(data.to_dict(), indent=2))
