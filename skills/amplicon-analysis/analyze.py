"""
analyze.py — orchestrate the amplicon pipeline end to end.

load+validate -> preprocess -> alpha -> beta -> differential abundance, writing a
structured folder: <base>/tables, <base>/images, <base>/script, and report.md.
Reuses scientific-data-viz for output layout and figure style.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SDV = os.path.join(_HERE, "..", "scientific-data-viz")
for p in (_HERE, _SDV):
    if p not in sys.path:
        sys.path.insert(0, p)

import pandas as pd
import journal_style as J
import preprocess as P
import diversity as D
import differential as DA
import figures as F

_EFFECT_COL = {"clr_test": "effect_clr", "kruskal_lfc": "log2fc", "pydeseq2": "log2fc"}


def run(feature_table, metadata, group_col, out_dir, da_method="clr_test",
        metric="braycurtis", min_prevalence=0.1, do_rarefy=False, rarefy_depth=None,
        palette="okabe_ito"):
    """Run the full pipeline. Returns a dict of result paths + key stats."""
    img, scr = J.prepare_output(out_dir)
    tables = os.path.join(out_dir, "tables")
    os.makedirs(tables, exist_ok=True)

    table = P.load_table(feature_table)
    meta = P.load_metadata(metadata)
    dtype = P.detect_type(table)
    table, meta, jreport = P.join(table, meta)
    table, removed = P.filter_features(table, min_prevalence=min_prevalence)

    is_counts = dtype == "counts"
    work, rare_note = table, "none"
    if is_counts and do_rarefy:
        work, depth, dropped = P.rarefy(table, rarefy_depth)
        meta = meta.loc[work.index]
        rare_note = f"rarefied to {depth} reads/sample ({len(dropped)} samples dropped)"

    rel = P.to_relative(work)
    clr_df = P.clr(work)
    groups = meta[group_col]

    # alpha
    adf = D.alpha_table(work, counts=is_counts)
    adf.insert(0, group_col, groups.values)
    adf.to_csv(os.path.join(tables, "alpha_diversity.csv"))
    metrics = [c for c in adf.columns if c != group_col]
    F.alpha_figure(adf[metrics], groups, os.path.join(img, "alpha_diversity"), palette=palette)

    # beta
    dm = D.beta_distance(rel, metric=metric)
    coords, var, ids = D.ordinate(dm)
    perm = D.permanova_test(dm, meta, group_col)
    pd.DataFrame(dm.data, index=dm.ids, columns=dm.ids).to_csv(
        os.path.join(tables, f"beta_distance_{metric}.csv"))
    pd.DataFrame(coords[:, :2], index=ids, columns=["PCoA1", "PCoA2"]).assign(
        **{group_col: groups.loc[ids].values}).to_csv(os.path.join(tables, "beta_pcoa.csv"))
    F.beta_figure(coords, var, groups.loc[ids].values, perm, os.path.join(img, "beta_pcoa"),
                  palette=palette)

    # differential abundance
    if da_method == "clr_test":
        da, label = DA.clr_test(clr_df, groups)
    elif da_method == "kruskal_lfc":
        da, label = DA.kruskal_lfc(rel, groups)
    elif da_method == "pydeseq2":
        if not is_counts:
            raise ValueError("pydeseq2 needs counts input; got relative abundance.")
        da, label = DA.pydeseq2(work, meta, group_col)
    else:
        raise ValueError(f"unknown da_method '{da_method}'")
    da.to_csv(os.path.join(tables, "differential_abundance.csv"), index=False)
    F.differential_figure(da, os.path.join(img, "differential_abundance"),
                          effect_col=_EFFECT_COL[da_method], palette=palette)

    _write_report(out_dir, dict(
        feature_table=feature_table, metadata=metadata, group_col=group_col, dtype=dtype,
        n_samples=len(work), n_features=work.shape[1], n_removed=len(removed),
        join=jreport, rarefaction=rare_note, metric=metric, da_method=label,
        n_sig=int(da["significant"].sum()), perm=perm, groups=list(pd.unique(groups)),
        alpha_metrics=metrics))
    _write_script(scr, dict(feature_table=feature_table, metadata=metadata, group_col=group_col,
                            out_dir=out_dir, da_method=da_method, metric=metric,
                            min_prevalence=min_prevalence, do_rarefy=do_rarefy,
                            rarefy_depth=rarefy_depth, palette=palette))
    return {"images": img, "tables": tables, "script": scr,
            "n_significant": int(da["significant"].sum()), "permanova": perm}


def _write_report(out_dir, r):
    lines = [
        "# Amplicon analysis report", "",
        f"- Input: `{os.path.basename(r['feature_table'])}` ({r['dtype']}) + "
        f"`{os.path.basename(r['metadata'])}`, grouped by **{r['group_col']}** "
        f"({', '.join(map(str, r['groups']))}).",
        f"- Samples analyzed: {r['n_samples']}; features kept: {r['n_features']} "
        f"({r['n_removed']} low-prevalence removed).",
        f"- Join: {r['join']['n_common']} matched; "
        f"only-in-table={r['join']['only_in_table']}; only-in-metadata={r['join']['only_in_metadata']}.",
        f"- Rarefaction: {r['rarefaction']}.", "",
        "## Alpha diversity",
        f"Metrics: {', '.join(r['alpha_metrics'])}. Per-group comparison test annotated on the figure "
        "(parametric vs non-parametric chosen by a Shapiro-Wilk normality test).", "",
        "## Beta diversity",
        f"Distance: {r['metric']}; ordination: PCoA. Group separation: "
        f"PERMANOVA pseudo-F = {r['perm']['stat']:.2f}, R2 = {r['perm']['R2']:.2f}, "
        f"P = {r['perm']['p']:.3f} ({r['perm']['permutations']} permutations).", "",
        "## Differential abundance",
        f"Method: {r['da_method']}. Significant features (adjusted P < 0.05): **{r['n_sig']}**. "
        "See `tables/differential_abundance.csv` and the volcano/bar figure.", "",
        "_Figures: images/ (PNG + editable PDF). Tables: tables/. Reproducible call: script/._",
    ]
    open(os.path.join(out_dir, "report.md"), "w").write("\n".join(lines))


def _write_script(scr, kw):
    args = ",\n    ".join(f"{k}={v!r}" for k, v in kw.items())
    code = ("import sys\n"
            f"sys.path.insert(0, {_HERE!r})\n"
            "import analyze\n\n"
            f"analyze.run(\n    {args},\n)\n")
    open(os.path.join(scr, "run_amplicon_analysis.py"), "w").write(code)
