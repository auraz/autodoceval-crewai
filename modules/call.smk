rule call:
    input:
        bam = "results/{sample}/aligned.bam"
    output:
        vcf = "results/{sample}/calls.vcf"
    threads: config["threads"]["call"]
    resources:
        mem_mb = config["mem_mb"]["call"]
    params:
        extra = config["params"]["call_extra"]
    shell:
        """
        caller -i {input.bam} -o {output.vcf} {params.extra}
        """
