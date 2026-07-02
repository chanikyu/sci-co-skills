"""
stage0.py — amplicon Stage 0: paired FASTQ -> ASV feature table (DADA2), with ITS primer
removal via cutadapt. Runs tools inside the `scico-amplicon` conda env.

UNVERIFIED in-session (needs env + reads + DB). Standard DADA2/cutadapt usage; the caller
(pipeline) should pick truncLen/maxEE from the read-quality profile per SKILL.md.
"""
import os
import glob
import datetime
import subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))
ENV = "scico-amplicon"


def _tee(cmd, logf):
    with open(logf, "a") as fh:
        fh.write(f"[{datetime.datetime.now():%H:%M:%S}] $ {' '.join(cmd)}\n")
    p = subprocess.run(cmd, capture_output=True, text=True)
    with open(logf, "a") as fh:
        fh.write(p.stdout + p.stderr + f"[exit {p.returncode}]\n")
    if p.returncode != 0:
        raise RuntimeError(f"command failed (see {logf}): {' '.join(cmd)}")


def _pairs(d, pat_f="_R1", pat_r="_R2"):
    fwd = sorted(glob.glob(os.path.join(d, f"*{pat_f}*")))
    return [(os.path.basename(f).split(pat_f)[0], f, f.replace(pat_f, pat_r)) for f in fwd]


def _cutadapt_primers(input_dir, out_dir, fwd_primer, rev_primer, logf):
    """Remove primers (ITS) with cutadapt, per read pair. Returns the trimmed dir."""
    trimmed = os.path.join(out_dir, "primer_trimmed")
    os.makedirs(trimmed, exist_ok=True)
    for name, r1, r2 in _pairs(input_dir):
        o1 = os.path.join(trimmed, os.path.basename(r1))
        o2 = os.path.join(trimmed, os.path.basename(r2))
        _tee(["conda", "run", "-n", ENV, "cutadapt", "-g", fwd_primer, "-G", rev_primer,
              "--discard-untrimmed", "-o", o1, "-p", o2, r1, r2], logf)
    return trimmed


def run(input_dir, out_dir, marker="16S", fwd_primer=None, rev_primer=None,
        trunc_f=0, trunc_r=0, maxee_f=2.0, maxee_r=2.0, tax_db=None, threads=1, logf=None):
    """FASTQ dir -> feature_table.csv (path returned). ITS: primers trimmed first, no truncLen."""
    os.makedirs(out_dir, exist_ok=True)
    logf = logf or os.path.join(out_dir, "stage0.log")
    reads = input_dir
    if marker.upper() == "ITS":
        if fwd_primer and rev_primer:
            reads = _cutadapt_primers(input_dir, out_dir, fwd_primer, rev_primer, logf)
        trunc_f = trunc_r = 0            # ITS reads are variable length — never truncate

    dada_out = os.path.join(out_dir, "dada2")
    cmd = ["conda", "run", "-n", ENV, "Rscript", os.path.join(_HERE, "run_dada2.R"),
           "--input_dir", reads, "--out_dir", dada_out,
           "--trunc_f", str(trunc_f), "--trunc_r", str(trunc_r),
           "--maxee_f", str(maxee_f), "--maxee_r", str(maxee_r), "--threads", str(threads)]
    if tax_db:
        cmd += ["--tax_db", tax_db]
    _tee(cmd, logf)
    return os.path.join(dada_out, "feature_table.csv")
