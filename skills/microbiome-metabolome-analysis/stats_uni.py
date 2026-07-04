"""stats_uni.py — univariate metabolomics statistics + fold-change (BH-FDR corrected).
Run on transformed (log), UNSCALED data; fold-change on the original / normalized (non-log) scale."""
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests


def run_univariate(df, groups, test="auto", paired=False):
    """df: samples × features (log, unscaled). Returns per-feature table (statistic, pvalue, padj)."""
    g = pd.Series(list(groups), index=df.index).astype(str)
    levels = sorted(pd.unique(g).tolist())           # deterministic; ref = levels[0]
    pvals, stat_ = [], []
    for f in df.columns:
        data = [df.loc[g == lv, f].values for lv in levels]
        if len(levels) == 2:
            a, b = data[1], data[0]                   # test = levels[1] vs ref = levels[0] (matches log2FC sign)
            if paired and test == "mannwhitney":
                s, p = stats.wilcoxon(a, b)
            elif paired:
                s, p = stats.ttest_rel(a, b)
            elif test == "mannwhitney":
                s, p = stats.mannwhitneyu(a, b, alternative="two-sided")
            else:                                    # auto/ttest -> Welch
                s, p = stats.ttest_ind(a, b, equal_var=False)
        else:
            s, p = (stats.kruskal(*data) if test == "kruskal" else stats.f_oneway(*data))
        pvals.append(float(p)); stat_.append(float(s))
    padj = multipletests(np.nan_to_num(pvals, nan=1.0), method="fdr_bh")[1]
    return pd.DataFrame({"statistic": stat_, "pvalue": pvals, "padj": padj}, index=df.columns)


def fold_change(df_raw, groups, test_level, ref_level):
    """log2 fold-change (test vs ref) per feature, on the original / normalized (non-log) scale."""
    g = pd.Series(list(groups), index=df_raw.index).astype(str)
    ma = df_raw.loc[g == test_level].mean(axis=0)
    mb = df_raw.loc[g == ref_level].mean(axis=0)
    m = df_raw[df_raw > 0].min().min()
    eps = m if (pd.notna(m) and m > 0) else 1e-9
    return np.log2((ma + eps) / (mb + eps))


def n_significant(res, padj=0.05, lfc=1.0):
    r = res.dropna(subset=["padj"])
    if lfc is not None and "log2FC" in r.columns:
        return int(((r["padj"] < padj) & (r["log2FC"].abs() >= lfc)).sum())
    return int((r["padj"] < padj).sum())
