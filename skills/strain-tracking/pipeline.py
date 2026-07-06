"""pipeline.py — strain-tracking enter-at-any-stage orchestrator.

Multi-sample reads → per-sample strain profiling (StrainPhlAn / inStrain) → per-species strain distance
matrices → same-strain calls → strain-sharing network + longitudinal persistence. A distance matrix /
a directory of matrices enters straight into the (testable) sharing + persistence core.
"""
import os
import sys
import glob
import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_AMP = os.path.abspath(os.path.join(_HERE, "..", "amplicon-analysis"))
_SDV = os.path.abspath(os.path.join(_HERE, "..", "scientific-data-viz"))
for p in (_AMP, _SDV):                 # siblings: lower priority so this skill's own modules win
    if p not in sys.path:
        sys.path.append(p)
if _HERE in sys.path:                   # this skill's dir must resolve stages/share/persist/figures first
    sys.path.remove(_HERE)
sys.path.insert(0, _HERE)

for _m in ("stages", "runners", "share", "persist", "figures"):   # evict a sibling skill's same-named module
    _cached = sys.modules.get(_m)
    if _cached is not None and getattr(_cached, "__file__", None) and \
            os.path.dirname(os.path.abspath(_cached.__file__)) != _HERE:
        del sys.modules[_m]

import numpy as np
import pandas as pd
import journal_style as J
import stages as ST
import runners as R
import share as SH
import persist as PS
import figures as SF
import preprocess as P              # amplicon-analysis: load_metadata

_DEFAULT_THRESH = {"identity": 99.999, "distance": 0.1}   # popANI% for inStrain; nGD placeholder for StrainPhlAn


def _log(logf, msg):
    line = f"[{datetime.datetime.now():%H:%M:%S}] {msg}"
    print(line)
    with open(logf, "a") as fh:
        fh.write(line + "\n")


def _read(path):
    return pd.read_csv(path, sep="\t" if path.lower().endswith((".tsv", ".txt")) else ",", index_col=0)


def _load_matrix_dir(path):
    mats = {}
    for f in sorted(glob.glob(os.path.join(path, "*.csv")) + glob.glob(os.path.join(path, "*.tsv"))):
        mats[os.path.splitext(os.path.basename(f))[0]] = _read(f)
    return mats


def _validate_matrix(sp, m):
    """Coerce ids to str, align columns to rows, require the same sample set + symmetry."""
    m = m.copy()
    m.index = m.index.astype(str); m.columns = m.columns.astype(str)
    if set(m.index) != set(m.columns):
        raise ValueError(f"species '{sp}': matrix rows and columns are not the same sample set.")
    m = m.reindex(columns=m.index)
    if not np.allclose(m.values, m.values.T, atol=1e-6, equal_nan=True):
        raise ValueError(f"species '{sp}': strain matrix is not symmetric.")
    return m


def _check_metric_scale(species_mat, metric, logf):
    """Catch the most likely user error: a percent-identity matrix read as 'distance' (or vice-versa)."""
    finite = [m.values[np.isfinite(m.values)].ravel() for m in species_mat.values() if m.size]
    finite = [f for f in finite if f.size]
    if not finite:
        return
    mx = float(np.max(np.abs(np.concatenate(finite))))
    if metric == "distance" and mx > 2.0:
        raise ValueError(f"metric='distance' but values reach {mx:.1f} — looks like a percent-identity "
                         f"matrix; set metric='identity'.")
    if metric == "identity" and mx <= 1.5:
        _log(logf, "  WARNING: metric='identity' but values are <=1.5 — a 0-1 identity needs a matching "
                   "threshold (popANI default 99.999 is on a 0-100 scale).")


