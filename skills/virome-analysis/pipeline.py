"""pipeline.py — virome enter-at-any-stage orchestrator.

contigs → geNomad → CheckV → dereplicate (vOTU) → map reads → vOTU abundance. A vOTU abundance table
/ distance / alpha → the shared downstream, REUSED from amplicon-analysis (analyze / diversity /
figures). Mirrors shotgun-analysis / metatranscriptome-analysis.
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
import derep
import abundance
import analyze                     # amplicon-analysis core
import diversity as D
import figures as F
import preprocess as P


def _log(logf, msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(logf, "a") as fh:
        fh.write(line + "\n")


def _fasta_lengths(path):
    lengths, name, n = {}, None, 0
    with open(path) as fh:
        for line in fh:
            if line.startswith(">"):
                if name:
                    lengths[name] = n
                name, n = line[1:].split()[0], 0
            else:
                n += len(line.strip())
    if name:
        lengths[name] = n
    return lengths


def _write_reps(fasta, reps, out_fa):
    keep, write = set(reps), False
    with open(fasta) as fh, open(out_fa, "w") as out:
        for line in fh:
            if line.startswith(">"):
                write = line[1:].split()[0] in keep
            if write:
                out.write(line)
    return out_fa


def _read(path):
    return pd.read_csv(path, sep="\t" if path.lower().endswith((".tsv", ".txt")) else ",", index_col=0)


def _filter_checkv(fasta, quality_summary, out_fa, logf, keep=("Complete", "High-quality", "Medium-quality")):
    """Keep only Medium+ vOTUs (CheckV completeness estimate) and log the quality tiers."""
    try:
        q = pd.read_csv(quality_summary, sep="\t")
    except Exception:
        return fasta
    idcol = "contig_id" if "contig_id" in q.columns else q.columns[0]
    if "checkv_quality" not in q.columns:
        return fasta
    _log(logf, f"  CheckV quality tiers {q['checkv_quality'].value_counts().to_dict()}")
    keep_ids = set(q.loc[q["checkv_quality"].isin(keep), idcol].astype(str))
    _log(logf, f"  keeping {len(keep_ids)} Medium+ vOTUs")
    return _write_reps(fasta, keep_ids, out_fa)


def _parse_coverm(tsv):
    """CoverM contig output (wide: contig + <sample> RPKM / <sample> covered fraction) -> {sample: df}."""
    df = pd.read_csv(tsv, sep="\t", index_col=0)
    per = {}
    for col in df.columns:
        if col.lower().endswith("rpkm"):
            s = col.rsplit(" ", 1)[0]
            bcol = [c for c in df.columns if c.startswith(s) and "covered" in c.lower()]
            per[s] = pd.DataFrame({"rpkm": df[col], "covered_fraction": df[bcol[0]] if bcol else 1.0})
    return per


def run(input_path, metadata, group_col, out_dir, from_stage=None, reads_dir=None,
        genomad_db=None, checkv_db=None, min_score=0.7, breadth_min=0.75,
        da_method="clr_test", metric="braycurtis", min_prevalence=0.1, do_rarefy=False, palette="okabe_ito"):
    img, scr = J.prepare_output(out_dir)
    tables = os.path.join(out_dir, "tables"); logs = os.path.join(out_dir, "logs")
    os.makedirs(tables, exist_ok=True); os.makedirs(logs, exist_ok=True)
    logf = os.path.join(logs, "pipeline.log")

    det = stages.detect_stage(input_path)
    stage = from_stage or det["stage"]
    _log(logf, f"input: {input_path}")
    _log(logf, f"stage: {stage} ({det.get('detail','')})")
    result = {"stage": stage, "out_dir": out_dir}

    if stage == "contigs":
        if not reads_dir:
            raise ValueError("reads_dir is required for the contigs stage (to map reads for vOTU abundance).")
        _log(logf, "geNomad → CheckV (Medium+) → dereplicate (vOTU) → map reads")
        flog = os.path.join(logs, "front.log")
        viral = runners.genomad(input_path, os.path.join(out_dir, "genomad"), genomad_db, flog, min_score)
        clean, qsum = runners.checkv(viral, os.path.join(out_dir, "checkv"), checkv_db, flog)
        clean = _filter_checkv(clean, qsum, os.path.join(out_dir, "checkv", "medium_plus.fna"), logf)
        ani = runners.ani_table(clean, os.path.join(out_dir, "ani"), flog)
        lengths = _fasta_lengths(clean)
        _, clusters = derep.cluster_votus(pd.read_csv(ani, sep="\t"), lengths)
        votu_fa = _write_reps(clean, list(clusters), os.path.join(out_dir, "votus.fna"))
        derep.votu_summary(clusters).to_csv(os.path.join(tables, "votu_clusters.csv"), index=False)
        _log(logf, f"  {len(lengths)} viral genomes → {len(clusters)} vOTUs (95% ANI / 85% AF)")
        coverm = runners.map_coverm(votu_fa, reads_dir, os.path.join(out_dir, "coverm"), flog)
        tab = abundance.build_table(_parse_coverm(coverm), breadth_min)
        tab_path = os.path.join(tables, "votu_abundance.csv")
        tab.to_csv(tab_path)
        _log(logf, f"  vOTU abundance: {tab.shape[0]} samples × {tab.shape[1]} vOTUs (breadth≥{breadth_min})")
        return run(tab_path, metadata, group_col, out_dir, from_stage="feature_table",
                   da_method=da_method, metric=metric, min_prevalence=min_prevalence,
                   do_rarefy=do_rarefy, palette=palette)

    meta = P.load_metadata(metadata) if metadata else None

    if stage == "feature_table":
        _log(logf, f"core (reused from amplicon-analysis): preprocess → alpha → beta ({metric}) → {da_method}")
        res = analyze.run(input_path, metadata, group_col, out_dir, da_method=da_method, metric=metric,
                          min_prevalence=min_prevalence, do_rarefy=do_rarefy, palette=palette)
        result.update(res)
        _log(logf, f"  differential: {res['n_significant']} significant vOTUs; "
                   f"PERMANOVA R2={res['permanova']['R2']:.2f}, p={res['permanova']['p']:.3f}")

    elif stage == "distance_matrix":
        if meta is None:
            raise ValueError("metadata is required for the distance_matrix stage.")
        import numpy as np
        from skbio.stats.distance import DistanceMatrix
        dmdf = _read(input_path)
        dm = DistanceMatrix(np.ascontiguousarray(dmdf.values, dtype=float), ids=[str(i) for i in dmdf.index])
        coords, var, ids = D.ordinate(dm)
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
    _log(logf, f"validation: {'PASS' if result['ok'] else 'FAIL'} — {len(pngs)} figure(s)")
    return result
