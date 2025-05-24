"""Snakemake workflow for document evaluation and improvement"""
from pathlib import Path

from evcrew import DocumentCrew

MAX_ITERATIONS = 2  # Auto-improve iteration cap
TARGET_SCORE = 85  # Desired quality score (0-100 scale)

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
        expand(str(OUTPUT_DIR) + "/{name}/{name}_evaluation.json", name=[stem(p) for p in DOCS])

rule evaluate_one:
    input:
        doc=lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        json = str(OUTPUT_DIR) + "/{name}/{name}_evaluation.json"
    run:
        print(f"📊 Evaluating {wildcards.name}...")
        crew = DocumentCrew()
        crew.evaluate_file(input.doc, Path(output.json).parent, wildcards.name)

rule evaluate_and_improve:
    input:
        doc=lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        json = str(OUTPUT_DIR) + "/{name}/{name}_improved.json",
        improved = str(OUTPUT_DIR) + "/{name}/{name}_improved.md"
    run:
        print(f"🔄 Evaluating and improving {wildcards.name}...")
        crew = DocumentCrew()
        crew.evaluate_and_improve_file(input.doc, Path(output.json).parent, wildcards.name)

rule auto_improve:
    input:
        doc = lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        final = str(OUTPUT_DIR) + "/{name}/{name}_final.md",
        json = str(OUTPUT_DIR) + "/{name}/{name}_results.json"
    run:
        print(f"🔄 Starting auto-improvement for {wildcards.name}...")
        crew = DocumentCrew()
        crew.auto_improve_file(input.doc, Path(output.final).parent, wildcards.name, MAX_ITERATIONS, TARGET_SCORE)
