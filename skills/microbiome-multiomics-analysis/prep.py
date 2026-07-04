"""prep.py — multi-omics sample alignment + per-omic filtering and compositional transform.
Each omic table is rows = samples, cols = features."""
import numpy as np
import pandas as pd


def align(omics, meta, min_overlap=8):
    """Intersect sample IDs across all omics + metadata. Returns (aligned_omics, meta, ids, dropped)."""
    for name, df in {**omics, "metadata": meta}.items():
        if not df.index.is_unique:
            dups = df.index[df.index.duplicated()].tolist()
            raise ValueError(f"{name}: duplicate sample IDs {dups} — sample IDs must be unique per table.")
    common = set(meta.index)
    for df in omics.values():
        common &= set(df.index)
    ids = sorted(common)
    if len(ids) < min_overlap:
        raise ValueError(f"Only {len(ids)} samples overlap across omics + metadata "
                         f"(need >= {min_overlap}). Check that sample IDs match across tables.")
    aligned = {k: df.loc[ids] for k, df in omics.items()}
    dropped = {k: sorted(set(df.index) - set(ids)) for k, df in omics.items()}
    return aligned, meta.loc[ids], ids, dropped


def filter_features(df, min_prevalence=0.1, top_n=None):
    """Prevalence filter, then (optional) keep the top_n most-abundant features to bound test count."""
    df = df.loc[:, (df > 0).mean(axis=0) >= min_prevalence]
    if top_n and df.shape[1] > top_n:
        df = df[df.mean(axis=0).sort_values(ascending=False).index[:top_n]]
    return df


def clr_transform(df):
    """Compositional transform: closure -> zero replacement -> centered log-ratio (scikit-bio)."""
    from skbio.stats.composition import clr, closure
    try:
        from skbio.stats.composition import multi_replace as _zrep      # scikit-bio >= 0.6
    except ImportError:                                                 # older name
        from skbio.stats.composition import multiplicative_replacement as _zrep
    X = closure(df.values.astype(float))
    return pd.DataFrame(clr(_zrep(X)), index=df.index, columns=df.columns)


def log_scale(df):
    """Metabolome transform: log10 (adaptive pseudocount) -> auto-scale (unit variance)."""
    pos = df.values[df.values > 0]
    c = 0.5 * pos.min() if pos.size else 1.0
    lg = np.log10(df + c)
    return (lg - lg.mean(axis=0)) / lg.std(axis=0).replace(0, 1.0)


def transform_omic(name, df, compositional=None):
    """CLR for compositional omics (taxa/genes/transcripts); log+scale for metabolome.
    Heuristic by name unless `compositional` (bool) is given."""
    if compositional is None:
        compositional = "metabol" not in name.lower()
    return clr_transform(df) if compositional else log_scale(df)
