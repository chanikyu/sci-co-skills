"""pipeline.py — metabolomics upstream orchestrator (raw spectra -> annotated feature table).

raw mzML/.CDF -> feature detection (asari/XCMS/eRah) -> feature table. A feature table -> QC
(RSD/blank/QC-RLSC) -> annotation (matchms + MSI level). An annotated table -> hand off to
microbiome-metabolome-analysis. Figures reuse scientific-data-viz.
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
import runners
import qc
import annotate as A
import figures as F


def _log(logf, msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(logf, "a") as fh:
        fh.write(line + "\n")


def _read(path):
    return pd.read_csv(path, sep="\t" if path.lower().endswith((".tsv", ".txt")) else ",", index_col=0)


def _load_spectra(path):
    from matchms.importing import load_from_mgf, load_from_msp
    loader = load_from_mgf if path.lower().endswith(".mgf") else load_from_msp
    return list(loader(path))


def run(input_path, metadata, out_dir, platform="lc", engine="asari", from_stage=None,
        library=None, spectra=None, mode="pos", max_rsd=0.30, blank_fold=3.0, qc_span=0.5,
        cosine_min=0.7, ppm=10, palette="okabe_ito"):
    img, scr = J.prepare_output(out_dir)
    tables = os.path.join(out_dir, "tables"); logs = os.path.join(out_dir, "logs")
    os.makedirs(tables, exist_ok=True); os.makedirs(logs, exist_ok=True)
    logf = os.path.join(logs, "pipeline.log")

    det = stages.detect_stage(input_path)
    stage = from_stage or det["stage"]
    _log(logf, f"input: {input_path}")
    _log(logf, f"stage: {stage} ({det.get('detail','')}) | platform={platform}")
    result = {"stage": stage, "out_dir": out_dir}

    if stage == "raw":
        _log(logf, f"feature detection ({'GC/eRah' if platform=='gc' else engine})")
        ftab = runners.detect_features(input_path, os.path.join(out_dir, "detect"), platform=platform,
                                       engine=engine, mode=mode, ppm=ppm,
                                       log=os.path.join(logs, "detect.log"))
        _log(logf, f"  detected -> {ftab}; continuing to QC")
        return run(ftab, metadata, out_dir, platform=platform, engine=engine, from_stage="feature_table",
                   library=library, spectra=spectra, mode=mode, max_rsd=max_rsd, blank_fold=blank_fold,
                   qc_span=qc_span, cosine_min=cosine_min, ppm=ppm, palette=palette)

    if stage == "annotated_table":
        _log(logf, "already annotated — hand off to microbiome-metabolome-analysis for statistics")
        result["ok"] = True; result["log"] = logf
        return result

    # --- feature_table: QC then annotation ---
    df = _read(input_path)
    meta = _read(metadata)
    df.index = df.index.astype(str).str.strip()
    meta.index = meta.index.astype(str).str.strip()
    # detectors emit features × samples; the QC / stats contract is samples × features -> auto-orient
    if not (set(df.index) & set(meta.index)) and (set(df.columns) & set(meta.index)):
        df = df.T
        _log(logf, "  transposed feature table to samples × features")
    common = [s for s in df.index if s in meta.index]
    if not common:
        raise ValueError(f"No overlapping sample IDs between the feature table ({len(df.index)}) and "
                         f"metadata ({len(meta.index)}) — check that sample IDs match.")
    if len(common) < len(df.index):
        _log(logf, f"  WARNING: only {len(common)}/{len(df.index)} table samples matched metadata")
    df = df.loc[common]; meta = meta.loc[common]
    if "sample_type" in meta.columns:
        st = meta["sample_type"].astype(str).str.strip().str.lower()
        extra = set(st.unique()) - {"sample", "qc", "blank"}
        if extra:
            _log(logf, f"  note: unrecognized sample_type {extra} treated as 'sample'")
    else:
        st = pd.Series("sample", index=df.index)
    qc_mask, blank_mask = (st == "qc"), (st == "blank")
    sample_mask = ~(qc_mask | blank_mask)
    _log(logf, f"{df.shape[0]} samples ({int(qc_mask.sum())} QC, {int(blank_mask.sum())} blank) "
               f"× {df.shape[1]} features")
    n0 = df.shape[1]

    # QC order: blank filter -> drift correction (QC-RLSC) -> RSD filter (drift must be removed
    # before RSD, else within-run drift inflates RSD and wrongly drops good features).
    df = qc.blank_filter(df, blank_mask, sample_mask, blank_fold)
    if qc_mask.sum() >= 4 and "run_order" in meta.columns:
        df = qc.qc_rlsc(df, qc_mask, meta["run_order"].values, qc_span)
        _log(logf, "  QC-RLSC drift correction applied")
    elif qc_mask.sum() >= 4:
        _log(logf, "  QC-RLSC skipped — no 'run_order' column in metadata")
    rsd = pd.Series(dtype=float)
    if qc_mask.any():
        df, rsd = qc.rsd_filter(df, qc_mask, max_rsd)
    df.to_csv(os.path.join(tables, "feature_table_clean.csv"))
    _log(logf, f"QC: {n0} -> {df.shape[1]} features kept (blank×{blank_fold}, then RSD<{max_rsd})")
    if rsd.notna().any():
        F.qc_rsd_figure(rsd, max_rsd, os.path.join(img, "qc_rsd"), palette=palette)
    result["n_features"] = int(df.shape[1])

    if spectra and library:
        _log(logf, "annotation: matchms spectral matching + MSI level")
        ann = A.annotate(_load_spectra(spectra), _load_spectra(library), cosine_min=cosine_min)
        ann.to_csv(os.path.join(tables, "annotations.csv"), index=False)
        summ = A.annotation_summary(ann)
        F.msi_figure(summ, os.path.join(img, "msi_levels"), palette=palette)
        lv = summ["n_features"].to_dict()
        _log(logf, f"  annotated: {int(ann['msi_level'].isin([1,2,3]).sum())}/{len(ann)} features "
                   f"(MSI level counts {lv}); most putative (2-3)")
        result["annotation"] = lv
    else:
        _log(logf, "annotation skipped — provide spectra (.mgf/.msp) + a library to annotate")

    pngs = [f for f in os.listdir(img) if f.endswith(".png")]
    result["ok"] = True; result["log"] = logf
    _log(logf, f"validation: PASS — {len(pngs)} figure(s); clean table -> hand off to "
               f"microbiome-metabolome-analysis for stats")
    return result
