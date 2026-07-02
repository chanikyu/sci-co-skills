"""
pipeline.py — shotgun enter-at-any-stage orchestrator with logging and validation.

Raw FASTQ → shotgun front stages (QC → host removal → profiling → HUMAnN) → abundance table.
Abundance table / distance matrix / alpha table → the shared downstream, REUSED from the
sibling amplicon-analysis skill (its analyze / diversity / figures). Mirrors
amplicon-analysis/pipeline.py.
"""
import os
import sys
import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_AMP = os.path.join(_HERE, "..", "amplicon-analysis")          # reuse the analysis core
_SDV = os.path.join(_HERE, "..", "scientific-data-viz")
for p in (_HERE, _AMP, _SDV):                                   # _HERE first: our own `stages`
    if p not in sys.path:
        sys.path.insert(0, p)

import pandas as pd
import stages                    # shotgun (this dir)
import frontstages               # shotgun read-based front stages (this dir)
import assembly                  # shotgun assembly-based track (this dir)
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


def run(input_path, metadata, group_col, out_dir, from_stage=None, profiler="metaphlan",
        da_method="clr_test", metric="braycurtis", min_prevalence=0.1,
        do_rarefy=False, palette="okabe_ito",
        host_index=None, metaphlan_db=None, kraken_db=None, readlen=150,
        humann_nuc_db=None, humann_prot_db=None,
        track="read", assembler="megahit", coassembly=True, checkm2_db=None, gtdbtk_db=None,
        threads=4):
    """Run the shotgun pipeline from whatever stage `input_path` represents.
    track: 'read' (profiling: MetaPhlAn/Kraken2) or 'assembly' (MAGs: assemble -> bin -> QC)."""
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
        if track == "assembly":
            _log(logf, f"Assembly track: fastp QC{' + host removal' if host_index else ''} -> "
                       f"{assembler} -> MetaBAT2+CONCOCT+SemiBin2 -> DAS_Tool -> "
                       f"CheckM2/GTDB-Tk -> MAG abundance")
            ab = assembly.run(input_path, os.path.join(out_dir, "assembly"), assembler=assembler,
                              coassembly=coassembly, host_index=host_index, checkm2_db=checkm2_db,
                              gtdbtk_db=gtdbtk_db, threads=threads,
                              logf=os.path.join(logs, "assembly.log"))
        else:
            _log(logf, f"Read-based track: fastp QC{' + host removal' if host_index else ''} -> "
                       f"{profiler}{' + HUMAnN' if (humann_nuc_db and humann_prot_db) else ''}")
            ab = frontstages.run(input_path, os.path.join(out_dir, "frontstages"), profiler=profiler,
                                 host_index=host_index, metaphlan_db=metaphlan_db, kraken_db=kraken_db,
                                 readlen=readlen, humann_nuc_db=humann_nuc_db,
                                 humann_prot_db=humann_prot_db, threads=threads,
                                 logf=os.path.join(logs, "frontstages.log"))
        _log(logf, f"  {track} track -> {ab}; continuing downstream")
        return run(ab, metadata, group_col, out_dir, from_stage="feature_table", profiler=profiler,
                   da_method=da_method, metric=metric, min_prevalence=min_prevalence,
                   do_rarefy=do_rarefy, palette=palette)

    meta = P.load_metadata(metadata) if metadata else None

    if stage == "feature_table":            # taxonomic/functional abundance table
        _log(logf, f"core (reused from amplicon-analysis): preprocess -> alpha -> beta ({metric}) -> {da_method}")
        res = analyze.run(input_path, metadata, group_col, out_dir, da_method=da_method,
                          metric=metric, min_prevalence=min_prevalence,
                          do_rarefy=do_rarefy, palette=palette)
        result.update(res)
        _log(logf, f"  differential: {res['n_significant']} significant features")
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

    pngs = [f for f in os.listdir(img) if f.endswith(".png")]
    ok = len(pngs) > 0
    _log(logf, f"validation: {'PASS' if ok else 'FAIL'} — {len(pngs)} figure(s), "
               f"{len([f for f in os.listdir(tables) if f.endswith('.csv')])} table(s)")
    result["ok"] = ok
    result["log"] = logf
    return result
