"""abundance.py — assemble a vOTU × samples abundance table from per-sample CoverM output, applying a
coverage-breadth cutoff (a vOTU is present in a sample only if >= breadth_min of its length is covered,
which prevents a single stray read from calling a whole virus present). Pure Python — testable."""
import pandas as pd


def build_table(coverm, breadth_min=0.75, value="rpkm"):
    """coverm: {sample: DataFrame indexed by vOTU with a `value` column and a 'covered_fraction' column
    (0-1)}. Entries below the breadth cutoff are zeroed. Returns a samples × vOTU DataFrame (all-absent
    vOTUs dropped)."""
    cols = {}
    for sample, df in coverm.items():
        if value not in df.columns or "covered_fraction" not in df.columns:
            raise ValueError(f"sample {sample!r}: CoverM output missing '{value}' or 'covered_fraction'")
        v = df[value].astype(float).copy()
        v[df["covered_fraction"].astype(float) < breadth_min] = 0.0
        cols[sample] = v
    tab = pd.DataFrame(cols).fillna(0.0).T                      # samples × vOTU
    tab = tab.loc[:, tab.sum(axis=0) > 0]
    if tab.shape[1] == 0:
        raise ValueError(f"No vOTU passed the coverage-breadth cutoff ({breadth_min}) in any sample — "
                         f"lower breadth_min or check the CoverM inputs.")
    return tab


def present_summary(tab):
    """vOTUs detected per sample (after the breadth cutoff) — an honest presence count."""
    return (tab > 0).sum(axis=1).rename("n_vOTUs_detected").to_frame()
