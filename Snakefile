"""
Snakemake workflow that wires the existing high-level helpers in
modules.core (evaluate_document, improve_document, auto_improve_document).

The workflow assumes:
  • every Markdown document you want to process lives under docs/
  • results are written under output/  (same dir the library already uses)
  • optional settings live in a small config.yaml (memory id, target score,
    max iterations, etc.)


"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))  # allow “import modules…”


configfile: "snakefile-config.yaml"

MEMORY_ID      = config.get("memory_id")          # may be None
MAX_ITERATIONS = config.get("max_iterations", 3)
TARGET_SCORE   = config.get("target_score", 0.7)
DOCS           = [Path(p) for p in config["documents"]]

# helper to strip extension once
def stem(path): return Path(path).stem


rule all:
    input:
        expand("output/{name}/{name}_final.md", name=[stem(p) for p in DOCS])

rule evaluate:
    input:
        doc=lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        score   = "output/{name}/{name}_score.txt",
        feedback= "output/{name}/{name}_feedback.txt"
    params:
        memory  = MEMORY_ID
    run:
        from modules.core import evaluate_document, format_percentage
        txt = Path(input.doc).read_text()
        score, fb = evaluate_document(txt, memory_id=params.memory)
        Path(output.score).write_text(format_percentage(score))
        Path(output.feedback).write_text(fb)

rule auto_improve:
    input:
        doc = lambda wc: next(p for p in DOCS if stem(p) == wc.name)
    output:
        final = "output/{name}/{name}_final.md"
    params:
        memory        = MEMORY_ID,
        max_iter      = MAX_ITERATIONS,
        target_score  = TARGET_SCORE
    run:
        from modules.core import auto_improve_document
        final_path = auto_improve_document(
            doc_path     = input.doc,
            max_iterations = params.max_iter,
            target_score   = params.target_score,
            memory_id      = params.memory,
            persist_memory = bool(params.memory),
        )
        # auto_improve_document already writes the file; just
        # symlink/copy so Snakemake has its expected output
        from shutil import copyfile
        copyfile(final_path, output.final)
