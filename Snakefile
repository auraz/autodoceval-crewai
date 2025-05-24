"""Snakemake workflow for document evaluation and improvement"""
from pathlib import Path
import json
import uuid
from datetime import datetime

from evcrew.agents import DocumentEvaluator, DocumentImprover

# Utility functions
def read_file(file_path: str) -> str:
    """Read file and return its contents."""
    return Path(file_path).read_text(encoding="utf-8")

def write_file(file_path: str, content: str) -> None:
    """Write content to file, creating directories if needed."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def save_auto_improve_metadata(output_path: str, doc_name: str, history: list, params, status: str) -> None:
    """Save comprehensive metadata for auto-improve runs."""
    metadata = {
        "document": doc_name,
        "timestamp": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
        "status": status,
        "target_score": params.target_score,
        "max_iterations": params.max_iter,
        "memory_id": params.memory,
        "improvement_history": history,
        "final_score": history[-1]["score"],
        "total_improvement": history[-1]["score"] - history[0]["score"],
        "iterations_used": len(history) - 1
    }
    metadata_path = Path(output_path).parent / f"{doc_name}_auto_improve_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

# Default configuration values
DEFAULT_MEMORY_ID = "api_docs_memory"  # Set to None to generate unique IDs
DEFAULT_MAX_ITERATIONS = 3             # Auto-improve iteration cap
DEFAULT_TARGET_SCORE = 85              # Desired quality score (0-100 scale)

# Get configuration from command line or use defaults
MEMORY_ID = config.get("memory_id", DEFAULT_MEMORY_ID)
MAX_ITERATIONS = config.get("max_iterations", DEFAULT_MAX_ITERATIONS)
TARGET_SCORE = config.get("target_score", DEFAULT_TARGET_SCORE)

INPUT_DIR = Path("docs") / "input"
OUTPUT_DIR = Path("docs") / "output"

# iterate through all *.md files in docs/input/
DOCS = sorted(INPUT_DIR.glob("*.md"))

def stem(path): return Path(path).stem  # helper to strip extension once


rule all:
    input:
        expand(str(OUTPUT_DIR) + "/{name}/{name}_final.md",
               name=[stem(p) for p in DOCS])

rule evaluate_doc:
    input:
        doc=lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        score    = str(OUTPUT_DIR) + "/{name}/{name}_score.txt",
        feedback = str(OUTPUT_DIR) + "/{name}/{name}_feedback.txt"
    params:
        memory  = MEMORY_ID
    run:
        Path(output.score).parent.mkdir(parents=True, exist_ok=True)

        # Read document
        doc_content = Path(input.doc).read_text()

        # Create evaluator and evaluate
        print(f"📊 Evaluating {wildcards.name}...", end="", flush=True)
        memory_id = params.memory or f"eval_{wildcards.name}_{uuid.uuid4().hex[:8]}"
        evaluator = DocumentEvaluator(memory_id)
        score, feedback = evaluator.execute(doc_content)
        print(f" Score: {score:.1f}%")

        # Save run data
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        run_dir = OUTPUT_DIR / f"evaluate_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)

        (run_dir / "input.txt").write_text(doc_content, encoding="utf-8")
        (run_dir / "output.txt").write_text(f"Score: {score}\nFeedback: {feedback}", encoding="utf-8")
        meta = {"run_type": "evaluate", "timestamp": timestamp, "score": score, "feedback": feedback, "memory_id": memory_id}
        (run_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        # Write outputs
        Path(output.score).write_text(f"{score:.1f}%")
        Path(output.feedback).write_text(feedback)
        
        # Save metadata in the same directory as outputs
        metadata = {
            "document": wildcards.name,
            "timestamp": timestamp,
            "score": score,
            "feedback": feedback,
            "memory_id": memory_id,
            "input_file": str(input.doc)
        }
        metadata_path = Path(output.score).parent / f"{wildcards.name}_metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

rule auto_improve:
    input:
        doc = lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        final = str(OUTPUT_DIR) + "/{name}/{name}_final.md"
    params:
        memory        = MEMORY_ID,
        max_iter      = MAX_ITERATIONS,
        target_score  = TARGET_SCORE
    run:
        Path(output.final).parent.mkdir(parents=True, exist_ok=True)
        doc_path = str(input.doc)

        print(f"🔄 Starting auto-improvement for {wildcards.name}...")

        # Setup memory IDs
        base_memory_id = params.memory or f"autodoceval_{wildcards.name}_{uuid.uuid4().hex[:8]}"
        evaluator_memory_id = f"{base_memory_id}_evaluator"
        improver_memory_id = f"{base_memory_id}_improver"
        # Memory IDs: evaluator_memory_id, improver_memory_id

        # Create agents
        evaluator = DocumentEvaluator(evaluator_memory_id)
        improver = DocumentImprover(improver_memory_id)

        # Read and evaluate original document
        print(f"  📊 Initial evaluation...", end="", flush=True)
        original_doc = read_file(doc_path)
        original_score, original_feedback = evaluator.execute(original_doc)
        print(f" Score: {original_score:.1f}%")
        # Track improvement history
        improvement_history = [{
            "iteration": 0,
            "score": original_score,
            "feedback": original_feedback,
            "file": doc_path
        }]

        current_doc = original_doc
        current_feedback = original_feedback
        last_score = original_score
        iteration = 0
        final_path = doc_path

        # Skip improvement if already at target
        if original_score >= params.target_score:
            write_file(output.final, original_doc)
            # Save metadata
            save_auto_improve_metadata(output.final, wildcards.name, improvement_history, params, "target_met_original")
            return

        while iteration < params.max_iter:
            iteration += 1
            print(f"  📝 Iteration {iteration}/{params.max_iter}...", end="", flush=True)

            # Improve document
            improved_doc = improver.execute(current_doc, current_feedback)

            # Save improved document
            improved_path = OUTPUT_DIR / wildcards.name / f"{wildcards.name}_iter{iteration}.md"
            write_file(str(improved_path), improved_doc)
            final_path = str(improved_path)

            # Evaluate improved document
            score, feedback = evaluator.execute(improved_doc)

            improvement = score - last_score
            
            # Add to history
            improvement_history.append({
                "iteration": iteration,
                "score": score,
                "feedback": feedback,
                "improvement": improvement,
                "file": str(improved_path)
            })
            
            print(f" Score: {score:.1f}% ({improvement:+.1f}%)")

            if score >= params.target_score:
                break

            current_doc = improved_doc
            current_feedback = feedback
            last_score = score

        # Determine completion status
        if score >= params.target_score:
            status = "target_reached"
            print(f"✅ Target score reached! Final score: {score:.1f}%")
        else:
            status = "max_iterations_reached"
            print(f"⚠️  Max iterations reached. Final score: {score:.1f}%")

        # Copy final result
        from shutil import copyfile
        copyfile(final_path, output.final)
        
        # Save comprehensive metadata
        save_auto_improve_metadata(output.final, wildcards.name, improvement_history, params, status)
