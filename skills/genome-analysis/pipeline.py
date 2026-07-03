"""
pipeline.py — genome-analysis enter-at-any-stage orchestrator with logging and validation.

FASTQ -> QC -> assembly -> assembly QC -> annotation -> species ID.
Contigs FASTA -> from assembly QC onward. Mirrors shotgun-analysis/pipeline.py.
"""
import os
import sys
import glob
import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import stages
import runners

_FASTA_EXT = (".fasta", ".fa", ".fna", ".fasta.gz", ".fa.gz", ".fna.gz")


def _log(logf, msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(logf, "a") as fh:
        fh.write(line + "\n")


def _resolve_contigs(path):
    if os.path.isdir(path):
        hits = [f for f in glob.glob(os.path.join(path, "*")) if f.lower().endswith(_FASTA_EXT)]
        if not hits:
            raise ValueError(f"no contigs FASTA in {path}")
        return hits[0]
    return path


def run(input_path, out_dir, from_stage=None, assembler="spades", long_reads=None,
        annotator="bakta", speciesid="gtdbtk", bakta_db=None, checkm2_db=None,
        gtdbtk_db=None, fastani_ref=None, threads=8):
    """Run the isolate-genome backbone from whatever stage `input_path` represents."""
    logs = os.path.join(out_dir, "logs")
    for sub in ("assembly", "qc", "annotation", "species", "logs"):
        os.makedirs(os.path.join(out_dir, sub), exist_ok=True)
    logf = os.path.join(logs, "pipeline.log")

    stage = from_stage or stages.detect_stage(input_path)["stage"]
    det = stages.detect_stage(input_path) if not from_stage else {"detail": f"forced --from {from_stage}"}
    _log(logf, f"input: {input_path}")
    _log(logf, f"stage: {stage}  ({det.get('detail', '')})")
    _log(logf, f"downstream: {' -> '.join(stages.DOWNSTREAM.get(stage, []))}")
    result = {"stage": stage, "out_dir": out_dir}

    # --- FASTQ: QC + assembly ---
    if stage == "fastq":
        _log(logf, f"QC (fastp) + assembly ({assembler}{' hybrid' if long_reads else ''})")
        if assembler in runners.LONG_ASSEMBLERS:
            reads = glob.glob(os.path.join(input_path, "*"))[0] if os.path.isdir(input_path) else input_path
            contigs = runners.assemble(reads, os.path.join(out_dir, "assembly"), assembler, logf, threads)
        else:
            r1, r2 = runners._pair(input_path)
            reads = runners.fastp(r1, r2, os.path.join(out_dir, "qc"), logf, threads)
            contigs = runners.assemble(reads, os.path.join(out_dir, "assembly"), assembler, logf,
                                       threads, long_reads=long_reads)
    else:
        contigs = _resolve_contigs(input_path)
    result["contigs"] = contigs
    _log(logf, f"contigs: {contigs}")

    # --- assembly QC ---
    runners.quast(contigs, os.path.join(out_dir, "qc", "quast"), logf, threads)
    _log(logf, "  QUAST done (contiguity: see qc/quast/report.tsv)")
    if checkm2_db:
        runners.checkm2(contigs, os.path.join(out_dir, "qc"), checkm2_db, logf, threads)
        _log(logf, "  CheckM2 done (completeness/contamination)")
    else:
        _log(logf, "  CheckM2 skipped (no --checkm2-db)")

    # --- annotation ---
    db = bakta_db if annotator == "bakta" else None
    if annotator == "bakta" and not bakta_db:
        _log(logf, "  Bakta has no --bakta-db; it will use its default DB path if configured")
    runners.annotate(contigs, os.path.join(out_dir, "annotation"), annotator, db, logf, threads)
    _log(logf, f"  annotation done ({annotator})")

    # --- species identification ---
    if speciesid == "gtdbtk" and gtdbtk_db:
        runners.species_id(contigs, os.path.join(out_dir, "species"), "gtdbtk", gtdbtk_db, None, logf, threads)
        _log(logf, "  species ID done (GTDB-Tk)")
    elif speciesid == "fastani" and fastani_ref:
        runners.species_id(contigs, os.path.join(out_dir, "species"), "fastani", None, fastani_ref, logf, threads)
        _log(logf, "  species ID done (fastANI)")
    else:
        _log(logf, f"  species ID skipped (no DB for {speciesid})")

    # --- validate ---
    ok = os.path.exists(contigs) and os.path.getsize(contigs) > 0 and \
        os.path.exists(os.path.join(out_dir, "qc", "quast", "report.tsv"))
    _log(logf, f"validation: {'PASS' if ok else 'FAIL'} — contigs + QUAST report present")
    result["ok"] = ok
    result["log"] = logf
    _write_report(out_dir, result, assembler, annotator, speciesid)
    return result


def _write_report(out_dir, result, assembler, annotator, speciesid):
    with open(os.path.join(out_dir, "report.md"), "w") as fh:
        fh.write(f"# Genome analysis report\n\n"
                 f"- entered at stage: **{result['stage']}**\n"
                 f"- assembler: {assembler} · annotator: {annotator} · species ID: {speciesid}\n"
                 f"- contigs: `{result.get('contigs', '')}`\n"
                 f"- validation: {'PASS' if result.get('ok') else 'FAIL'}\n\n"
                 f"Outputs: `assembly/` `qc/` (QUAST + CheckM2) `annotation/` `species/` `logs/`.\n")
