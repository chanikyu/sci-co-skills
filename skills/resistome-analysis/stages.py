"""stages.py — detect which resistome stage an input belongs to."""
import os
import numpy as np
import pandas as pd

DOWNSTREAM = {
    "reads":           ["ARG detection", "hAMRonize", "normalize", "aggregate (drug class)",
                        "preprocess", "alpha", "beta", "differential"],
    "feature_table":   ["preprocess", "alpha", "beta", "differential", "drug-class summary"],
    "distance_matrix": ["pcoa", "permanova", "beta_figure"],
    "alpha_table":     ["alpha_group_test", "alpha_figure"],
}
_FASTQ_EXT = (".fastq", ".fq", ".fastq.gz", ".fq.gz")
_ALPHA = {"observed", "observed_features", "shannon", "simpson", "pielou", "pielou_e", "chao1"}


def detect_stage(path):
    if os.path.isdir(path):
        reads = [f for _, _, fs in os.walk(path) for f in fs if f.lower().endswith(_FASTQ_EXT)]
        if reads:
            return {"stage": "reads", "detail": f"directory with {len(reads)} read files",
                    "downstream": DOWNSTREAM["reads"]}
        raise ValueError(f"{path} is a directory with no FASTQ reads — pass a reads dir or an ARG table.")
    if path.lower().endswith(_FASTQ_EXT):
        return {"stage": "reads", "detail": "reads", "downstream": DOWNSTREAM["reads"]}

    sep = "\t" if path.lower().endswith((".tsv", ".txt")) else ","
    df = pd.read_csv(path, sep=sep, index_col=0)
    if df.shape[0] == df.shape[1] and list(df.index) == list(df.columns) and \
            np.allclose(df.values, df.values.T, atol=1e-6, equal_nan=True):
        return {"stage": "distance_matrix", "detail": f"{df.shape[0]}×{df.shape[0]} distances",
                "downstream": DOWNSTREAM["distance_matrix"]}
    if {c.lower() for c in df.columns} & _ALPHA:
        return {"stage": "alpha_table", "detail": "alpha metrics", "downstream": DOWNSTREAM["alpha_table"]}
    num = df.select_dtypes("number")
    return {"stage": "feature_table",
            "detail": f"{df.shape[0]} samples × {num.shape[1]} ARGs",
            "downstream": DOWNSTREAM["feature_table"]}
