"""
pipeline.py — amr-profiling orchestrator. Screens assembled genomes for AMR (AMRFinderPlus +
abricate/CARD), virulence (abricate/VFDB), and plasmids (abricate/PlasmidFinder); a batch gets
a presence/absence summary per database. Logs + validates + writes report.md.
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


def run(input_path, out_dir, organism=None, amrfinder_db=None, threads=4):
    tables = os.path.join(out_dir, "tables")
    logs = os.path.join(out_dir, "logs")
    os.makedirs(tables, exist_ok=True)
    os.makedirs(logs, exist_ok=True)
    logf = os.path.join(logs, "amr.log")

    gs = runners.genomes(input_path)
    _log(logf, f"genomes: {len(gs)} ({', '.join(os.path.basename(g) for g in gs)})")

    # --- AMRFinderPlus (primary AMR) ---
    amr_dir = os.path.join(tables, "amrfinder")
    for g in gs:
        runners.amrfinder(g, amr_dir, organism, amrfinder_db, logf, threads)
    _log(logf, f"AMRFinderPlus -> {amr_dir}")

    # --- abricate: AMR / virulence / plasmid + batch summaries ---
    summaries = {}
    for target, db in runners.ABRICATE_DBS.items():
        ab_dir = os.path.join(tables, "abricate", db)
        tabs = [runners.abricate(g, db, ab_dir, logf) for g in gs]
        summaries[target] = runners.abricate_summary(tabs, db, tables, logf)
        _log(logf, f"abricate {target} ({db}) -> {summaries[target]}")

    ok = all(os.path.exists(s) for s in summaries.values())
    _log(logf, f"validation: {'PASS' if ok else 'FAIL'} — AMR/virulence/plasmid summaries present")
    with open(os.path.join(out_dir, "report.md"), "w") as fh:
        fh.write(f"# AMR profiling report\n\n- genomes: {len(gs)}\n"
                 f"- AMR: AMRFinderPlus + abricate/CARD\n"
                 f"- virulence: abricate/VFDB · plasmid: abricate/PlasmidFinder\n"
                 f"- summaries: {', '.join(f'`{os.path.basename(s)}`' for s in summaries.values())}\n"
                 f"- validation: {'PASS' if ok else 'FAIL'}\n\n"
                 f"> Note: a gene hit predicts genotype, not clinical phenotype.\n")
    return {"ok": ok, "summaries": summaries, "log": logf}
