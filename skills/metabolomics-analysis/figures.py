"""figures.py — metabolomics upstream QC / annotation figures (scientific-data-viz house style)."""
import os
import sys
import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_SDV = os.path.join(_HERE, "..", "scientific-data-viz")
if _SDV not in sys.path:
    sys.path.insert(0, _SDV)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import journal_style as J


def qc_rsd_figure(rsd, max_rsd, out_stem, palette="okabe_ito"):
    """Distribution of pooled-QC RSD across features + the pass/fail threshold."""
    J.set_style(palette=palette)
    r = np.asarray(pd.Series(rsd).dropna(), dtype=float) * 100.0
    r = r[np.isfinite(r)]
    if r.size < 2:
        return None                                   # nothing meaningful to plot
    col = J.palette(2)
    fig, axes = J.figure_grid(1, 1, width="1col", panel_h=3.0)
    ax = axes[0]
    bins = min(30, max(5, len(np.unique(np.round(r, 2)))))
    ax.hist(np.clip(r, 0, 100), bins=bins, color=col[0], edgecolor="#333", lw=0.4)
    ax.axvline(max_rsd * 100, ls="--", color=col[1], lw=1.2, label=f"cutoff {int(max_rsd*100)}%")
    kept = int((r <= max_rsd * 100).sum())
    ax.set_xlabel("pooled-QC RSD (%)"); ax.set_ylabel("features")
    ax.set_title(f"QC reproducibility ({kept}/{len(r)} features kept)")
    ax.legend(frameon=False, fontsize=7)
    J.finalize(ax)
    png, _ = J.save(fig, out_stem); plt.close(fig)
    return png


def msi_figure(summary, out_stem, palette="okabe_ito"):
    """Feature count per MSI/Schymanski confidence level (1 confirmed … 4 unknown)."""
    J.set_style(palette=palette)
    names = {1: "1 (confirmed)", 2: "2 (probable)", 3: "3 (putative)", 4: "4 (unknown)"}
    levels = [1, 2, 3, 4]
    counts = [int(summary["n_features"].get(l, 0)) for l in levels]
    cols = J.palette(4)
    fig, axes = J.figure_grid(1, 1, width="1col", panel_h=3.0)
    ax = axes[0]
    ax.bar(range(4), counts, color=cols, edgecolor="#333", lw=0.5)
    ax.set_xticks(range(4)); ax.set_xticklabels([names[l] for l in levels], rotation=20, ha="right", fontsize=6.5)
    ax.set_ylabel("features"); ax.set_title("Annotation confidence (MSI level)")
    for i, c in enumerate(counts):
        ax.text(i, c, str(c), ha="center", va="bottom", fontsize=7)
    J.finalize(ax)
    png, _ = J.save(fig, out_stem); plt.close(fig)
    return png
