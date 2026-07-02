"""
differential.py — differential abundance testing.

Methods (all opt-in; default clr_test):
- clr_test    : centered-log-ratio + per-feature Mann-Whitney/Kruskal + BH-FDR (compositional).
- kruskal_lfc : Kruskal-Wallis on relative abundance + log2 fold-change effect + BH-FDR.
- pydeseq2    : DESeq2-style negative-binomial (counts only) — used only if pydeseq2 is installed.

Every method returns a tidy DataFrame [feature, stat, p, p_adj, effect, enriched_in,
significant] and a human-readable method label. Multiple-testing correction is always applied.
"""
import numpy as np
import pandas as pd
from scipy import stats as sps


def _bh(pvals):
    """Benjamini-Hochberg FDR-adjusted p-values."""
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    adj = np.empty(n)
    prev = 1.0
    for rank in range(n - 1, -1, -1):
        idx = order[rank]
        prev = min(prev, p[idx] * n / (rank + 1))
        adj[idx] = min(prev, 1.0)
    return adj


def _as_groups(index, groups):
    g = groups if isinstance(groups, pd.Series) else pd.Series(list(groups), index=index)
    return g.loc[index]


def clr_test(clr_df, groups, alpha=0.05):
    """CLR + per-feature nonparametric test + BH. clr_df: CLR-transformed table
    (samples × features). Returns (DataFrame, method_label)."""
    groups = _as_groups(clr_df.index, groups)
    labs = list(pd.unique(groups))
    two = len(labs) == 2
    rows = []
    for feat in clr_df.columns:
        vals = [clr_df.loc[groups == g, feat].values for g in labs]
        if two:
            stat, p = sps.mannwhitneyu(vals[0], vals[1], alternative="two-sided")
            effect = float(np.mean(vals[1]) - np.mean(vals[0]))   # + => higher in labs[1]
            enriched = labs[1] if effect > 0 else labs[0]
        else:
            stat, p = sps.kruskal(*vals)
            means = {g: float(np.mean(v)) for g, v in zip(labs, vals)}
            enriched = max(means, key=means.get)
            effect = float(max(means.values()) - min(means.values()))
        rows.append((feat, float(stat), float(p), effect, enriched))
    df = pd.DataFrame(rows, columns=["feature", "stat", "p", "effect_clr", "enriched_in"])
    df["p_adj"] = _bh(df["p"].values)
    df["significant"] = df["p_adj"] < alpha
    label = "CLR + Mann-Whitney U + BH-FDR" if two else "CLR + Kruskal-Wallis + BH-FDR"
    return df.sort_values("p_adj").reset_index(drop=True), label


def kruskal_lfc(rel_df, groups, alpha=0.05, eps=1e-6):
    """Kruskal-Wallis on relative abundance + log2 fold-change effect (2 groups)."""
    groups = _as_groups(rel_df.index, groups)
    labs = list(pd.unique(groups))
    two = len(labs) == 2
    rows = []
    for feat in rel_df.columns:
        vals = [rel_df.loc[groups == g, feat].values for g in labs]
        stat, p = sps.kruskal(*vals)
        means = {g: float(np.mean(v)) for g, v in zip(labs, vals)}
        if two:
            effect = float(np.log2((means[labs[1]] + eps) / (means[labs[0]] + eps)))
            enriched = labs[1] if effect > 0 else labs[0]
        else:
            enriched = max(means, key=means.get)
            effect = float(np.log2((max(means.values()) + eps) / (min(means.values()) + eps)))
        rows.append((feat, float(stat), float(p), effect, enriched))
    df = pd.DataFrame(rows, columns=["feature", "stat", "p", "log2fc", "enriched_in"])
    df["p_adj"] = _bh(df["p"].values)
    df["significant"] = df["p_adj"] < alpha
    return df.sort_values("p_adj").reset_index(drop=True), "Kruskal-Wallis + log2FC + BH-FDR"


def pydeseq2(counts_df, metadata, group_col, alpha=0.05):
    """DESeq2-style DA (counts only). Requires the optional `pydeseq2` package;
    raises a clear error if it is not installed."""
    try:
        from pydeseq2.dds import DeseqDataSet
        from pydeseq2.ds import DeseqStats
    except ImportError as e:
        raise ImportError("pydeseq2 not installed. `pip install pydeseq2` (counts input "
                          "required), or use clr_test / kruskal_lfc.") from e
    meta = metadata.loc[counts_df.index, [group_col]].copy()
    dds = DeseqDataSet(counts=counts_df.round().astype(int), metadata=meta,
                       design_factors=group_col, quiet=True)
    dds.deseq2()
    res = DeseqStats(dds, quiet=True)
    res.summary()
    out = res.results_df.reset_index().rename(
        columns={"index": "feature", "log2FoldChange": "log2fc", "pvalue": "p", "padj": "p_adj"})
    out["significant"] = out["p_adj"] < alpha
    return out.sort_values("p_adj").reset_index(drop=True), "DESeq2 (pydeseq2, Wald + BH)"
