"""
stages.py — detect which pipeline stage an input belongs to, and the steps that
run downstream from it. This powers the "enter at any stage" behavior: give raw
FASTQ, a feature table, a distance matrix, or an alpha table, and the skill runs
from that point forward.
"""
import os
import pandas as pd

# ordered pipeline; each artifact enters at a point and runs everything after it
DOWNSTREAM = {
    "fastq":           ["denoise (DADA2)", "assign_taxonomy (optional, needs DB)",
                        "preprocess", "alpha", "beta", "differential"],
    "feature_table":   ["preprocess", "alpha", "beta", "differential"],
    "distance_matrix": ["pcoa", "permanova", "beta_figure"],
    "alpha_table":     ["alpha_group_test", "alpha_figure"],
}

_FASTQ_EXT = (".fastq", ".fq", ".fastq.gz", ".fq.gz")
_ALPHA_NAMES = {"observed", "observed_features", "shannon", "simpson",
                "pielou", "pielou_e", "pielou_evenness", "chao1", "faith_pd"}


def detect_stage(path):
    """Inspect `path` and return {stage, detail, downstream}.

    stage ∈ fastq | feature_table | distance_matrix | alpha_table.
    Raw reads (a .fastq[.gz] file or a directory of them) → fastq.
    A square, symmetric numeric table with matching row/col labels → distance_matrix.
    A table whose columns are alpha-diversity metrics → alpha_table.
    Otherwise a samples × features table → feature_table (+ counts/relative subtype).
    """
    # raw reads: a fastq file, or a directory containing fastq files
    if os.path.isdir(path):
        if any(f.lower().endswith(_FASTQ_EXT) for f in os.listdir(path)):
            return {"stage": "fastq", "detail": "directory of FASTQ reads",
                    "downstream": DOWNSTREAM["fastq"]}
    if path.lower().endswith(_FASTQ_EXT):
        return {"stage": "fastq", "detail": "FASTQ reads",
                "downstream": DOWNSTREAM["fastq"]}

    sep = "\t" if path.endswith((".tsv", ".txt")) else ","
    df = pd.read_csv(path, sep=sep, index_col=0)
    numeric = df.select_dtypes("number")

    # distance matrix: square, symmetric, labels match
    if df.shape[0] == df.shape[1] and list(df.index) == list(df.columns):
        import numpy as np
        if np.allclose(df.values, df.values.T, atol=1e-6):
            return {"stage": "distance_matrix", "detail": f"{df.shape[0]}×{df.shape[0]} distances",
                    "downstream": DOWNSTREAM["distance_matrix"]}

    # alpha table: columns are alpha metrics
    cols = {c.lower() for c in df.columns}
    if cols & _ALPHA_NAMES:
        found = sorted(cols & _ALPHA_NAMES)
        return {"stage": "alpha_table", "detail": f"alpha metrics: {', '.join(found)}",
                "downstream": DOWNSTREAM["alpha_table"]}

    # otherwise a feature table
    X = numeric.values
    import numpy as np
    is_counts = np.allclose(X, np.round(X)) and (X.sum(axis=1) > 1.5).any()
    subtype = "counts" if is_counts else "relative abundance"
    return {"stage": "feature_table", "detail": f"{df.shape[0]} samples × {numeric.shape[1]} features ({subtype})",
            "downstream": DOWNSTREAM["feature_table"]}
