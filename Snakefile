"""Snakemake workflow that wires the existing high-level helpers in modules.core"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))  # allow “import modules…”

# --- guarantee that our local "modules" package is importable ----------
if 'modules' in sys.modules and not getattr(sys.modules['modules'], '__path__', None):
    # a non-package named "modules" was imported earlier – remove it
    del sys.modules['modules']
# -----------------------------------------------------------------------

configfile: "snakefile-config.yaml"

INPUT_DIR  = Path("docs") / "input"
OUTPUT_DIR = Path("docs") / "output"

MEMORY_ID      = config.get("memory_id")          # may be None
MAX_ITERATIONS = config.get("max_iterations", 3)
TARGET_SCORE   = config.get("target_score", 0.7)

# iterate through all *.md files in docs/input/
DOCS = sorted(INPUT_DIR.glob("*.md"))

# helper to strip extension once
def stem(path): return Path(path).stem


rule all:
    input:
        expand(str(OUTPUT_DIR) + "/{name}/{name}_final.md",
               name=[stem(p) for p in DOCS])

rule evaluate:
    input:
        expand(str(OUTPUT_DIR) + "/{name}/{name}_score.txt",
               name=[stem(p) for p in DOCS]) +
        expand(str(OUTPUT_DIR) + "/{name}/{name}_feedback.txt",
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
        from modules.core import evaluate_document, format_percentage
        txt = Path(input.doc).read_text()
        score, fb = evaluate_document(txt, memory_id=params.memory)
        Path(output.score).write_text(format_percentage(score))
        Path(output.feedback).write_text(fb)

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
