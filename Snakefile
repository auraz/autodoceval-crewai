configfile: "config.yaml"

import os
SAMPLES  = config["samples"]
WORKDIR  = config.get("workdir", "results")   # change “results” if you kept “work”
def outdir(sample): return f"{WORKDIR}/{sample}"

localrules: all

rule all:
    input:
        expand(outdir("{sample}") + "/final.out",
               sample=SAMPLES)

rule process_sample:
    input:
        fq   = "data/{sample}.fastq",
        ref  = config["reference"]          # path stored in YAML
    output:
        bam  = temp(outdir("{sample}") + "/aligned.bam"),
        vcf  =       outdir("{sample}") + "/calls.vcf",
        rpt  =       outdir("{sample}") + "/qc.txt"
    resources:
        threads = config["threads"]["process"],
        mem_mb  = config["mem_mb"]["process"]
    shell:
        """
        aligner -t {resources.threads} -r {input.ref} \
                -i {input.fq} -o {output.bam}
        caller  -i {output.bam} -o {output.vcf}
        qc_tool -i {output.bam} > {output.rpt}
        """

if not workflow.is_local:
    include: "cluster_profile.smk"
