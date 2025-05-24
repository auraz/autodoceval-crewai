"""Document improvement iteration tracking system."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


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


class IterationTracker:
    """Track document improvement iterations with metadata."""

    def __init__(self, doc_name: str, doc_path: str):
        self.launch_id = f"doc-improve-{doc_name}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        self.doc_info = DocumentInfo(doc_id=doc_name, path=doc_path)
        self.iterations: list[IterationResult] = []
        self.start_time = datetime.utcnow()

    def add_iteration(self, iteration: int, score: float, feedback: str, improved_path: Optional[str] = None) -> None:
        """Add iteration result to tracking."""
        metrics = QualityMetrics(score=score, feedback=feedback)
        improvement_delta = None

        if self.iterations and iteration > 0:
            improvement_delta = score - self.iterations[-1].metrics.score

        result = IterationResult(iteration=iteration, metrics=metrics, improved_path=improved_path, improvement_delta=improvement_delta)
        self.iterations.append(result)

    def get_summary(self) -> dict[str, Any]:
        """Get tracking summary."""
        if not self.iterations:
            return {}

        initial = self.iterations[0]
        final = self.iterations[-1]

        return {
            "launch_id": self.launch_id,
            "document": self.doc_info.doc_id,
            "path": self.doc_info.path,
            "iterations_count": len(self.iterations) - 1,  # Exclude initial evaluation
            "initial_score": initial.metrics.score,
            "final_score": final.metrics.score,
            "total_improvement": final.metrics.score - initial.metrics.score,
            "duration_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "iterations": [{"number": r.iteration, "score": r.metrics.score, "improvement": r.improvement_delta, "path": r.improved_path} for r in self.iterations],
        }

    def save_to_file(self, output_dir: Path) -> None:
        """Save tracking data to JSON file."""
        summary = self.get_summary()
        output_path = output_dir / f"{self.doc_info.doc_id}_tracking.json"
        output_path.write_text(json.dumps(summary, indent=2))
