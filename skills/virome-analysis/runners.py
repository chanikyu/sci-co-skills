"""runners.py — virome external-tool runners (contigs -> viral genomes -> vOTU abundance). Tools run
in the `scico-virome` conda env via `conda run`.

UNVERIFIED in-session (needs contigs + large DBs: geNomad ~1.4 GB, CheckV ~10 GB, iPHoP ~40 GB).
Standard commands; dereplication + abundance assembly are done in Python (derep.py / abundance.py).
"""
import os
import glob
import shlex
import datetime
import subprocess

ENV = "scico-virome"


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


def genomad(contigs, out_dir, db, log, min_score=0.7):
    """Viral contig identification + taxonomy (geNomad end-to-end). Returns the viral contigs FASTA."""
    os.makedirs(out_dir, exist_ok=True)
    _tee(_cr("genomad", "end-to-end", "--cleanup", "--min-score", str(min_score),
             contigs, out_dir, db), log)
    hit = glob.glob(os.path.join(out_dir, "**", "*_virus.fna"), recursive=True)
    if not hit:
        raise RuntimeError(f"geNomad produced no virus FASTA under {out_dir}")
    return sorted(hit)[0]


def checkv(viral_fasta, out_dir, db, log):
    """QC: completeness / contamination + provirus excision (CheckV). Returns the cleaned viral FASTA
    (proviruses + viruses) and the quality_summary.tsv path."""
    os.makedirs(out_dir, exist_ok=True)
    _tee(_cr("checkv", "end_to_end", viral_fasta, out_dir, "-d", db), log)
    combined = os.path.join(out_dir, "viruses_and_proviruses.fna")
    q = shlex.quote
    _tee(_cr("bash", "-c",                              # proviruses.fna is often absent (normal) — skip missing
             f"for f in {q(out_dir + '/viruses.fna')} {q(out_dir + '/proviruses.fna')}; do "
             f'[ -s "$f" ] && cat "$f"; done > {q(combined)}'), log)
    return combined, os.path.join(out_dir, "quality_summary.tsv")


def ani_table(fasta, out_dir, log):
    """All-vs-all ANI/AF for dereplication (megablast + CheckV anicalc). Returns the ANI TSV
    (columns: query, target, ani, af) consumed by derep.cluster_votus."""
    os.makedirs(out_dir, exist_ok=True)
    db = os.path.join(out_dir, "db")
    _tee(_cr("makeblastdb", "-in", fasta, "-dbtype", "nucl", "-out", db), log)
    bl = os.path.join(out_dir, "blast.tsv")
    q = shlex.quote
    _tee(_cr("bash", "-c",
             f"blastn -query {q(fasta)} -db {q(db)} -outfmt '6 std qlen slen' -max_target_seqs 10000 "
             f"-perc_identity 90 -out {q(bl)}"), log)
    ani = os.path.join(out_dir, "ani.tsv")
    _tee(_cr("bash", "-c", f"anicalc.py -i {q(bl)} -o {q(ani)}"), log)   # CheckV helper (query,target,ani,qcov,tcov)
    return ani


def map_coverm(votu_fasta, reads_dir, out_dir, log, threads=4):
    """Map reads back to the vOTU set (CoverM). Returns {sample: per-vOTU coverage TSV} with rpkm +
    covered_fraction, consumed by abundance.build_table."""
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "coverm.tsv")
    _tee(_cr("coverm", "contig", "--reference", votu_fasta, "--coupled",
             *sorted(glob.glob(os.path.join(reads_dir, "*"))), "--methods", "rpkm", "covered_fraction",
             "--threads", str(threads), "--output-file", out), log)
    return out