def run(input_path, metadata, out_dir, engine="strainphlan", metric="distance", threshold=None,
        subject_col=None, time_col=None, genomes_fasta=None, from_stage=None, palette="okabe_ito"):
    img, _ = J.prepare_output(out_dir)
    tables = os.path.join(out_dir, "tables"); logs = os.path.join(out_dir, "logs")
    os.makedirs(tables, exist_ok=True); os.makedirs(logs, exist_ok=True)
    logf = os.path.join(logs, "pipeline.log")

    det = ST.detect_stage(input_path); stage = from_stage or det["stage"]
    _log(logf, f"input: {input_path}"); _log(logf, f"stage: {stage} ({det.get('detail','')})")
    meta = P.load_metadata(metadata) if metadata else None
    if meta is not None:
        meta.index = meta.index.astype(str)
    result = {"stage": stage, "out_dir": out_dir}

    if stage == "reads":
        _log(logf, f"strain profiling ({engine})")
        species_mat, metric = R.detect_strains(input_path, os.path.join(out_dir, "profile"),
                                               engine=engine, genomes_fasta=genomes_fasta,
                                               log=os.path.join(logs, "profile.log"))
    elif stage == "matrix_dir":
        species_mat = _load_matrix_dir(input_path)
    else:
        species_mat = {"species": _read(input_path)}
    if not species_mat:
        raise ValueError("no per-species strain matrices were produced/loaded.")
    species_mat = {sp: _validate_matrix(sp, m) for sp, m in species_mat.items()}
    _check_metric_scale(species_mat, metric, logf)
    if meta is not None:
        miss = set().union(*[set(m.index) for m in species_mat.values()]) - set(meta.index)
        if miss:
            raise ValueError(f"{len(miss)} matrix sample(s) not in metadata (e.g. {sorted(miss)[:3]}).")

    thr = threshold if threshold is not None else _DEFAULT_THRESH[metric]
    if metric == "distance" and threshold is None:
        _log(logf, "  NOTE: default distance threshold 0.1 is a placeholder — StrainPhlAn thresholds are "
                   "tool/species-specific; set `threshold` explicitly for real data.")
    _log(logf, f"  {len(species_mat)} species; metric={metric}, same-strain threshold={thr}")

    species_adj = {sp: SH.same_strain_adjacency(m, thr, metric) for sp, m in species_mat.items()}

    # per-species shared pairs
    rows = []
    for sp, adj in species_adj.items():
        for a, b in SH.shared_pairs(adj):
            r = {"species": sp, "sample_a": a, "sample_b": b}
            if meta is not None and subject_col:
                r["subject_a"] = meta.loc[a, subject_col]; r["subject_b"] = meta.loc[b, subject_col]
                r["cross_subject"] = r["subject_a"] != r["subject_b"]
            rows.append(r)
    _cols = ["species", "sample_a", "sample_b"] + (
        ["subject_a", "subject_b", "cross_subject"] if (meta is not None and subject_col) else [])
    pd.DataFrame(rows, columns=_cols).to_csv(os.path.join(tables, "shared_strains.csv"), index=False)

    G, edges = SH.sharing_network(species_adj, meta, subject_col)
    edges.to_csv(os.path.join(tables, "sharing_edges.csv"), index=False)
    SF.sharing_network_figure(G, os.path.join(img, "sharing_network"), palette=palette)
    result["n_species"] = len(species_mat)
    result["n_sharing_links"] = G.number_of_edges()
    _log(logf, f"  sharing network: {G.number_of_nodes()} nodes, {G.number_of_edges()} shared-strain links")

    if meta is not None and subject_col and time_col:
        pdf = PS.persistence(species_mat, meta, subject_col, time_col, thr, metric)
        pdf.to_csv(os.path.join(tables, "persistence.csv"), index=False)
        if len(pdf):
            SF.persistence_figure(pdf, os.path.join(img, "persistence"), palette=palette)
        result["persistence"] = pdf["outcome"].value_counts().to_dict() if len(pdf) else {}
        _log(logf, f"  persistence: {result['persistence']}")

    result["ok"] = os.path.exists(os.path.join(img, "sharing_network.png"))
    result["log"] = logf
    _log(logf, f"validation: {'PASS' if result['ok'] else 'FAIL'} — sharing_network figure "
               f"{'present' if result['ok'] else 'MISSING'}. "
               f"Sharing != transmission; per species; state tool + threshold ({metric} {thr}) + DB.")
    return result
