"""Snakemake workflow for document evaluation and improvement"""
from pathlib import Path

from evcrew import DocumentCrew, process_file
from evcrew.utils import read_file

MAX_ITERATIONS = 2  # Auto-improve iteration cap

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
        crew = DocumentCrew()
        content = read_file(input.doc)
        score, feedback = crew.evaluate_one(content)
        print(f"📊 {wildcards.name}: {score:.0f}%")
        crew.evaluator.save(score, feedback, content, Path(output.json).parent, wildcards.name, input.doc)

rule evaluate_and_improve_all:
    input:
        expand(str(OUTPUT_DIR) + "/{name}/{name}_improved.md", name=[stem(p) for p in DOCS])

rule evaluate_and_improve_one:
    input:
        doc=lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        json = str(OUTPUT_DIR) + "/{name}/{name}_improved.json",
        improved = str(OUTPUT_DIR) + "/{name}/{name}_improved.md"
    run:
        print(f"🔄 {wildcards.name}: evaluating and improving...")
        crew = DocumentCrew()
        content = read_file(input.doc)
        improved_content, score, feedback = crew.evaluate_and_improve_one(content, wildcards.name)
        print(f"   → Final: {score:.0f}%")
        crew.improver.save(content, improved_content, score, feedback, Path(output.json).parent, wildcards.name, input.doc)

rule auto_improve_all:
    input:
        doc = lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        final = str(OUTPUT_DIR) + "/{name}/{name}_final.md",
        json = str(OUTPUT_DIR) + "/{name}/{name}_results.json"
    run:
        crew = DocumentCrew()
        content = read_file(input.doc)
        iterator = crew.auto_improve_one(content, Path(output.final).parent, wildcards.name, str(input.doc), MAX_ITERATIONS)

rule auto_improve_one:
    input:
        doc = Path("{doc}")
    output:
        final = str(OUTPUT_DIR) + "/custom/{name}_final.md",
        json = str(OUTPUT_DIR) + "/custom/{name}_results.json"
    run:
        crew = DocumentCrew()
        content = read_file(input.doc)
        iterator = crew.auto_improve_one(content, Path(output.final).parent, wildcards.name, str(input.doc), MAX_ITERATIONS)