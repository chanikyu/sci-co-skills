"""stages.py — detect which metabolomics upstream stage an input belongs to."""
import os
import pandas as pd

DOWNSTREAM = {
    "raw":             ["feature detection", "alignment", "QC (RSD/blank/QC-RLSC)", "annotation (MSI)"],
    "feature_table":   ["QC (RSD/blank/QC-RLSC)", "annotation (MSI)"],
    "annotated_table": ["hand off to microbiome-metabolome-analysis (stats)"],
}
_RAW_EXT = (".mzml", ".mzxml", ".cdf", ".raw", ".d", ".wiff")
_ANN_COLS = {"msi_level", "compound_name", "annotation", "inchikey", "smiles", "match"}


def detect_stage(path):
    if os.path.isdir(path):
        raw = [f for _, _, fs in os.walk(path) for f in fs if f.lower().endswith(_RAW_EXT)]
        if raw:
            return {"stage": "raw", "detail": f"directory with {len(raw)} raw spectra (mzML/.CDF)",
                    "downstream": DOWNSTREAM["raw"]}
        raise ValueError(f"{path} is a directory with no raw spectra ({', '.join(_RAW_EXT)}) — "
                         f"pass an mzML/.CDF directory or a feature-table file.")
    if path.lower().endswith(_RAW_EXT):
        return {"stage": "raw", "detail": "raw spectra file", "downstream": DOWNSTREAM["raw"]}

    sep = "\t" if path.lower().endswith((".tsv", ".txt")) else ","
    df = pd.read_csv(path, sep=sep, index_col=0)
    cols = {c.lower() for c in df.columns}
    if cols & _ANN_COLS:
        return {"stage": "annotated_table", "detail": f"annotated feature table ({df.shape[0]} rows)",
                "downstream": DOWNSTREAM["annotated_table"]}
    return {"stage": "feature_table",
            "detail": f"{df.shape[0]} × {df.shape[1]} feature table (unannotated)",
            "downstream": DOWNSTREAM["feature_table"]}
