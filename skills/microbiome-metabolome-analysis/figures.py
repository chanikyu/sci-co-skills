"""figures.py — metabolomics figures in the scientific-data-viz house style:
PCA (samples), volcano (univariate), PLS-DA scores + VIP, heatmap (top features)."""
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


def pca_figure(coords, ev, groups, out_stem, palette="okabe_ito"):
    J.set_style(palette=palette)
    groups = np.asarray([str(g) for g in groups])
    labs = list(dict.fromkeys(groups))
    cmap = {g: c for g, c in zip(labs, J.palette(len(labs)))}
    fig, axes = J.figure_grid(1, 1, width="1.5col", panel_h=3.4)
    ax = axes[0]
    for g in labs:
        m = groups == g
        ax.scatter(coords[m, 0], coords[m, 1], s=34, color=cmap[g], edgecolor="#333", lw=0.4, label=g)
    J.group_ellipses(ax, coords[:, :2], groups, colors=cmap, n_std=2.0, alpha=0.3)
    ax.set_xlabel(J.var_label("PC1", ev[0])); ax.set_ylabel(J.var_label("PC2", ev[1]))
    ax.set_title("Metabolome PCA"); ax.legend(frameon=False, fontsize=7, loc="best")
    J.finalize(ax)
    png, _ = J.save(fig, out_stem); plt.close(fig)
    return png


def volcano_figure(res, out_stem, padj_thr=0.05, lfc_thr=1.0, palette="okabe_ito"):
    J.set_style(palette=palette)
    col = J.palette(2)
    r = res.dropna(subset=["padj", "log2FC"]).copy()
    x = r["log2FC"].values
    y = -np.log10(np.clip(r["padj"].values, 1e-300, 1))
    up = (r["padj"] < padj_thr) & (r["log2FC"] >= lfc_thr)
    dn = (r["padj"] < padj_thr) & (r["log2FC"] <= -lfc_thr)
    ns = ~(up | dn)
    fig, axes = J.figure_grid(1, 1, width="1.5col", panel_h=3.4)
    ax = axes[0]
    ax.scatter(x[ns], y[ns], s=9, color="#c9c9c9", edgecolor="none", label="n.s.")
    ax.scatter(x[up], y[up], s=11, color=col[1], edgecolor="none", label="up")
    ax.scatter(x[dn], y[dn], s=11, color=col[0], edgecolor="none", label="down")
    ax.axhline(-np.log10(padj_thr), ls="--", color="#888", lw=0.7)
    ax.axvline(lfc_thr, ls="--", color="#ccc", lw=0.6); ax.axvline(-lfc_thr, ls="--", color="#ccc", lw=0.6)
    ax.set_xlabel("log2 fold-change"); ax.set_ylabel("-log10 FDR")
    ax.set_title("Univariate (metabolites)"); ax.legend(frameon=False, fontsize=7, loc="upper right")
    J.finalize(ax)
    png, _ = J.save(fig, out_stem); plt.close(fig)
    return png


def plsda_figure(scores, groups, vip, out_stem, perm_p=None, top=15, palette="okabe_ito"):
    J.set_style(palette=palette)
    groups = np.asarray([str(g) for g in groups])
    labs = list(dict.fromkeys(groups))
    cmap = {g: c for g, c in zip(labs, J.palette(len(labs)))}
    fig, axes = J.figure_grid(1, 2, width="2col", panel_h=3.2)
    axA, axB = axes
    for g in labs:
        m = groups == g
        axA.scatter(scores[m, 0], scores[m, 1], s=34, color=cmap[g], edgecolor="#333", lw=0.4, label=g)
    J.group_ellipses(axA, scores[:, :2], groups, colors=cmap, n_std=2.0, alpha=0.3)
    axA.set_xlabel("PLS-DA component 1"); axA.set_ylabel("PLS-DA component 2")
    axA.set_title("PLS-DA scores"); axA.legend(frameon=False, fontsize=7, loc="best")
    if perm_p is not None:
        J.stats_text(axA, f"permutation P = {perm_p:.3f}")
    J.finalize(axA); J.panel_letter(axA, "A")

    v = vip.sort_values(ascending=True).tail(top)
    axB.barh(range(len(v)), v.values, color=J.palette(3)[2], edgecolor="#333", lw=0.4)
    axB.axvline(1.0, ls="--", color="#888", lw=0.8)
    axB.set_yticks(range(len(v))); axB.set_yticklabels(v.index, fontsize=5.5)
    axB.set_xlabel("VIP score"); axB.set_title(f"Top {len(v)} by VIP (>1)")
    J.finalize(axB); J.panel_letter(axB, "B")
    png, _ = J.save(fig, out_stem); plt.close(fig)
    return png


def heatmap_figure(mat, res, groups, out_stem, top=30, palette="okabe_ito"):
    J.set_style(palette=palette)
    sig = [f for f in res.sort_values("padj").head(top).index if f in mat.columns]
    z = mat[sig].copy()
    z = (z - z.mean(axis=0)) / z.std(axis=0).replace(0, 1)
    order = pd.Series([str(g) for g in groups], index=mat.index).sort_values().index
    z = z.loc[order]
    fig, axes = J.figure_grid(1, 1, width="1.5col", panel_h=4.4)
    ax = axes[0]
    im = ax.imshow(z.T.values, aspect="auto", cmap="RdBu_r", vmin=-2, vmax=2)
    ax.set_xticks(range(len(order))); ax.set_xticklabels(order, rotation=90, fontsize=4.5)
    ax.set_yticks(range(len(sig))); ax.set_yticklabels(sig, fontsize=4.5)
    ax.set_title(f"Top {len(sig)} metabolites (z-score)")
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="z")
    png, _ = J.save(fig, out_stem); plt.close(fig)
    return png
