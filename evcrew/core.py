"""Core functionality for document evaluation and improvement using CrewAI agents."""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from .agents import DocumentEvaluator, DocumentImprover
from .file_utils import format_percentage, read_file, write_file

_OUTPUT_BASE_DIR = Path("docs") / "output"

__all__ = [
    "auto_improve_document",
    "evaluate_document",
    "generate_improved_path",
    "improve_document",
]


def _save_run_data(
    run_type: str,
    input_content: str,
    output_content: str,
    meta: dict,
) -> None:
    """Persist input, output and metadata of a single evaluate / improve run."""
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    run_dir = _OUTPUT_BASE_DIR / f"{run_type}_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "input.txt").write_text(input_content, encoding="utf-8")
    (run_dir / "output.txt").write_text(output_content, encoding="utf-8")
    meta |= {"run_type": run_type, "timestamp": timestamp}
    (run_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def evaluate_document(doc_content: str, memory_id: str) -> tuple[float, str]:
    """Evaluate document for clarity and return score with reasoning."""
    evaluator = DocumentEvaluator(memory_id)
    score, reasoning = evaluator.evaluate(doc_content)

    _save_run_data(
        "evaluate",
        doc_content,
        f"Score: {score}\nReasoning: {reasoning}",
        {"score": score, "reasoning": reasoning, "memory_id": memory_id},
    )
    return score, reasoning


def improve_document(
    doc_content: str,
    feedback: str,
    memory_id: str,
    previous_score: float | None = None,
) -> str:
    """Generate improved document based on evaluation feedback."""
    improver = DocumentImprover(memory_id)
    improved_doc = improver.improve(doc_content, feedback)

    _save_run_data(
        "improve",
        doc_content,
        improved_doc,
        {
            "feedback": feedback,
            "memory_id": memory_id,
            "previous_score": previous_score,
        },
    )
    return improved_doc


def generate_improved_path(doc_path: str, iteration: int) -> str:
    """Generate output path for improved document at given iteration."""
    base_name = os.path.basename(doc_path)
    filename, ext = os.path.splitext(base_name) if "." in base_name else (base_name, ".md")

    if "_iter" in filename:  
        filename = filename.split("_iter")[0]

    out_dir = _OUTPUT_BASE_DIR / filename  
    out_dir.mkdir(parents=True, exist_ok=True)

    return str(out_dir / f"{filename}_iter{iteration}{ext}")


def auto_improve_document(
    doc_path: str,
    max_iterations: int = 3,
    target_score: float = 0.7,
    memory_id: Optional[str] = None,
) -> str:
    """Run auto-improvement loop on a document with persistent memory."""
    if not os.path.exists(doc_path):
        raise FileNotFoundError(f"File not found: {doc_path}")

    final_path: str = doc_path  

    print(f"🔄 Starting auto-improvement loop for {doc_path}")
    print(f"Target score: {format_percentage(target_score)}")
    print(f"Maximum iterations: {max_iterations}")

    base_memory_id = memory_id or f"autodoceval_{Path(doc_path).stem}_{uuid.uuid4().hex[:8]}"
    evaluator_memory_id = f"{base_memory_id}_evaluator"
    improver_memory_id = f"{base_memory_id}_improver"
    print(f"🧠 Using memory IDs: {evaluator_memory_id}, {improver_memory_id}")

    original_doc = read_file(doc_path)
    original_score, original_feedback = evaluate_document(original_doc, memory_id=evaluator_memory_id)
    print(f"Original document score: {format_percentage(original_score)}")

    current_doc = original_doc
    current_feedback = original_feedback
    last_score = original_score
    iteration = 0

    # Skip improvement if already at target
    if original_score >= target_score:
        print(f"✅ Original document already meets target score of {format_percentage(target_score)}!")
        return final_path

    while iteration < max_iterations:
        iteration += 1
        print(f"\n📝 Iteration {iteration}/{max_iterations}")

        # Improve document based on feedback
        improved_doc = improve_document(
            current_doc,
            current_feedback,
            memory_id=improver_memory_id,
            previous_score=last_score,
        )

        # Save improved document
        improved_path = generate_improved_path(doc_path, iteration)
        write_file(improved_path, improved_doc)
        final_path = improved_path

        # Evaluate improved document
        score, feedback = evaluate_document(improved_doc, memory_id=evaluator_memory_id)

        # Print current score
        print(f"Score after iteration {iteration}: {format_percentage(score)}")
        improvement = score - last_score
        print(f"Improvement: {format_percentage(improvement)} from previous version")

        # Check if we've reached the target score
        if score >= target_score:
            print(f"✅ Target score of {format_percentage(target_score)} reached!")
            break

        # Use the improved document for the next iteration
        current_doc = improved_doc
        current_feedback = feedback
        last_score = score

    # Print final results
    print(f"\n📈 Total improvement: {format_percentage(score - original_score)}")

    if iteration >= max_iterations and score < target_score:
        print(f"⚠️ Maximum iterations ({max_iterations}) reached without achieving target score")

    print("\n✅ Auto-improvement process completed!")
    return final_path
