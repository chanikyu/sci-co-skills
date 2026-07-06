"""pipeline.py — resistome enter-at-any-stage orchestrator.

QC'd reads → ARG detection (RGI/DeepARG) → hAMRonize → normalize (RPKM + per-marker) → ARG × samples.
An ARG abundance table / distance / alpha → the shared downstream, REUSED from amplicon-analysis
(analyze / diversity / figures); optional drug-class aggregation. Mirrors virome / shotgun.
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
import journal_style as J
import stages
import runners
import normalize as N
import aggregate as AG
import analyze                     # amplicon-analysis core
import diversity as D
import figures as F
import preprocess as P


def _log(logf, msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(logf, "a") as fh:
        fh.write(line + "\n")


def _read(path):
    return pd.read_csv(path, sep="\t" if path.lower().endswith((".tsv", ".txt")) else ",", index_col=0)


def run(input_path, metadata, group_col, out_dir, from_stage=None, engine="deeparg", card_db=None,
        marker_rpkm=None, arg_to_class=None, da_method="clr_test", metric="braycurtis",
        min_prevalence=0.1, do_rarefy=False, palette="okabe_ito"):
    img, scr = J.prepare_output(out_dir)
    tables = os.path.join(out_dir, "tables"); logs = os.path.join(out_dir, "logs")
    os.makedirs(tables, exist_ok=True); os.makedirs(logs, exist_ok=True)
    logf = os.path.join(logs, "pipeline.log")

    det = stages.detect_stage(input_path)
    stage = from_stage or det["stage"]
    _log(logf, f"input: {input_path}")
    _log(logf, f"stage: {stage} ({det.get('detail','')})")
    result = {"stage": stage, "out_dir": out_dir}

    if stage == "reads":
        _log(logf, f"ARG detection ({engine}) → read counts + library size (seqkit) → normalize")
        counts, gene_lengths, total_reads, arg_map = runners.detect_args(
            input_path, os.path.join(out_dir, "detect"), engine=engine, card_db=card_db,
            log=os.path.join(logs, "detect.log"))
        normed, method = N.normalize(counts, gene_lengths, total_reads, marker_rpkm)
        tab_path = os.path.join(tables, "arg_abundance.csv")
        normed.T.to_csv(tab_path)                             # samples × ARGs
        _log(logf, f"  {counts.shape[0]} ARGs × {counts.shape[1]} samples normalized ({method})")
        return run(tab_path, metadata, group_col, out_dir, from_stage="feature_table", engine=engine,
                   arg_to_class=(arg_to_class or arg_map), da_method=da_method, metric=metric,
                   min_prevalence=min_prevalence, do_rarefy=do_rarefy, palette=palette)

    meta = P.load_metadata(metadata) if metadata else None
    if meta is not None:
        meta.index = meta.index.astype(str)

    if stage == "feature_table":
        _log(logf, f"core (reused from amplicon-analysis): preprocess → alpha → beta ({metric}) → {da_method}")
        res = analyze.run(input_path, metadata, group_col, out_dir, da_method=da_method, metric=metric,
                          min_prevalence=min_prevalence, do_rarefy=do_rarefy, palette=palette)
        result.update(res)
        _log(logf, f"  differential: {res['n_significant']} significant ARGs; "
                   f"PERMANOVA R2={res['permanova']['R2']:.2f}, p={res['permanova']['p']:.3f}")
        if arg_to_class:
            argT = _read(input_path).T                        # ARG × samples
            dc = AG.to_drug_class(argT, arg_to_class)
            dc.to_csv(os.path.join(tables, "drug_class.csv"))
            AG.class_summary(dc).to_csv(os.path.join(tables, "drug_class_summary.csv"))
            unc = AG.unclassified_count(argT, arg_to_class)
            _log(logf, f"  aggregated to {dc.shape[0]} drug classes ({unc} ARGs unclassified)")
            result["n_drug_classes"] = int(dc.shape[0])

    elif stage == "distance_matrix":
        if meta is None:
            raise ValueError("metadata is required for the distance_matrix stage.")
        import numpy as np
        from skbio.stats.distance import DistanceMatrix
        dmdf = _read(input_path)
        dm = DistanceMatrix(np.ascontiguousarray(dmdf.values, dtype=float), ids=[str(i) for i in dmdf.index])
        coords, var, ids = D.ordinate(dm)
        missing = set(ids) - set(meta.index)
        if missing:
            raise ValueError(f"{len(missing)} distance-matrix samples missing from metadata "
                             f"(e.g. {sorted(missing)[:3]}).")
        perm = D.permanova_test(dm, meta, group_col)
        F.beta_figure(coords, var, meta.loc[ids, group_col].values, perm,
                      os.path.join(img, "beta_pcoa"), palette=palette)
        result["permanova"] = perm

    elif stage == "alpha_table":
        adf = _read(input_path)
        if group_col not in adf.columns and meta is None:
            raise ValueError("metadata (or a group column in the table) is required for the alpha_table stage.")
        groups = adf[group_col] if group_col in adf.columns else meta.loc[adf.index, group_col]
        metrics = [c for c in adf.select_dtypes("number").columns if c != group_col]
        F.alpha_figure(adf[metrics], groups, os.path.join(img, "alpha_diversity"), palette=palette)

    pngs = [f for f in os.listdir(img) if f.endswith(".png")]
    result["ok"] = len(pngs) > 0; result["log"] = logf
    _log(logf, f"validation: {'PASS' if result['ok'] else 'FAIL'} — {len(pngs)} figure(s). "
               f"Genotype != phenotype; state the DB + cutoffs.")
    return result
