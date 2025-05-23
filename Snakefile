"""Snakemake workflow for document evaluation and improvement"""
from pathlib import Path
import json
import uuid
from datetime import datetime

from evcrew.agents import DocumentEvaluator, DocumentImprover

# Utility functions
def format_percentage(value: float) -> str:
    """Format float as percentage string."""
    return f"{value * 100:.1f}%"

def read_file(file_path: str) -> str:
    """Read file and return its contents."""
    return Path(file_path).read_text(encoding="utf-8")

def write_file(file_path: str, content: str) -> None:
    """Write content to file, creating directories if needed."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

configfile: "snakefile-config.yaml"

INPUT_DIR  = Path("docs") / "input"
OUTPUT_DIR = Path("docs") / "output"

MEMORY_ID      = config.get("memory_id")          # may be None
MAX_ITERATIONS = config.get("max_iterations", 3)
TARGET_SCORE   = config.get("target_score", 0.7)

# iterate through all *.md files in docs/input/
DOCS = sorted(INPUT_DIR.glob("*.md"))

def stem(path): return Path(path).stem  # helper to strip extension once


rule all:
    input:
        expand(str(OUTPUT_DIR) + "/{name}/{name}_final.md",
               name=[stem(p) for p in DOCS])

rule evaluate:
    input:
        DOCS
    output:
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

        # Read document
        doc_content = Path(input.doc).read_text()
        
        # Create evaluator and evaluate
        memory_id = params.memory or f"eval_{wildcards.name}_{uuid.uuid4().hex[:8]}"
        evaluator = DocumentEvaluator(memory_id)
        score, feedback = evaluator.evaluate(doc_content)
        
        # Save run data
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        run_dir = OUTPUT_DIR / f"evaluate_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        (run_dir / "input.txt").write_text(doc_content, encoding="utf-8")
        (run_dir / "output.txt").write_text(f"Score: {score}\nFeedback: {feedback}", encoding="utf-8")
        meta = {"run_type": "evaluate", "timestamp": timestamp, "score": score, "feedback": feedback, "memory_id": memory_id}
        (run_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        # Write outputs
        Path(output.score).write_text(format_percentage(score))
        Path(output.feedback).write_text(feedback)

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
        
        print(f"🔄 Starting auto-improvement loop for {doc_path}")
        print(f"Target score: {format_percentage(params.target_score)}")
        print(f"Maximum iterations: {params.max_iter}")
        
        # Setup memory IDs
        base_memory_id = params.memory or f"autodoceval_{wildcards.name}_{uuid.uuid4().hex[:8]}"
        evaluator_memory_id = f"{base_memory_id}_evaluator"
        improver_memory_id = f"{base_memory_id}_improver"
        print(f"🧠 Using memory IDs: {evaluator_memory_id}, {improver_memory_id}")
        
        # Create agents
        evaluator = DocumentEvaluator(evaluator_memory_id)
        improver = DocumentImprover(improver_memory_id)
        
        # Read and evaluate original document
        original_doc = read_file(doc_path)
        original_score, original_feedback = evaluator.evaluate(original_doc)
        print(f"Original document score: {format_percentage(original_score)}")
        
        current_doc = original_doc
        current_feedback = original_feedback
        last_score = original_score
        iteration = 0
        final_path = doc_path
        
        # Skip improvement if already at target
        if original_score >= params.target_score:
            print(f"✅ Original document already meets target score!")
            write_file(output.final, original_doc)
            return
            
        while iteration < params.max_iter:
            iteration += 1
            print(f"\n📝 Iteration {iteration}/{params.max_iter}")
            
            # Improve document
            improved_doc = improver.improve(current_doc, current_feedback)
            
            # Save improved document
            improved_path = OUTPUT_DIR / wildcards.name / f"{wildcards.name}_iter{iteration}.md"
            write_file(str(improved_path), improved_doc)
            final_path = str(improved_path)
            
            # Evaluate improved document
            score, feedback = evaluator.evaluate(improved_doc)
            
            print(f"Score after iteration {iteration}: {format_percentage(score)}")
            improvement = score - last_score
            print(f"Improvement: {format_percentage(improvement)} from previous")
            
            if score >= params.target_score:
                print(f"✅ Target score reached!")
                break
                
            current_doc = improved_doc
            current_feedback = feedback
            last_score = score
            
        print(f"\n📈 Total improvement: {format_percentage(score - original_score)}")
        
        if iteration >= params.max_iter and score < params.target_score:
            print(f"⚠️ Max iterations reached without achieving target")
            
        print("\n✅ Auto-improvement completed!")
        
        # Copy final result
        from shutil import copyfile
        copyfile(final_path, output.final)
