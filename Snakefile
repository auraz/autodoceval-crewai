"""Snakemake workflow for document evaluation and improvement"""
from pathlib import Path
import json
import uuid
from datetime import datetime
from typing import Any

from evcrew import DocumentCrew

# Utility functions
def read_file(file_path: str) -> str:
    """Read file and return its contents."""
    return Path(file_path).read_text(encoding="utf-8")

def write_file(file_path: str, content: str) -> None:
    """Write content to file, creating directories if needed."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def save_auto_improve_metadata(output_path: str, doc_name: str, history: list[dict], params: Any, status: str) -> None:
    """Save comprehensive metadata for auto-improve runs."""
    metadata = {
        "document": doc_name,
        "timestamp": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
        "status": status,
        "target_score": params.target_score,
        "max_iterations": params.max_iter,
        "improvement_history": history,
        "final_score": history[-1]["score"],
        "total_improvement": history[-1]["score"] - history[0]["score"],
        "iterations_used": len(history) - 1
    }
    metadata_path = Path(output_path).parent / f"{doc_name}_auto_improve_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

DEFAULT_MAX_ITERATIONS = 3  # Auto-improve iteration cap
DEFAULT_TARGET_SCORE = 85  # Desired quality score (0-100 scale)

MAX_ITERATIONS = config.get("max_iterations", DEFAULT_MAX_ITERATIONS)
TARGET_SCORE = config.get("target_score", DEFAULT_TARGET_SCORE)

INPUT_DIR = Path("docs") / "input"
OUTPUT_DIR = Path("docs") / "output"

DOCS = sorted(INPUT_DIR.glob("*.md"))

def stem(path: Path) -> str: return Path(path).stem


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
    run:
        doc_content = Path(input.doc).read_text()
        output_dir = Path(output.score).parent
        
        print(f"📊 Evaluating {wildcards.name}...", end="", flush=True)
        crew = DocumentCrew()
        score, feedback = crew.evaluator.execute(doc_content)
        print(f" Score: {score:.1f}%")
        
        crew.evaluator.save_evaluation(score, feedback, output_dir, wildcards.name, doc_content)

rule auto_improve:
    input:
        doc = lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        final = str(OUTPUT_DIR) + "/{name}/{name}_final.md"
    params:
        max_iter      = MAX_ITERATIONS,
        target_score  = TARGET_SCORE
    run:
        output_dir = Path(output.final).parent
        doc_content = read_file(str(input.doc))
        
        print(f"🔄 Starting auto-improvement for {wildcards.name}...")
        
        crew = DocumentCrew()
        final_doc, history = crew.auto_improve(doc_content, output_dir, wildcards.name, params.max_iter, params.target_score)
        
        # Save final document
        write_file(output.final, final_doc)
        
        # Determine status
        final_score = history[-1]["score"]
        if final_score >= params.target_score:
            status = "target_reached"
            print(f"✅ Target score reached! Final score: {final_score:.1f}%")
        else:
            status = "max_iterations_reached"
            print(f"⚠️  Max iterations reached. Final score: {final_score:.1f}%")
            
        # Save metadata
        save_auto_improve_metadata(output.final, wildcards.name, history, params, status)
