"""pipeline.py — metabolomics enter-at-any-stage orchestrator with logging and validation.

Feature table -> clean -> normalize -> transform+scale -> univariate(+FDR) -> PCA -> PLS-DA(+VIP,
permutation) -> heatmap. A results table -> volcano. Figures reuse scientific-data-viz.
"""
import os
import sys
import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_SDV = os.path.join(_HERE, "..", "scientific-data-viz")
for p in (_HERE, _SDV):
    if p not in sys.path:
        sys.path.insert(0, p)

import pandas as pd
import journal_style as J
import stages
import preprocess as P
import stats_uni as U
import multivariate as M
import figures as F


def _log(logf, msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(logf, "a") as fh:
        fh.write(line + "\n")


def run(input_path, metadata, group_col, out_dir, from_stage=None, impute="halfmin",
        norm="pqn", scale="pareto", min_prevalence=0.1, padj_thr=0.05, lfc_thr=1.0,
        n_perm=200, reference=None, palette="okabe_ito"):
    img, scr = J.prepare_output(out_dir)
    tables = os.path.join(out_dir, "tables"); logs = os.path.join(out_dir, "logs")
    os.makedirs(tables, exist_ok=True); os.makedirs(logs, exist_ok=True)
    logf = os.path.join(logs, "pipeline.log")

    det = stages.detect_stage(input_path)
    stage = from_stage or det["stage"]
    _log(logf, f"input: {input_path}")
    _log(logf, f"stage: {stage} ({det.get('detail','')})")
    result = {"stage": stage, "out_dir": out_dir}

    if stage == "results_table":
        res = pd.read_csv(input_path, index_col=0)
        if "log2FC" in res.columns:
            F.volcano_figure(res, os.path.join(img, "volcano"), padj_thr, lfc_thr, palette=palette)
        result["ok"] = True; result["log"] = logf
        return result

    df = pd.read_csv(input_path, index_col=0)
    meta = pd.read_csv(metadata, index_col=0)
    common = [s for s in df.index if s in meta.index]
    if len(common) < 3:
        raise ValueError(f"Only {len(common)} sample IDs overlap between the feature table "
                         f"({df.shape[0]}) and metadata ({meta.shape[0]}) — check that sample_id "
                         f"values match (whitespace / case / prefix).")
    df = df.loc[common]
    groups = meta.loc[common, group_col].astype(str)
    levels = sorted(pd.unique(groups).tolist())                 # deterministic; ref = levels[0]
    if reference in levels:
        levels = [reference] + [lv for lv in levels if lv != reference]
    _log(logf, f"{df.shape[0]} samples × {df.shape[1]} metabolites | groups {levels} "
               f"(reference = {levels[0]})")

    # preprocessing (group-blind): filter on RAW (prevalence) -> impute -> normalize -> transform -> scale
    filt = P.filter_features(df, min_prevalence=min_prevalence)
    imp, dropped = P.impute_missing(filt, method=impute)
    if imp.shape[1] == 0:
        raise ValueError("No metabolite features remain after prevalence filter + missing drop; "
                         "loosen min_prevalence.")
    normed = P.normalize_samples(imp, method=norm)              # non-log (for fold change)
    trans = P.transform(normed, "log10")                       # log (adaptive pseudocount) — for stats
    scaled = P.scale_features(trans, method=scale)             # for descriptive PCA / PLS-DA
    _log(logf, f"clean: {filt.shape[1]} features after prevalence filter, {imp.shape[1]} kept "
               f"(dropped {dropped} high-missing); impute={impute}, norm={norm}, scale={scale}")

    # univariate + fold change
    uni = U.run_univariate(trans, groups)
    if len(levels) == 2:
        uni["log2FC"] = U.fold_change(normed, groups, levels[1], levels[0])
    uni.sort_values("padj").to_csv(os.path.join(tables, "univariate_results.csv"))
    nsig = U.n_significant(uni, padj_thr, lfc_thr if len(levels) == 2 else None)
    _log(logf, f"univariate: {nsig} significant (BH-FDR<{padj_thr}"
               f"{', |log2FC|>=%s' % lfc_thr if len(levels)==2 else ''})")

    # multivariate
    coords, ev = M.pca_scores(scaled)
    F.pca_figure(coords, ev, groups.values, os.path.join(img, "pca"), palette=palette)
    _, plsda_scores, vip, _ = M.plsda(scaled, groups.values)
    vip.sort_values(ascending=False).to_csv(os.path.join(tables, "plsda_vip.csv"))
    obs, perm, pperm = M.permutation_test(trans, groups.values, n_perm=n_perm)
    _log(logf, f"PLS-DA: CV accuracy={obs:.3f}, permutation P={pperm:.3f} (n_perm={n_perm})")
    F.plsda_figure(plsda_scores, groups.values, vip, os.path.join(img, "plsda"),
                   perm_p=pperm, palette=palette)
    if len(levels) == 2:
        F.volcano_figure(uni, os.path.join(img, "volcano"), padj_thr, lfc_thr, palette=palette)
    F.heatmap_figure(trans, uni, groups.values, os.path.join(img, "heatmap"), palette=palette)

    pngs = [f for f in os.listdir(img) if f.endswith(".png")]
    ok = len(pngs) > 0
    _log(logf, f"validation: {'PASS' if ok else 'FAIL'} — {len(pngs)} figures, "
               f"{len([f for f in os.listdir(tables) if f.endswith('.csv')])} tables")
    result.update({"n_significant": nsig, "plsda_cv_accuracy": round(float(obs), 3),
                   "plsda_perm_p": round(float(pperm), 3), "ok": ok, "log": logf})
    return result
