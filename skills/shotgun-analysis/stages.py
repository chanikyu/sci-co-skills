"""
stages.py — detect which shotgun pipeline stage an input belongs to.

Raw FASTQ enters the shotgun front stages (QC → host removal → profiling); an abundance
table / distance matrix / alpha table enters the shared downstream (reused from
amplicon-analysis). Mirrors amplicon-analysis/stages.py.
"""
import os
import numpy as np
import pandas as pd

DOWNSTREAM = {
    "fastq":           ["fastp QC", "host removal (optional)",
                        "taxonomic profiling (MetaPhlAn/Kraken2)",
                        "functional profiling (HUMAnN, optional)",
                        "preprocess", "alpha", "beta", "differential"],
    "feature_table":   ["preprocess", "alpha", "beta", "differential"],  # abundance table
    "distance_matrix": ["pcoa", "permanova", "beta_figure"],
    "alpha_table":     ["alpha_group_test", "alpha_figure"],
}

_FASTQ_EXT = (".fastq", ".fq", ".fastq.gz", ".fq.gz")
_ALPHA_NAMES = {"observed", "observed_features", "shannon", "simpson",
                "pielou", "pielou_e", "pielou_evenness", "chao1", "faith_pd"}


def detect_stage(path):
    """Return {stage, detail, downstream}. Raw reads → fastq; a square symmetric table →
    distance_matrix; alpha-metric columns → alpha_table; otherwise a samples × features
    abundance table → feature_table."""
    if os.path.isdir(path):
        if any(f.lower().endswith(_FASTQ_EXT) for f in os.listdir(path)):
            return {"stage": "fastq", "detail": "directory of FASTQ reads",
                    "downstream": DOWNSTREAM["fastq"]}
    if path.lower().endswith(_FASTQ_EXT):
        return {"stage": "fastq", "detail": "FASTQ reads", "downstream": DOWNSTREAM["fastq"]}

    sep = "\t" if path.endswith((".tsv", ".txt")) else ","
    df = pd.read_csv(path, sep=sep, index_col=0)

    if df.shape[0] == df.shape[1] and list(df.index) == list(df.columns):
        if np.allclose(df.values, df.values.T, atol=1e-6):
            return {"stage": "distance_matrix", "detail": f"{df.shape[0]}×{df.shape[0]} distances",
                    "downstream": DOWNSTREAM["distance_matrix"]}

    if {c.lower() for c in df.columns} & _ALPHA_NAMES:
        found = sorted({c.lower() for c in df.columns} & _ALPHA_NAMES)
        return {"stage": "alpha_table", "detail": f"alpha metrics: {', '.join(found)}",
                "downstream": DOWNSTREAM["alpha_table"]}

    num = df.select_dtypes("number")
    X = num.values
    is_counts = np.allclose(X, np.round(X)) and (X.sum(axis=1) > 1.5).any()
    return {"stage": "feature_table",
            "detail": f"{df.shape[0]} samples × {num.shape[1]} features "
                      f"({'counts' if is_counts else 'relative abundance'})",
            "downstream": DOWNSTREAM["feature_table"]}
