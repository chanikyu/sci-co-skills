"""pipeline.py — transcriptome enter-at-any-stage orchestrator with logging and validation.

FASTQ -> QC + quantify -> gene counts. Count matrix -> pydeseq2 DE -> figures (PCA, volcano, heatmap).
DE table -> volcano. Mirrors the other SciCo pipeline skills.
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
import de
import figures


def _log(logf, msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(logf, "a") as fh:
        fh.write(line + "\n")


def run(input_path, metadata, condition, out_dir, from_stage=None, aligner="salmon",
        index=None, tx2gene=None, gtf=None, min_count=10, padj_thr=0.05, lfc_thr=1.0,
        ref_level=None, palette="okabe_ito", threads=4):
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
        _log(logf, f"QC (fastp) + quantify ({aligner})")
        counts_csv = runners.quantify(input_path, os.path.join(out_dir, "quant"), aligner,
                                      index, tx2gene, gtf, os.path.join(logs, "quantify.log"), threads)
        _log(logf, f"  quantified -> {counts_csv}; continuing to DE")
        return run(counts_csv, metadata, condition, out_dir, from_stage="count_matrix", aligner=aligner,
                   min_count=min_count, padj_thr=padj_thr, lfc_thr=lfc_thr, ref_level=ref_level,
                   palette=palette, threads=threads)

    meta = pd.read_csv(metadata, index_col=0)

    if stage == "count_matrix":
        counts = pd.read_csv(input_path, index_col=0)
        _log(logf, f"pydeseq2 DE on {counts.shape[0]} genes × {counts.shape[1]} samples (min_count={min_count})")
        res, norm, (test, ref) = de.run_de(counts, meta, condition, ref_level, min_count)
        res.to_csv(os.path.join(tables, "de_results.csv"))
        norm.to_csv(os.path.join(tables, "normalized_counts.csv"))
        nsig = de.n_significant(res, padj_thr, lfc_thr)
        _log(logf, f"  contrast: {test} vs {ref} | {nsig} DE genes (padj<{padj_thr}, |lfc|>={lfc_thr})")
        figures.pca_figure(norm, meta, condition, os.path.join(img, "pca"), palette=palette)
        figures.volcano_figure(res, os.path.join(img, "volcano"), padj_thr, lfc_thr, palette=palette)
        figures.heatmap_figure(norm, res, meta, condition, os.path.join(img, "heatmap"), palette=palette)
        result.update({"n_significant": nsig, "contrast": f"{test} vs {ref}"})

    elif stage == "de_table":
        res = pd.read_csv(input_path, index_col=0)
        figures.volcano_figure(res, os.path.join(img, "volcano"), padj_thr, lfc_thr, palette=palette)
        result["n_significant"] = de.n_significant(res, padj_thr, lfc_thr)

    pngs = [f for f in os.listdir(img) if f.endswith(".png")]
    ok = len(pngs) > 0
    _log(logf, f"validation: {'PASS' if ok else 'FAIL'} — {len(pngs)} figure(s), "
               f"{len([f for f in os.listdir(tables) if f.endswith('.csv')])} table(s)")
    result["ok"] = ok
    result["log"] = logf
    return result
