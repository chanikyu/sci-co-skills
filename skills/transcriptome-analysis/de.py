"""de.py — differential expression via pydeseq2 (DESeq2 negative-binomial model, pure Python).
Input: raw integer gene counts (genes × samples) + metadata (sample × covariates) with a condition."""
import numpy as np
import pandas as pd


def run_de(counts, metadata, condition, ref_level=None, min_count=10):
    """Return (results_df, normalized_counts genes×samples, (test_level, ref_level)).
    Low-count genes (row sum < min_count) are filtered and reported by the caller."""
    from pydeseq2.dds import DeseqDataSet
    from pydeseq2.ds import DeseqStats

    samples = [s for s in counts.columns if s in metadata.index]
    counts = counts[samples]
    meta = metadata.loc[samples].copy()

    keep = counts.sum(axis=1) >= min_count
    counts = counts.loc[keep]

    levels = list(pd.unique(meta[condition].astype(str)))
    meta[condition] = meta[condition].astype(str)
    if ref_level is None:
        ref_level = levels[0]
    test_level = [l for l in levels if l != ref_level][0]

    cT = counts.T.astype(int)                      # pydeseq2: samples × genes
    try:
        dds = DeseqDataSet(counts=cT, metadata=meta, design_factors=condition,
                           ref_level=[condition, ref_level], quiet=True)
    except TypeError:                              # older/newer signature
        dds = DeseqDataSet(counts=cT, metadata=meta, design_factors=condition)
    dds.deseq2()
    st = DeseqStats(dds, contrast=[condition, test_level, ref_level], quiet=True)
    st.summary()
    res = st.results_df.sort_values("padj")

    try:
        normed = dds.layers["normed_counts"]
    except Exception:
        normed = dds.layers["normed"]
    norm = pd.DataFrame(np.asarray(normed).T, index=counts.index, columns=samples)
    return res, norm, (test_level, ref_level)


def n_significant(res, padj=0.05, lfc=1.0):
    r = res.dropna(subset=["padj"])
    return int(((r["padj"] < padj) & (r["log2FoldChange"].abs() >= lfc)).sum())
