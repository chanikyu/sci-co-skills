"""figures.py — bulk RNA-seq figures in the scientific-data-viz house style:
PCA (samples), volcano (DE genes), heatmap (top DE genes)."""
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


def pca_figure(norm, metadata, condition, out_stem, n_top=500, palette="okabe_ito"):
    from sklearn.decomposition import PCA
    logn = np.log2(norm + 1.0)
    v = logn.var(axis=1).sort_values(ascending=False)
    X = logn.loc[v.index[:n_top]].T.values                 # samples × genes
    p = PCA(n_components=2).fit(X)
    coords = p.transform(X)
    ev = p.explained_variance_ratio_ * 100
    groups = metadata.loc[norm.columns, condition].astype(str).values

    J.set_style(palette=palette)
    labs = list(dict.fromkeys(groups))
    cmap = {g: c for g, c in zip(labs, J.palette(len(labs)))}
    fig, axes = J.figure_grid(1, 1, width="1.5col", panel_h=3.4)
    ax = axes[0]
    for g in labs:
        m = groups == g
        ax.scatter(coords[m, 0], coords[m, 1], s=34, color=cmap[g], edgecolor="#333", lw=0.4, label=g)
    J.group_ellipses(ax, coords[:, :2], groups, colors=cmap, n_std=2.0, alpha=0.3)
    ax.set_xlabel(J.var_label("PC1", ev[0])); ax.set_ylabel(J.var_label("PC2", ev[1]))
    ax.set_title("Sample PCA (top variable genes)")
    ax.legend(frameon=False, fontsize=7, loc="best")
    J.finalize(ax)
    png, pdf = J.save(fig, out_stem); plt.close(fig)
    return png, pdf


def volcano_figure(res, out_stem, padj_thr=0.05, lfc_thr=1.0, palette="okabe_ito"):
    J.set_style(palette=palette)
    col = J.palette(2)
    r = res.dropna(subset=["padj", "log2FoldChange"]).copy()
    x = r["log2FoldChange"].values
    y = -np.log10(np.clip(r["padj"].values, 1e-300, 1))
    up = (r["padj"] < padj_thr) & (r["log2FoldChange"] >= lfc_thr)
    dn = (r["padj"] < padj_thr) & (r["log2FoldChange"] <= -lfc_thr)
    ns = ~(up | dn)
    fig, axes = J.figure_grid(1, 1, width="1.5col", panel_h=3.4)
    ax = axes[0]
    ax.scatter(x[ns], y[ns], s=8, color="#c9c9c9", edgecolor="none", label="n.s.")
    ax.scatter(x[up], y[up], s=10, color=col[1], edgecolor="none", label="up")
    ax.scatter(x[dn], y[dn], s=10, color=col[0], edgecolor="none", label="down")
    ax.axhline(-np.log10(padj_thr), ls="--", color="#888", lw=0.7)
    ax.axvline(lfc_thr, ls="--", color="#ccc", lw=0.6); ax.axvline(-lfc_thr, ls="--", color="#ccc", lw=0.6)
    ax.set_xlabel("log2 fold-change"); ax.set_ylabel("−log10 FDR")
    ax.set_title("Differential expression"); ax.legend(frameon=False, fontsize=7, loc="upper right")
    J.finalize(ax)
    png, pdf = J.save(fig, out_stem); plt.close(fig)
    return png, pdf


def heatmap_figure(norm, res, metadata, condition, out_stem, top=30, palette="okabe_ito"):
    J.set_style(palette=palette)
    sig = res.dropna(subset=["padj"]).sort_values("padj").head(top).index
    sig = [g for g in sig if g in norm.index]
    logn = np.log2(norm.loc[sig] + 1.0)
    z = logn.sub(logn.mean(axis=1), axis=0).div(logn.std(axis=1).replace(0, 1), axis=0)
    order = metadata.loc[norm.columns, condition].astype(str).sort_values().index
    z = z[order]
    fig, axes = J.figure_grid(1, 1, width="1.5col", panel_h=4.2)
    ax = axes[0]
    im = ax.imshow(z.values, aspect="auto", cmap="RdBu_r", vmin=-2, vmax=2)
    ax.set_xticks(range(len(order))); ax.set_xticklabels(order, rotation=90, fontsize=5)
    ax.set_yticks(range(len(sig))); ax.set_yticklabels(sig, fontsize=5)
    ax.set_title(f"Top {len(sig)} DE genes (z-score)")
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="z")
    png, pdf = J.save(fig, out_stem); plt.close(fig)
    return png, pdf
