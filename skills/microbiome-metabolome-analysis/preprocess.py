"""preprocess.py — metabolomics feature-table preprocessing (rows = samples, cols = metabolites).
Order (do not change): filter/impute -> sample normalization -> transformation -> feature scaling.
All steps are group-blind (no leakage)."""
import numpy as np
import pandas as pd


def impute_missing(df, method="halfmin", max_missing=0.5):
    """Treat 0 and NaN as missing. Drop features missing in > max_missing of samples, then impute.
    Returns (imputed_df, n_features_dropped)."""
    x = df.replace(0, np.nan)
    keep = x.isna().mean(axis=0) <= max_missing
    dropped = int((~keep).sum())
    x = x.loc[:, keep]
    if method == "knn":
        from sklearn.impute import KNNImputer
        k = max(2, min(5, x.shape[0] - 1))
        x = pd.DataFrame(KNNImputer(n_neighbors=k).fit_transform(x), index=x.index, columns=x.columns)
    else:  # half-minimum (per feature)
        x = x.fillna(x.min(axis=0, skipna=True) / 2.0)
    x = x.dropna(axis=1, how="all")                # guard: drop any feature with no observed value
    return x, dropped


def filter_features(df, min_prevalence=0.1, low_var_quantile=0.0):
    prev = (df > 0).mean(axis=0)
    df = df.loc[:, prev >= min_prevalence]
    if low_var_quantile > 0:
        v = df.var(axis=0)
        df = df.loc[:, v >= v.quantile(low_var_quantile)]
    return df


def normalize_samples(df, method="pqn"):
    """Sample-wise (row) normalization to correct per-sample dilution/amount."""
    if method == "tss":
        return df.div(df.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    if method == "median":
        return df.div(df.median(axis=1).replace(0, np.nan), axis=0).fillna(df)
    # PQN: total-sum normalize -> reference = median spectrum -> divide by median quotient
    tss = df.div(df.sum(axis=1), axis=0)
    ref = tss.median(axis=0).replace(0, np.nan)
    quot = tss.div(ref, axis=1)
    factor = quot.median(axis=1).replace(0, np.nan)
    return tss.div(factor, axis=0).fillna(tss)


def transform(df, method="log10"):
    pos = df.values[df.values > 0]
    lam = pos.min() if pos.size else 1.0
    if method == "glog":
        return np.log2((df + np.sqrt(df ** 2 + lam ** 2)) / 2.0)
    # adaptive pseudocount (fraction of the min positive value) — a fixed +1 would linearize
    # proportion-scale (PQN/TSS) data and defeat the log transform.
    return np.log10(df + 0.5 * lam)


def scale_features(df, method="pareto"):
    """Column (feature) scaling."""
    mu = df.mean(axis=0)
    sd = df.std(axis=0).replace(0, 1.0)
    if method == "auto":
        return (df - mu) / sd
    if method == "range":
        rng = (df.max(axis=0) - df.min(axis=0)).replace(0, 1.0)
        return (df - mu) / rng
    return (df - mu) / np.sqrt(sd)  # Pareto (default)
