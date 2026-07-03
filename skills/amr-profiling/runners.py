"""
runners.py — amr-profiling runners (AMRFinderPlus + abricate for AMR / virulence / plasmid).
Tools run inside the `scico-amr` conda env via `conda run`.

UNVERIFIED in-session (needs env + assemblies + AMRFinderPlus DB). Standard tool usage.
"""
import os
import glob
import datetime
import subprocess

ENV = "scico-amr"
_FA = (".fasta", ".fa", ".fna", ".fasta.gz", ".fa.gz", ".fna.gz")

# abricate database per target
ABRICATE_DBS = {"amr": "card", "virulence": "vfdb", "plasmid": "plasmidfinder"}


def _tee(cmd, logf, shell=False):
    with open(logf, "a") as fh:
        fh.write(f"[{datetime.datetime.now():%H:%M:%S}] $ {cmd if shell else ' '.join(cmd)}\n")
    p = subprocess.run(cmd, capture_output=True, text=True, shell=shell)
    with open(logf, "a") as fh:
        fh.write(p.stdout + p.stderr + f"[exit {p.returncode}]\n")
    if p.returncode != 0:
        raise RuntimeError(f"command failed (see {logf}): {cmd}")


def _cr(*args):
    return ["conda", "run", "-n", ENV, *args]


def genomes(path):
    if os.path.isdir(path):
        gs = sorted(f for f in glob.glob(os.path.join(path, "*")) if f.lower().endswith(_FA))
        if not gs:
            raise ValueError(f"no FASTA genomes in {path}")
        return gs
    return [path]


def amrfinder(genome, out, organism, db, log, threads=4):
    os.makedirs(out, exist_ok=True)
    name = os.path.splitext(os.path.basename(genome))[0]
    res = os.path.join(out, f"{name}.amrfinder.tsv")
    cmd = _cr("amrfinder", "-n", genome, "-o", res, "--plus", "--threads", str(threads))
    if organism:
        cmd += ["--organism", organism]
    if db:
        cmd += ["--database", db]
    _tee(cmd, log)
    return res


def abricate(genome, db, out, log):
    """Screen one genome against one abricate database -> a .tab file (path returned)."""
    os.makedirs(out, exist_ok=True)
    name = os.path.splitext(os.path.basename(genome))[0]
    tab = os.path.join(out, f"{name}.{db}.tab")
    _tee(_cr("bash", "-c", f"abricate --db {db} {genome} > {tab}"), log)
    return tab


def abricate_summary(tabs, db, out, log):
    """Presence/absence summary across a batch for one database."""
    summ = os.path.join(out, f"summary_{db}.tsv")
    _tee(_cr("bash", "-c", f"abricate --summary {' '.join(tabs)} > {summ}"), log)
    return summ
