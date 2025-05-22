rule qc:
    input:
        bam = "results/{sample}/aligned.bam"
    output:
        rpt = "results/{sample}/qc.txt"
    shell:
        """
        qc_tool -i {input.bam} > {output.rpt}
        """
