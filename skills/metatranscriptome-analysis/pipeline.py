"""pipeline.py — metatranscriptome enter-at-any-stage orchestrator with logging and validation.

Raw RNA FASTQ -> QC -> host removal -> rRNA removal -> HUMAnN/MetaPhlAn -> abundance table.
Abundance table / distance matrix / alpha table -> the shared downstream, REUSED from the sibling
amplicon-analysis skill (analyze / diversity / figures). Mirrors shotgun-analysis/pipeline.py.
"""
import os
import sys
import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_AMP = os.path.join(_HERE, "..", "amplicon-analysis")
_SDV = os.path.join(_HERE, "..", "scientific-data-viz")
for p in (_HERE, _AMP, _SDV):
    if p not in sys.path:
        sys.path.insert(0, p)

import pandas as pd
import stages                    # metatx (this dir)
import runners                   # metatx front stages (this dir)
import journal_style as J        # scientific-data-viz
import analyze                   # amplicon-analysis core (unique names -> no clash)
import diversity as D
import figures as F
import preprocess as P


def _log(logf, msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(logf, "a") as fh:
        fh.write(line + "\n")


def run(input_path, metadata, condition, out_dir, from_stage=None, profiler="humann",
        da_method="clr_test", metric="braycurtis", min_prevalence=0.1, do_rarefy=False,
        palette="okabe_ito", host_index=None, rrna_db=None, metaphlan_db=None,
        humann_nuc_db=None, humann_prot_db=None, threads=4):
    img, scr = J.prepare_output(out_dir)
    tables = os.path.join(out_dir, "tables"); logs = os.path.join(out_dir, "logs")
    os.makedirs(tables, exist_ok=True); os.makedirs(logs, exist_ok=True)
    logf = os.path.join(logs, "pipeline.log")

    stage = from_stage or stages.detect_stage(input_path)["stage"]
    det = stages.detect_stage(input_path) if not from_stage else {"detail": f"forced --from {from_stage}"}
    _log(logf, f"input: {input_path}")
    _log(logf, f"stage: {stage}  ({det.get('detail', '')})")
    result = {"stage": stage, "out_dir": out_dir}

    if stage == "fastq":
        _log(logf, f"front: fastp QC{' + host removal' if host_index else ''} + rRNA removal "
                   f"(SortMeRNA) -> {profiler}")
        ab = runners.run(input_path, os.path.join(out_dir, "frontstages"), profiler=profiler,
                         host_index=host_index, rrna_db=rrna_db, metaphlan_db=metaphlan_db,
                         humann_nuc_db=humann_nuc_db, humann_prot_db=humann_prot_db, threads=threads,
                         logf=os.path.join(logs, "frontstages.log"))
        _log(logf, f"  front -> {ab}; continuing downstream")
        return run(ab, metadata, condition, out_dir, from_stage="feature_table", profiler=profiler,
                   da_method=da_method, metric=metric, min_prevalence=min_prevalence,
                   do_rarefy=do_rarefy, palette=palette)

    meta = P.load_metadata(metadata) if metadata else None

    if stage == "feature_table":
        _log(logf, f"core (reused from amplicon-analysis): preprocess -> alpha -> beta ({metric}) -> {da_method}")
        res = analyze.run(input_path, metadata, condition, out_dir, da_method=da_method,
                          metric=metric, min_prevalence=min_prevalence, do_rarefy=do_rarefy, palette=palette)
        result.update(res)
        _log(logf, f"  differential: {res['n_significant']} significant features; "
                   f"PERMANOVA R2={res['permanova']['R2']:.2f}, p={res['permanova']['p']:.3f}")

    elif stage == "distance_matrix":
        import numpy as np
        from skbio.stats.distance import DistanceMatrix
        dmdf = pd.read_csv(input_path, index_col=0)
        dm = DistanceMatrix(np.ascontiguousarray(dmdf.values, dtype=float), ids=[str(i) for i in dmdf.index])
        coords, var, ids = D.ordinate(dm)
        perm = D.permanova_test(dm, meta, condition)
        F.beta_figure(coords, var, meta.loc[ids, condition].values, perm,
                      os.path.join(img, "beta_pcoa"), palette=palette)
        result["permanova"] = perm

    elif stage == "alpha_table":
        adf = pd.read_csv(input_path, index_col=0)
        groups = adf[condition] if condition in adf.columns else meta.loc[adf.index, condition]
        metrics = [c for c in adf.columns if c != condition] if condition in adf.columns \
            else list(adf.select_dtypes("number").columns)
        F.alpha_figure(adf[metrics], groups, os.path.join(img, "alpha_diversity"), palette=palette)

    pngs = [f for f in os.listdir(img) if f.endswith(".png")]
    ok = len(pngs) > 0
    _log(logf, f"validation: {'PASS' if ok else 'FAIL'} — {len(pngs)} figure(s), "
               f"{len([f for f in os.listdir(tables) if f.endswith('.csv')])} table(s)")
    result["ok"] = ok; result["log"] = logf
    return result
