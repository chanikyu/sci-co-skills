"""
stages.py — detect which stage a genome-analysis input belongs to.

Raw reads enter the full backbone (QC -> assembly -> assembly QC -> annotation -> species ID);
an assembled contigs FASTA enters from assembly QC onward. Mirrors shotgun-analysis/stages.py.
"""
import os

DOWNSTREAM = {
    "fastq":    ["fastp QC", "assembly", "assembly QC (QUAST/CheckM2)", "annotation", "species ID"],
    "assembly": ["assembly QC (QUAST/CheckM2)", "annotation", "species ID"],
}

_FASTQ_EXT = (".fastq", ".fq", ".fastq.gz", ".fq.gz")
_FASTA_EXT = (".fasta", ".fa", ".fna", ".fasta.gz", ".fa.gz", ".fna.gz")


def detect_stage(path):
    """Return {stage, detail, downstream}. A .fastq[.gz] file or a directory of them → fastq;
    a nucleotide FASTA of contigs → assembly."""
    if os.path.isdir(path):
        files = os.listdir(path)
        if any(f.lower().endswith(_FASTQ_EXT) for f in files):
            return {"stage": "fastq", "detail": "directory of FASTQ reads",
                    "downstream": DOWNSTREAM["fastq"]}
        if any(f.lower().endswith(_FASTA_EXT) for f in files):
            return {"stage": "assembly", "detail": "directory with a contigs FASTA",
                    "downstream": DOWNSTREAM["assembly"]}
        raise ValueError(f"no FASTQ or FASTA found in directory: {path}")

    low = path.lower()
    if low.endswith(_FASTQ_EXT):
        return {"stage": "fastq", "detail": "FASTQ reads", "downstream": DOWNSTREAM["fastq"]}
    if low.endswith(_FASTA_EXT):
        return {"stage": "assembly", "detail": "contigs FASTA", "downstream": DOWNSTREAM["assembly"]}
    raise ValueError(f"unrecognized input (expected FASTQ or FASTA): {path}")
