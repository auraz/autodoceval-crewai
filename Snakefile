"""Snakemake workflow for document evaluation and improvement"""
from pathlib import Path
import json
import uuid
from datetime import datetime
from typing import Any

from box import Box

from evcrew import DocumentCrew, IterationTracker

# Utility functions
def read_file(file_path: str) -> str:
    """Read file and return its contents."""
    return Path(file_path).read_text(encoding="utf-8")

def write_file(file_path: str, content: str) -> None:
    """Write content to file, creating directories if needed."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def save_auto_improve_metadata(output_path: str, tracker: IterationTracker, params: Any, status: str) -> None:
    """Save comprehensive metadata for auto-improve runs."""
    summary = tracker.get_summary()
    summary.status = status
    summary.target_score = params.target_score
    summary.max_iterations = params.max_iter
    
    metadata_path = Path(output_path).parent / f"{tracker.doc_info.doc_id}_auto_improve_metadata.json"
    metadata_path.write_text(json.dumps(summary.to_dict(), indent=2), encoding="utf-8")

DEFAULT_MAX_ITERATIONS = 2  # Auto-improve iteration cap
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

rule evaluate:
    input:
        expand(str(OUTPUT_DIR) + "/{name}/{name}_score.txt",
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
        
        crew.evaluator.save_results(score, feedback, output_dir, wildcards.name, doc_content)

rule evaluate_and_improve:
    input:
        doc=lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        score    = str(OUTPUT_DIR) + "/{name}/{name}_improved_score.txt",
        feedback = str(OUTPUT_DIR) + "/{name}/{name}_improved_feedback.txt",
        improved = str(OUTPUT_DIR) + "/{name}/{name}_improved.md"
    run:
        doc_content = Path(input.doc).read_text()
        output_dir = Path(output.score).parent
        
        print(f"🔄 Evaluating and improving {wildcards.name}...")
        crew = DocumentCrew()
        improved_content, score, feedback = crew.evaluate_and_improve(doc_content, wildcards.name)
        
        print(f"   Final score: {score:.1f}%")
        
        # Save all outputs
        Path(output.score).write_text(f"{score:.1f}%")
        Path(output.feedback).write_text(feedback)
        Path(output.improved).write_text(improved_content)
        
        # Save metadata using Box
        metadata = Box({
            "document": wildcards.name,
            "timestamp": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "score": score,
            "feedback": feedback,
            "input_file": str(input.doc),
            "method": "evaluate_and_improve"
        })
        metadata_path = output_dir / f"{wildcards.name}_improved_metadata.json"
        metadata_path.write_text(json.dumps(metadata.to_dict(), indent=2))

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
        final_doc, tracker, status = crew.auto_improve(doc_content, output_dir, wildcards.name, params.max_iter, params.target_score, str(input.doc))
        
        write_file(output.final, final_doc)
        save_auto_improve_metadata(output.final, tracker, params, status)
