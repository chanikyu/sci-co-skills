"""normalize.py — resistome normalization. RPKM (gene-length + sequencing-depth) and optional
per-marker (single-copy gene / 16S rRNA) normalization to "ARGs per cell". Pure Python — testable.
Raw ARG read counts are NOT comparable across samples; always normalize before beta/differential.

Note: `total_reads` must be the sample's TRUE library size (total QC'd/mapped reads), not a sum of the
ARG table. `per_marker` divides by a per-sample constant, so it changes Bray-Curtis + the drug-class
summary but NOT CLR-based differential abundance (CLR is invariant to a per-sample multiplier).
"""
import numpy as np
import pandas as pd


def rpkm(counts, gene_lengths, total_reads):
    """counts: ARG × samples read counts. gene_lengths: {ARG: bp}. total_reads: {sample: library size}.
    RPKM = reads / gene_kb / (total_reads / 1e6). Raises on any ARG/sample missing its metadata."""
    miss_g = set(counts.index) - set(gene_lengths)
    if miss_g:
        raise ValueError(f"{len(miss_g)} ARG(s) missing from gene_lengths (e.g. {sorted(miss_g)[:3]}) "
                         f"— gene IDs must match.")
    miss_s = set(counts.columns) - set(total_reads)
    if miss_s:
        raise ValueError(f"{len(miss_s)} sample(s) missing from total_reads (e.g. {sorted(miss_s)[:3]}).")
    kb = (pd.Series(gene_lengths, dtype=float).reindex(counts.index) / 1000.0).replace(0, np.nan)
    per_kb = counts.div(kb, axis=0)
    depth = pd.Series(total_reads, dtype=float).reindex(counts.columns) / 1e6
    return per_kb.div(depth, axis=1)


def per_marker(rpkm_df, marker_rpkm):
    """Divide each sample's ARG RPKM by that sample's single-copy-gene (or 16S) RPKM → "ARGs per cell".
    marker_rpkm: {sample: marker RPKM} — user-provided (the pipeline does not quantify markers itself).
    Prefer a single-copy-gene panel (rpoB / recA / universal SCGs): 16S copy number varies 1–15× per genome."""
    miss = set(rpkm_df.columns) - set(marker_rpkm)
    if miss:
        raise ValueError(f"{len(miss)} sample(s) missing from marker_rpkm (e.g. {sorted(miss)[:3]}).")
    m = pd.Series(marker_rpkm, dtype=float).reindex(rpkm_df.columns).replace(0, np.nan)
    return rpkm_df.div(m, axis=1)


def normalize(counts, gene_lengths, total_reads, marker_rpkm=None):
    """RPKM, then per-marker if marker RPKM is supplied. Returns (normalized_table, method_label)."""
    out = rpkm(counts, gene_lengths, total_reads)
    if marker_rpkm is not None:
        return per_marker(out, marker_rpkm), "RPKM / marker (per-cell)"
    return out, "RPKM"
