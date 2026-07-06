"""stages.py — detect which virome stage an input belongs to."""
import os
import numpy as np
import pandas as pd

DOWNSTREAM = {
    "contigs":         ["geNomad identify", "CheckV QC", "dereplicate (vOTU)", "map reads",
                        "preprocess", "alpha", "beta", "differential"],
    "feature_table":   ["preprocess", "alpha", "beta", "differential"],   # vOTU × samples abundance
    "distance_matrix": ["pcoa", "permanova", "beta_figure"],
    "alpha_table":     ["alpha_group_test", "alpha_figure"],
}
_FASTA_EXT = (".fasta", ".fa", ".fna", ".fasta.gz", ".fa.gz", ".fna.gz")
_ALPHA = {"observed", "observed_features", "shannon", "simpson", "pielou", "pielou_e", "chao1"}


def detect_stage(path):
    if path.lower().endswith(_FASTA_EXT):
        return {"stage": "contigs", "detail": "assembled contigs FASTA", "downstream": DOWNSTREAM["contigs"]}
    if os.path.isfile(path):
        with open(path, "r", errors="ignore") as fh:
            if fh.read(1) == ">":
                return {"stage": "contigs", "detail": "FASTA sequences", "downstream": DOWNSTREAM["contigs"]}

    sep = "\t" if path.lower().endswith((".tsv", ".txt")) else ","
    df = pd.read_csv(path, sep=sep, index_col=0)
    if df.shape[0] == df.shape[1] and list(df.index) == list(df.columns) and \
            np.allclose(df.values, df.values.T, atol=1e-6):
        return {"stage": "distance_matrix", "detail": f"{df.shape[0]}×{df.shape[0]} distances",
                "downstream": DOWNSTREAM["distance_matrix"]}
    if {c.lower() for c in df.columns} & _ALPHA:
        return {"stage": "alpha_table", "detail": "alpha metrics", "downstream": DOWNSTREAM["alpha_table"]}
    num = df.select_dtypes("number")
    return {"stage": "feature_table",
            "detail": f"{df.shape[0]} samples × {num.shape[1]} vOTUs",
            "downstream": DOWNSTREAM["feature_table"]}
