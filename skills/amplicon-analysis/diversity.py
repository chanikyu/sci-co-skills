"""
diversity.py — alpha and beta diversity via scikit-bio.

Alpha: per-sample richness/evenness metrics. Beta: sample-sample distances + PCoA
(with % variance explained) + PERMANOVA group test. scikit-bio is the engine; it
requires Python <= 3.12.
"""
import numpy as np
import pandas as pd
from skbio.diversity import alpha_diversity, beta_diversity
from skbio.stats.ordination import pcoa as _skbio_pcoa
from skbio.stats.distance import permanova as _skbio_permanova

ALPHA_COUNTS = ["observed_features", "shannon", "simpson", "pielou_e", "chao1"]
ALPHA_RELATIVE = ["observed_features", "shannon", "simpson", "pielou_e"]  # chao1 needs counts


def alpha_table(table, counts=True):
    """Per-sample alpha diversity DataFrame. counts=True enables chao1 (needs integers).
    Shannon is reported in nats (natural log)."""
    mat = table.values
    ids = list(table.index)
    metrics = ALPHA_COUNTS if counts else ALPHA_RELATIVE
    cols = {}
    for m in metrics:
        kw = {"base": np.e} if m == "shannon" else {}
        cols[m] = alpha_diversity(m, mat, ids=ids, validate=counts, **kw)
    return pd.DataFrame(cols)


def beta_distance(rel_table, metric="braycurtis"):
    """Sample-sample distance matrix (skbio DistanceMatrix) from a relative-abundance
    table. metric: 'braycurtis' or 'jaccard'."""
    return beta_diversity(metric, rel_table.values, ids=list(rel_table.index),
                          validate=False)


def ordinate(dm, k=3):
    """PCoA of a distance matrix. Returns (coords n×k, var_explained % per axis, ids)."""
    res = _skbio_pcoa(dm, number_of_dimensions=k)
    var = res.proportion_explained.values[:k] * 100.0
    return res.samples.values[:, :k], var, list(res.samples.index)


def permanova_test(dm, metadata, column, permutations=999):
    """PERMANOVA: do groups differ in multivariate space? Uses scikit-bio for the
    pseudo-F and permutation p; R² is derived exactly from pseudo-F.
    Returns a dict shaped for scientific-data-viz stats.report()."""
    grouping = metadata.loc[list(dm.ids), column]
    r = _skbio_permanova(dm, grouping, permutations=permutations)
    F = float(r["test statistic"])
    N = int(r["sample size"])
    a = int(r["number of groups"])
    ratio = F * (a - 1) / (N - a)
    r2 = ratio / (1 + ratio)
    return {"test": "PERMANOVA", "stat": F, "stat_symbol": "pseudo-F",
            "R2": r2, "p": float(r["p-value"]), "permutations": permutations}
