rule align:
    input:
        fq = "data/{sample}.fastq",
        ref = config["reference"]
    output:
        bam = temp("results/{sample}/aligned.bam")
    threads: config["threads"]["align"]
    resources:
        mem_mb = config["mem_mb"]["align"]
    params:
        extra = config["params"]["align_extra"]
    shell:
        """
        aligner -t {threads} -r {input.ref} -i {input.fq} -o {output.bam} {params.extra}
        """
