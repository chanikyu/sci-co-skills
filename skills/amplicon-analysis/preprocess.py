"""
preprocess.py — load, validate, filter, and normalize an amplicon feature table.

Handles counts OR relative-abundance tables (auto-detected). Joins a feature table
to sample metadata on sample_id and reports mismatches (never silently drops).
Provides filtering, rarefaction (counts only), relative normalization, and CLR.
"""
import numpy as np
import pandas as pd


def load_table(path, index_col=0):
    """Load a samples × features table (CSV/TSV). Rows=samples (index=sample_id)."""
    sep = "\t" if str(path).endswith((".tsv", ".txt")) else ","
    return pd.read_csv(path, sep=sep, index_col=index_col)


def load_metadata(path, id_col="sample_id"):
    """Load sample metadata; index = sample_id."""
    sep = "\t" if str(path).endswith((".tsv", ".txt")) else ","
    df = pd.read_csv(path, sep=sep)
    if id_col in df.columns:
        df = df.set_index(id_col)
    else:
        df = df.set_index(df.columns[0])
    return df


def detect_type(table):
    """Return 'counts' or 'relative'. Integers with large row sums -> counts;
    rows summing to ~1 -> relative; ambiguous -> 'relative' (documented default)."""
    X = table.values.astype(float)
    rowsums = X.sum(axis=1)
    near_int = np.allclose(X, np.round(X))
    sums_to_one = np.allclose(rowsums, 1.0, atol=0.02)
    if sums_to_one and not (near_int and (X > 1).any()):
        return "relative"
    if near_int and (rowsums > 1.5).any():
        return "counts"
    return "relative"


def join(table, metadata):
    """Inner-join table and metadata on sample_id. Returns (table, metadata, report).
    report lists IDs present in only one file — surface these, do not hide them."""
    common = table.index.intersection(metadata.index)
    report = {
        "n_common": int(len(common)),
        "only_in_table": list(table.index.difference(metadata.index)),
        "only_in_metadata": list(metadata.index.difference(table.index)),
    }
    return table.loc[common], metadata.loc[common], report


def filter_features(table, min_prevalence=0.1, min_total=0.0):
    """Drop low-prevalence / low-abundance features.
    min_prevalence: fraction of samples in which a feature must be present.
    min_total: minimum column sum (in the table's own units) to keep.
    Returns (filtered_table, removed_feature_names)."""
    present = (table > 0).mean(axis=0)
    totals = table.sum(axis=0)
    keep = (present >= min_prevalence) & (totals >= min_total)
    return table.loc[:, keep], list(table.columns[~keep])


def rarefy(counts, depth=None, seed=0):
    """Subsample each sample WITHOUT replacement to an even depth (counts only).
    depth defaults to the minimum sample total. Samples below depth are dropped.
    Rarefaction discards data — use deliberately. Returns (rarefied, depth, dropped)."""
    counts = counts.round().astype(int)
    totals = counts.sum(axis=1)
    if depth is None:
        depth = int(totals.min())
    rng = np.random.default_rng(seed)
    rows, keep, dropped = [], [], []
    for sid, row in counts.iterrows():
        if int(row.sum()) < depth:
            dropped.append(sid)
            continue
        rows.append(rng.multivariate_hypergeometric(row.values, depth))
        keep.append(sid)
    return pd.DataFrame(rows, index=keep, columns=counts.columns), depth, dropped


def to_relative(table):
    """Row-normalize to relative abundance (each sample sums to 1)."""
    return table.div(table.sum(axis=1), axis=0)


def clr(table, pseudocount=None):
    """Centered log-ratio transform (compositional). Zeros get a pseudocount
    (default: half the smallest nonzero value). Works on counts or relative."""
    X = table.values.astype(float)
    if pseudocount is None:
        nz = X[X > 0]
        pseudocount = (nz.min() / 2) if nz.size else 1e-6
    logX = np.log(X + pseudocount)
    clr_vals = logX - logX.mean(axis=1, keepdims=True)
    return pd.DataFrame(clr_vals, index=table.index, columns=table.columns)
