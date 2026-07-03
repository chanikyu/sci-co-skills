"""
figures.py — standard amplicon figures in journal house style.

Reuses scientific-data-viz's journal_style (J) for the look and stats (S) for the
full-name test annotations. Alpha boxplots, beta PCoA, and a differential-abundance
volcano + top-taxa bar.
"""
import os
import sys
import numpy as np

_SDV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scientific-data-viz")
if _SDV not in sys.path:
    sys.path.insert(0, _SDV)
import matplotlib          # noqa: E402
matplotlib.use("Agg")      # headless-safe rendering
import journal_style as J   # noqa: E402
import stats as S           # noqa: E402


def alpha_figure(alpha_df, groups, out_stem, metrics=None, palette="okabe_ito"):
    """Box + individual points per group, one panel per alpha metric, with the
    computed group test annotated by full name."""
    import pandas as pd
    groups = pd.Series(list(groups), index=alpha_df.index)
    labs = list(pd.unique(groups))
    metrics = metrics or list(alpha_df.columns)
    J.set_style(palette=palette)
    fig, axes = J.figure_grid(1, len(metrics), width=min(3.2 * len(metrics), 12), panel_h=3.2)
    gcol = J.palette(len(labs))
    for ax, m in zip(axes, metrics):
        data = [alpha_df.loc[groups == g, m].dropna().values for g in labs]
        bp = ax.boxplot(data, positions=range(len(labs)), widths=0.55, patch_artist=True,
                        medianprops=dict(color="k", lw=1.3), flierprops=dict(marker=""))
        for patch, c in zip(bp["boxes"], gcol):
            patch.set_facecolor(c); patch.set_alpha(0.85); patch.set_edgecolor("k")
        for i, d in enumerate(data):
            ax.scatter(J.jitter(i, len(d), rng=np.random.default_rng(i)), d, s=12, color="k", zorder=3)
        ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs)
        ax.set_ylabel(m.replace("_", " "))
        allv = np.concatenate([d for d in data if len(d)]) if any(len(d) for d in data) else np.array([])
        ymax = float(np.nanmax(allv)) if allv.size else 1.0
        try:
            res = S.compare(data); p = res["p"]
        except Exception:
            res, p = None, float("nan")
        if res is not None and np.isfinite(p):
            if len(labs) == 2:
                J.sig_bracket(ax, 0, 1, ymax * 1.03, J.stars(p))
            J.stats_text(ax, S.report(res))
        else:
            J.stats_text(ax, "test n/a (no variation)")
        ax.set_title(m.replace("_", " "))
        J.finalize(ax)
    png, pdf = J.save(fig, out_stem)
    import matplotlib.pyplot as plt; plt.close(fig)
    return png, pdf


def beta_figure(coords, var, groups, permanova_res, out_stem, palette="okabe_ito"):
    """PCoA scatter colored by group; % variance axis labels; PERMANOVA annotation."""
    import pandas as pd, matplotlib.pyplot as plt
    groups = list(groups)
    labs = list(pd.unique(pd.Series(groups)))
    J.set_style(palette=palette)
    fig, axes = J.figure_grid(1, 1, width="1.5col", panel_h=3.6); ax = axes[0]
    gcol = dict(zip(labs, J.palette(len(labs))))
    g = np.array(groups)
    for lab in labs:
        m = g == lab
        ax.scatter(coords[m, 0], coords[m, 1], s=34, color=gcol[lab], edgecolor="k",
                   lw=0.4, label=lab, zorder=3)
    J.group_ellipses(ax, coords[:, :2], g, colors=gcol, n_std=2.0, alpha=0.3)
    ax.axhline(0, color="#dddddd", lw=0.8, zorder=0); ax.axvline(0, color="#dddddd", lw=0.8, zorder=0)
    ax.set_xlabel(J.var_label("PCoA1", var[0])); ax.set_ylabel(J.var_label("PCoA2", var[1]))
    ax.set_title("Beta diversity (PCoA)")
    J.stats_text(ax, S.report(permanova_res))
    J.legend_outside(ax, fontsize=9, title="Group")
    J.finalize(ax)
    png, pdf = J.save(fig, out_stem); plt.close(fig)
    return png, pdf


def differential_figure(da_df, out_stem, effect_col="effect_clr", top=15, palette="okabe_ito"):
    """Volcano (effect vs -log10 p_adj) + ranked bar of the top significant features."""
    import matplotlib.pyplot as plt
    J.set_style(palette=palette)
    fig, axes = J.figure_grid(1, 2, width=9.5, panel_h=3.6, wspace=0.6)
    axv, axb = axes
    eff = da_df[effect_col].values
    nlp = -np.log10(np.clip(da_df["p_adj"].values, 1e-300, 1))
    sig = da_df["significant"].values
    axv.scatter(eff[~sig], nlp[~sig], s=14, color="#b8b8b8", zorder=2)
    axv.scatter(eff[sig], nlp[sig], s=18, color=J.palette(2)[1], edgecolor="k", lw=0.3, zorder=3)
    axv.axhline(-np.log10(0.05), color="#999", ls="--", lw=0.8)
    axv.axvline(0, color="#999", ls="-", lw=0.6)
    axv.set_xlabel(effect_col.replace("_", " ")); axv.set_ylabel("-log10 adjusted P")
    axv.set_title("Differential abundance"); J.finalize(axv); J.panel_letter(axv, "A")

    sig_df = da_df[da_df["significant"]].head(top).iloc[::-1]
    if len(sig_df):
        y = range(len(sig_df))
        colors = [J.palette(2)[1] if e > 0 else J.palette(2)[0] for e in sig_df[effect_col]]
        axb.barh(list(y), sig_df[effect_col].values, color=colors, edgecolor="#3a3a3a", lw=0.5)
        axb.set_yticks(list(y)); axb.set_yticklabels(sig_df["feature"], fontsize=7)
        axb.axvline(0, color="#999", lw=0.8)
    axb.set_xlabel(effect_col.replace("_", " ")); axb.set_title(f"Top {top} significant")
    J.finalize(axb); J.panel_letter(axb, "B")
    png, pdf = J.save(fig, out_stem); plt.close(fig)
    return png, pdf
