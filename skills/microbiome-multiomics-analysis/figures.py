"""figures.py — multi-omics integration figures (scientific-data-viz house style):
PERMANOVA-per-omic bars, cross-omic correlation heatmap, Procrustes overlay."""
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


def permanova_figure(perm, out_stem, palette="okabe_ito"):
    """perm: {omic: {R2, p, ...}}."""
    J.set_style(palette=palette)
    omics = list(perm.keys())
    r2 = [perm[o]["R2"] for o in omics]
    col = J.palette(len(omics))
    fig, axes = J.figure_grid(1, 1, width="1col", panel_h=3.0)
    ax = axes[0]
    ax.bar(range(len(omics)), r2, color=col, edgecolor="#333", lw=0.5)
    for i, o in enumerate(omics):
        star = "*" if perm[o]["p"] < 0.05 else "n.s."
        ax.text(i, r2[i] + 0.01, f"P={perm[o]['p']:.3f}\n{star}", ha="center", va="bottom", fontsize=6)
    ax.set_xticks(range(len(omics))); ax.set_xticklabels(omics, rotation=20, ha="right", fontsize=7)
    finite = [x for x in r2 if not np.isnan(x)]
    ax.set_ylabel("PERMANOVA R² (condition)"); ax.set_ylim(0, (max(finite) if finite else 1.0) * 1.25 + 0.05)
    ax.set_title("Condition footprint per omic")
    J.finalize(ax)
    png, _ = J.save(fig, out_stem); plt.close(fig)
    return png


def correlation_heatmap(full_df, sig, out_stem, name_a, name_b, top=20, palette="okabe_ito"):
    """Heatmap of Spearman rho for the features that appear in the strongest significant cross-omic pairs."""
    J.set_style(palette=palette)
    src = sig if len(sig) else full_df.reindex(full_df["rho"].abs().sort_values(ascending=False).index)
    fa = list(dict.fromkeys(src["feature_A"]))[:top]
    fb = list(dict.fromkeys(src["feature_B"]))[:top]
    mat = full_df.pivot(index="feature_A", columns="feature_B", values="rho").reindex(index=fa, columns=fb)
    fig, axes = J.figure_grid(1, 1, width="1.5col", panel_h=4.2)
    ax = axes[0]
    im = ax.imshow(mat.values, aspect="auto", cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(fb))); ax.set_xticklabels(fb, rotation=90, fontsize=4.5)
    ax.set_yticks(range(len(fa))); ax.set_yticklabels(fa, fontsize=4.5)
    ax.set_xlabel(name_b); ax.set_ylabel(name_a)
    ax.set_title(f"Cross-omic Spearman ρ\n{name_a} × {name_b} ({len(sig)} sig, BH-FDR)")
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02, label="ρ")
    png, _ = J.save(fig, out_stem); plt.close(fig)
    return png


def procrustes_figure(mtx1, mtx2, groups, out_stem, name_a, name_b,
                      disparity, mantel_r, mantel_p, palette="okabe_ito"):
    """Superimposed PCoA ordinations of two omics; a line connects each sample's two positions."""
    J.set_style(palette=palette)
    groups = np.asarray([str(g) for g in groups])
    labs = list(dict.fromkeys(groups))
    cmap = {g: c for g, c in zip(labs, J.palette(len(labs)))}
    fig, axes = J.figure_grid(1, 1, width="1.5col", panel_h=3.6)
    ax = axes[0]
    for a, b in zip(mtx1, mtx2):
        ax.plot([a[0], b[0]], [a[1], b[1]], color="#bbb", lw=0.5, zorder=1)
    for g in labs:
        m = groups == g
        ax.scatter(mtx1[m, 0], mtx1[m, 1], s=30, color=cmap[g], edgecolor="#333", lw=0.4,
                   marker="o", label=f"{g} · {name_a}", zorder=3)
        ax.scatter(mtx2[m, 0], mtx2[m, 1], s=30, color=cmap[g], edgecolor="#333", lw=0.4,
                   marker="^", zorder=3)
    ax.set_xlabel("Procrustes axis 1"); ax.set_ylabel("Procrustes axis 2")
    ax.set_title(f"Concordance: {name_a} (●) vs {name_b} (▲)")
    J.stats_text(ax, f"Procrustes m² = {disparity:.2f}\nMantel r = {mantel_r:.2f}, P = {mantel_p:.3f}")
    ax.legend(frameon=False, fontsize=6, loc="best")
    J.finalize(ax)
    png, _ = J.save(fig, out_stem); plt.close(fig)
    return png
