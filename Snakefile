"""Snakemake workflow for document evaluation and improvement"""
from pathlib import Path

from evcrew import DocumentCrew

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

rule evaluate_all:
    input:
        expand(str(OUTPUT_DIR) + "/{name}/{name}_score.txt",
               name=[stem(p) for p in DOCS])

rule evaluate_one:
    input:
        doc=lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        score    = str(OUTPUT_DIR) + "/{name}/{name}_score.txt",
        feedback = str(OUTPUT_DIR) + "/{name}/{name}_feedback.txt"
    run:
        print(f"📊 Evaluating {wildcards.name}...")
        crew = DocumentCrew()
        crew.evaluate_file(input.doc, Path(output.score).parent, wildcards.name)

rule evaluate_and_improve:
    input:
        doc=lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        score    = str(OUTPUT_DIR) + "/{name}/{name}_improved_score.txt",
        feedback = str(OUTPUT_DIR) + "/{name}/{name}_improved_feedback.txt",
        improved = str(OUTPUT_DIR) + "/{name}/{name}_improved.md"
    run:
        print(f"🔄 Evaluating and improving {wildcards.name}...")
        crew = DocumentCrew()
        crew.evaluate_and_improve_file(input.doc, Path(output.score).parent, wildcards.name)

rule auto_improve:
    input:
        doc = lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        final = str(OUTPUT_DIR) + "/{name}/{name}_final.md"
    params:
        max_iter      = MAX_ITERATIONS,
        target_score  = TARGET_SCORE
    run:
        print(f"🔄 Starting auto-improvement for {wildcards.name}...")
        crew = DocumentCrew()
        crew.auto_improve_file(input.doc, Path(output.final).parent, wildcards.name, params.max_iter, params.target_score)
