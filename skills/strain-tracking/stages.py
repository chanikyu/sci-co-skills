"""stages.py — detect which strain-tracking stage an input belongs to."""
import os
import numpy as np
import pandas as pd

_FASTQ_EXT = (".fastq", ".fq", ".fastq.gz", ".fq.gz")


def _is_square_symmetric(df):
    return (df.shape[0] == df.shape[1] and list(df.index) == list(df.columns)
            and np.allclose(df.values, df.values.T, atol=1e-6, equal_nan=True))


def detect_stage(path):
    """reads directory · a single per-species strain distance/identity matrix · a directory of matrices."""
    if os.path.isdir(path):
        reads = [f for _, _, fs in os.walk(path) for f in fs if f.lower().endswith(_FASTQ_EXT)]
        if reads:
            return {"stage": "reads", "detail": f"directory with {len(reads)} read files"}
        mats = [f for f in os.listdir(path) if f.lower().endswith((".csv", ".tsv"))]
        if mats:
            return {"stage": "matrix_dir", "detail": f"{len(mats)} per-species matrices"}
        raise ValueError(f"{path} is a directory with no FASTQ reads or matrices.")
    if path.lower().endswith(_FASTQ_EXT):
        return {"stage": "reads", "detail": "reads"}
    sep = "\t" if path.lower().endswith((".tsv", ".txt")) else ","
    df = pd.read_csv(path, sep=sep, index_col=0)
    if _is_square_symmetric(df):
        return {"stage": "distance_matrix", "detail": f"{df.shape[0]}×{df.shape[0]} strain matrix (1 species)"}
    raise ValueError(f"{path} is not a square symmetric strain matrix — pass a reads dir, a matrix, or a matrix dir.")
