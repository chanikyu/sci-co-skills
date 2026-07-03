"""stages.py — detect which transcriptome stage an input belongs to."""
import os
import numpy as np
import pandas as pd

DOWNSTREAM = {
    "fastq":        ["fastp QC", "quantify (salmon/kallisto/star)", "differential expression", "enrichment"],
    "count_matrix": ["differential expression (pydeseq2)", "enrichment", "figures"],
    "de_table":     ["figures (volcano)"],
}
_FASTQ_EXT = (".fastq", ".fq", ".fastq.gz", ".fq.gz")
_DE_COLS = {"log2foldchange", "padj", "pvalue", "basemean", "lfcse", "stat"}


def detect_stage(path):
    if os.path.isdir(path):
        if any(f.lower().endswith(_FASTQ_EXT) for f in os.listdir(path)):
            return {"stage": "fastq", "detail": "directory of FASTQ reads", "downstream": DOWNSTREAM["fastq"]}
    if path.lower().endswith(_FASTQ_EXT):
        return {"stage": "fastq", "detail": "FASTQ reads", "downstream": DOWNSTREAM["fastq"]}

    sep = "\t" if path.endswith((".tsv", ".txt")) else ","
    df = pd.read_csv(path, sep=sep, index_col=0)
    cols = {c.lower() for c in df.columns}
    if len(cols & _DE_COLS) >= 2:
        return {"stage": "de_table", "detail": f"DE results ({df.shape[0]} genes)",
                "downstream": DOWNSTREAM["de_table"]}
    num = df.select_dtypes("number")
    X = num.values
    is_counts = np.allclose(X, np.round(X)) and X.max() > 20
    return {"stage": "count_matrix",
            "detail": f"{df.shape[0]} genes × {num.shape[1]} samples ({'counts' if is_counts else 'values'})",
            "downstream": DOWNSTREAM["count_matrix"]}
