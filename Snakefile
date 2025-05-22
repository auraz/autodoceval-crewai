import os
from pathlib import Path

config.setdefault("max_iterations", 3)
config.setdefault("target_score", 0.7)
config.setdefault("input_file", "example.md")

OUTPUT_DIR = "output"

def get_output_path(filename, suffix):
    base = os.path.basename(filename)
    name, ext = os.path.splitext(base)
    return os.path.join(OUTPUT_DIR, f"{name}_{suffix}{ext}")


rule all:
    input:
        get_output_path(config["input_file"], "improved")

rule grade:
    input:
        config["infile"]
    output:
        json="f{input}_scores.json"
    shell:
        "python -m autodoceval_crewai.cli grade {input} --output {output.json}"


rule improve:
    input:
        doc="{file}",
        feedback="{file}_scores.json"
    output:
        "{file}_improved.md"
    shell:
        "python -m autodoceval_crewai.cli improve {input.doc} --feedback {input.feedback} --output {output}"

rule auto_improve:
    input:
        "{file}"
    output:
        directory("{file}_iterations")
    params:
        iterations=config["max_iterations"],
        target=config["target_score"]
    shell:
        """
        mkdir -p {output}
        python -m autodoceval_crewai.cli auto-improve {input} --iterations {params.iterations} --target {params.target}
        """

# Clean outputs
rule clean:
    shell:
        "rm -rf {OUTPUT_DIR}/*_scores.json {OUTPUT_DIR}/*_improved.md {OUTPUT_DIR}/*_iterations"

# Initialize project structure
rule init:
    output:
        directory(OUTPUT_DIR)
    shell:
        "mkdir -p {output}"