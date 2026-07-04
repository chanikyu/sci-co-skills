"""stages.py — detect which metabolomics stage an input is."""
import os
import pandas as pd

DOWNSTREAM = {
    "feature_table": ["clean/impute", "normalize", "transform+scale", "univariate (+FDR)",
                      "PCA", "PLS-DA (+VIP, permutation)", "heatmap", "figures"],
    "results_table": ["figures (volcano)"],
}
_RES_COLS = {"pvalue", "padj", "log2fc", "statistic", "vip", "qvalue"}


def detect_stage(path):
    sep = "\t" if path.endswith((".tsv", ".txt")) else ","
    df = pd.read_csv(path, sep=sep, index_col=0)
    cols = {c.lower() for c in df.columns}
    if len(cols & _RES_COLS) >= 2:
        return {"stage": "results_table", "detail": f"stats results ({df.shape[0]} features)",
                "downstream": DOWNSTREAM["results_table"]}
    return {"stage": "feature_table",
            "detail": f"{df.shape[0]} samples × {df.select_dtypes('number').shape[1]} metabolites",
            "downstream": DOWNSTREAM["feature_table"]}
