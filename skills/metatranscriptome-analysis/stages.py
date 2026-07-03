"""stages.py — detect which metatranscriptome stage an input belongs to.
Raw RNA reads -> front stages (QC -> host -> rRNA removal -> profiling); an abundance table /
distance matrix / alpha table -> the shared downstream (reused from amplicon-analysis)."""
import os
import numpy as np
import pandas as pd

DOWNSTREAM = {
    "fastq":           ["fastp QC", "host removal (optional)", "rRNA removal (SortMeRNA)",
                        "functional profiling (HUMAnN) / taxonomic (MetaPhlAn)",
                        "preprocess", "alpha", "beta", "differential"],
    "feature_table":   ["preprocess", "alpha", "beta", "differential"],   # function/pathway or taxa abundance
    "distance_matrix": ["pcoa", "permanova", "beta_figure"],
    "alpha_table":     ["alpha_group_test", "alpha_figure"],
}
_FASTQ_EXT = (".fastq", ".fq", ".fastq.gz", ".fq.gz")
_ALPHA = {"observed", "observed_features", "shannon", "simpson", "pielou", "pielou_e", "chao1", "faith_pd"}


def detect_stage(path):
    if os.path.isdir(path):
        if any(f.lower().endswith(_FASTQ_EXT) for f in os.listdir(path)):
            return {"stage": "fastq", "detail": "directory of RNA FASTQ reads", "downstream": DOWNSTREAM["fastq"]}
    if path.lower().endswith(_FASTQ_EXT):
        return {"stage": "fastq", "detail": "RNA FASTQ reads", "downstream": DOWNSTREAM["fastq"]}

    sep = "\t" if path.endswith((".tsv", ".txt")) else ","
    df = pd.read_csv(path, sep=sep, index_col=0)
    if df.shape[0] == df.shape[1] and list(df.index) == list(df.columns) and \
            np.allclose(df.values, df.values.T, atol=1e-6):
        return {"stage": "distance_matrix", "detail": f"{df.shape[0]}×{df.shape[0]} distances",
                "downstream": DOWNSTREAM["distance_matrix"]}
    if {c.lower() for c in df.columns} & _ALPHA:
        return {"stage": "alpha_table", "detail": "alpha metrics",
                "downstream": DOWNSTREAM["alpha_table"]}
    num = df.select_dtypes("number")
    return {"stage": "feature_table",
            "detail": f"{df.shape[0]} features × {num.shape[1]} samples (function/taxa abundance)",
            "downstream": DOWNSTREAM["feature_table"]}
