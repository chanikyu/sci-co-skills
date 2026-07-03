"""
pipeline.py — strain-typing orchestrator (MLST always; serotyping / cgMLST optional).
Input: a contigs FASTA or a folder of FASTAs. Logs + validates + writes report.md.
"""
import os
import sys
import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import runners


def _log(logf, msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(logf, "a") as fh:
        fh.write(line + "\n")


def run(input_path, out_dir, serotyper=None, cgmlst_scheme=None, threads=4):
    tables = os.path.join(out_dir, "tables")
    logs = os.path.join(out_dir, "logs")
    os.makedirs(tables, exist_ok=True)
    os.makedirs(logs, exist_ok=True)
    logf = os.path.join(logs, "typing.log")

    gs = runners.genomes(input_path)
    _log(logf, f"genomes: {len(gs)} ({', '.join(os.path.basename(g) for g in gs)})")

    mlst_tsv = runners.mlst(gs, tables, logf)
    _log(logf, f"MLST -> {mlst_tsv}")
    outputs = {"mlst": mlst_tsv}

    if serotyper:
        sero = os.path.join(tables, "serotype")
        for g in gs:
            runners.serotype(g, sero, serotyper, logf, threads)
        _log(logf, f"serotyping ({serotyper}) -> {sero}")
        outputs["serotype"] = sero

    if cgmlst_scheme:
        gdir = input_path if os.path.isdir(input_path) else os.path.dirname(input_path)
        runners.cgmlst(gdir, tables, cgmlst_scheme, logf, threads)
        _log(logf, f"cgMLST (scheme {cgmlst_scheme}) -> {os.path.join(tables, 'cgmlst')}")
        outputs["cgmlst"] = os.path.join(tables, "cgmlst")

    ok = os.path.exists(mlst_tsv) and os.path.getsize(mlst_tsv) > 0
    _log(logf, f"validation: {'PASS' if ok else 'FAIL'} — MLST table present")
    with open(os.path.join(out_dir, "report.md"), "w") as fh:
        fh.write(f"# Strain typing report\n\n- genomes: {len(gs)}\n"
                 f"- MLST: `{mlst_tsv}`\n"
                 f"- serotyping: {serotyper or 'skipped'}\n"
                 f"- cgMLST: {'yes (' + cgmlst_scheme + ')' if cgmlst_scheme else 'skipped'}\n"
                 f"- validation: {'PASS' if ok else 'FAIL'}\n")
    return {"ok": ok, "outputs": outputs, "log": logf}
