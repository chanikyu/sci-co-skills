"""
pipeline.py — enter-at-any-stage orchestrator with logging and validation.

Detects which stage the input belongs to (stages.detect_stage) and runs everything
downstream, logging each step to <out>/logs/pipeline.log and validating outputs.
Give raw FASTQ, a feature table, a distance matrix, or an alpha table.
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
import stage0
import diversity as D
import figures as F
import preprocess as P
import analyze


def _log(logf, msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(logf, "a") as fh:
        fh.write(line + "\n")


def run(input_path, metadata, group_col, out_dir, from_stage=None,
        da_method="clr_test", metric="braycurtis", min_prevalence=0.1,
        do_rarefy=False, palette="okabe_ito",
        marker="16S", fwd_primer=None, rev_primer=None,
        trunc_f=0, trunc_r=0, maxee_f=2.0, maxee_r=2.0, tax_db=None, threads=1):
    """Run the pipeline from whatever stage `input_path` represents."""
    img, scr = J.prepare_output(out_dir)
    tables = os.path.join(out_dir, "tables")
    logs = os.path.join(out_dir, "logs")
    os.makedirs(tables, exist_ok=True)
    os.makedirs(logs, exist_ok=True)
    logf = os.path.join(logs, "pipeline.log")

    stage = from_stage or stages.detect_stage(input_path)["stage"]
    det = stages.detect_stage(input_path) if not from_stage else {"detail": f"forced --from {from_stage}"}
    _log(logf, f"input: {input_path}")
    _log(logf, f"stage: {stage}  ({det.get('detail', '')})")
    _log(logf, f"downstream: {' -> '.join(stages.DOWNSTREAM.get(stage, []))}")
    result = {"stage": stage, "out_dir": out_dir}

    if stage == "fastq":
        _log(logf, f"Stage 0: FASTQ -> ASV feature table via DADA2 (marker={marker}"
                   f"{', taxonomy DB given' if tax_db else ', no taxonomy'})")
        ft = stage0.run(input_path, os.path.join(out_dir, "stage0"), marker=marker,
                        fwd_primer=fwd_primer, rev_primer=rev_primer,
                        trunc_f=trunc_f, trunc_r=trunc_r, maxee_f=maxee_f, maxee_r=maxee_r,
                        tax_db=tax_db, threads=threads, logf=os.path.join(logs, "stage0.log"))
        _log(logf, f"  Stage 0 -> {ft}; continuing downstream")
        return run(ft, metadata, group_col, out_dir, from_stage="feature_table",
                   da_method=da_method, metric=metric, min_prevalence=min_prevalence,
                   do_rarefy=do_rarefy, palette=palette)

    meta = P.load_metadata(metadata) if metadata else None

    if stage == "feature_table":
        _log(logf, f"core pipeline: preprocess -> alpha -> beta ({metric}) -> {da_method}")
        res = analyze.run(input_path, metadata, group_col, out_dir, da_method=da_method,
                          metric=metric, min_prevalence=min_prevalence,
                          do_rarefy=do_rarefy, palette=palette)
        result.update(res)
        _log(logf, f"  differential: {res['n_significant']} significant taxa")
        _log(logf, f"  beta: PERMANOVA pseudo-F={res['permanova']['stat']:.2f}, "
                   f"R2={res['permanova']['R2']:.2f}, p={res['permanova']['p']:.3f}")

    elif stage == "distance_matrix":
        import numpy as np
        from skbio.stats.distance import DistanceMatrix
        dmdf = pd.read_csv(input_path, index_col=0)
        dm = DistanceMatrix(np.ascontiguousarray(dmdf.values, dtype=float),
                            ids=[str(i) for i in dmdf.index])
        coords, var, ids = D.ordinate(dm)
        perm = D.permanova_test(dm, meta, group_col)
        pd.DataFrame(coords[:, :2], index=ids, columns=["PCoA1", "PCoA2"]).assign(
            **{group_col: meta.loc[ids, group_col].values}).to_csv(os.path.join(tables, "beta_pcoa.csv"))
        F.beta_figure(coords, var, meta.loc[ids, group_col].values, perm,
                      os.path.join(img, "beta_pcoa"), palette=palette)
        result["permanova"] = perm
        _log(logf, f"  beta: PERMANOVA pseudo-F={perm['stat']:.2f}, R2={perm['R2']:.2f}, "
                   f"p={perm['p']:.3f}; PCoA1={var[0]:.1f}%, PCoA2={var[1]:.1f}%")

    elif stage == "alpha_table":
        adf = pd.read_csv(input_path, index_col=0)
        if group_col in adf.columns:
            groups = adf[group_col]
            metrics = [c for c in adf.columns if c != group_col]
        else:
            groups = meta.loc[adf.index, group_col]
            metrics = list(adf.select_dtypes("number").columns)
        F.alpha_figure(adf[metrics], groups, os.path.join(img, "alpha_diversity"), palette=palette)
        result["metrics"] = metrics
        _log(logf, f"  alpha: metrics {metrics}; groups {list(pd.unique(groups))}")

    # validate: figures produced?
    pngs = [f for f in os.listdir(img) if f.endswith(".png")]
    ok = len(pngs) > 0
    _log(logf, f"validation: {'PASS' if ok else 'FAIL'} — {len(pngs)} figure(s), "
               f"{len([f for f in os.listdir(tables) if f.endswith('.csv')])} table(s)")
    result["ok"] = ok
    result["log"] = logf
    return result
