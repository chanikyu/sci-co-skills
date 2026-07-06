"""qc.py — metabolomics QC on a feature table (rows = samples, cols = features):
pooled-QC RSD filter, blank filter, and QC-RLSC (LOESS) signal-drift correction. Pure Python."""
import numpy as np
import pandas as pd


def rsd_filter(df, qc_mask, max_rsd=0.30):
    """Keep features whose relative standard deviation (SD/mean) across pooled-QC samples <= max_rsd.
    Returns (filtered_df, rsd_series). Analytically unreliable features are dropped (reported)."""
    qc = df.loc[qc_mask]
    if qc.shape[0] < 2:
        return df, pd.Series(np.nan, index=df.columns)
    rsd = qc.std(axis=0) / qc.mean(axis=0).abs().replace(0, np.nan)   # |mean| — negatives must not pass
    keep = ((rsd >= 0) & (rsd <= max_rsd)).fillna(False)
    return df.loc[:, keep], rsd


def blank_filter(df, blank_mask, sample_mask, fold=3.0):
    """Drop features whose sample-mean is not > fold × blank-mean (removes contaminants/background)."""
    if not np.asarray(blank_mask).any() or not np.asarray(sample_mask).any():
        return df                                     # no blanks (nothing to subtract) or no samples
    bmean = df.loc[blank_mask].mean(axis=0)
    smean = df.loc[sample_mask].mean(axis=0)
    keep = smean > fold * bmean
    return df.loc[:, keep]


def qc_rlsc(df, qc_mask, run_order, span=0.5):
    """QC-RLSC: fit a LOESS curve to each feature's pooled-QC intensities vs run order, then divide
    every sample by the interpolated curve (× median QC) to remove within-run signal drift."""
    from statsmodels.nonparametric.smoothers_lowess import lowess
    order = pd.to_numeric(pd.Series(run_order), errors="coerce").to_numpy(dtype=float)
    qc_idx = np.where(np.asarray(qc_mask))[0]
    out = df.copy().astype(float)
    if len(qc_idx) < 4 or not np.isfinite(order[qc_idx]).all():
        return out                                    # too few QCs, or QC run-order missing/non-numeric
    frac = min(1.0, max(span, 6.0 / len(qc_idx)))     # widen the window when QCs are few (less overfit)
    qx = order[qc_idx]
    for f in df.columns:
        y = df[f].to_numpy(dtype=float)
        qy = y[qc_idx]
        fin = np.isfinite(qy)
        if fin.sum() < 3 or np.nanstd(qy[fin]) == 0:  # all-NaN / constant QC -> skip (no crash)
            continue
        fit = lowess(qy[fin], qx[fin], frac=frac, return_sorted=True)
        if fit.shape[0] < 2:
            continue
        curve = np.interp(order, fit[:, 0], fit[:, 1])
        curve[curve <= 0] = np.nan
        out[f] = y / curve * np.nanmedian(qy[fin])
    return out.fillna(df.astype(float))
