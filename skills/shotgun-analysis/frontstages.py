"""
frontstages.py — shotgun Stage 0-2 runners (fastp QC -> host removal -> taxonomic profiling
-> optional HUMAnN), producing a samples × features abundance table for the shared core.
Tools run inside the `scico-shotgun` conda env via `conda run`.

UNVERIFIED in-session (needs env + reads + DBs). Standard tool usage; the caller should pick
per-tool options from the data (SKILL.md). DBs are user-provided paths; a missing optional DB
skips that stage.
"""
import os
import glob
import datetime
import subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))
ENV = "scico-shotgun"


def _tee(cmd, logf, shell=False):
    with open(logf, "a") as fh:
        fh.write(f"[{datetime.datetime.now():%H:%M:%S}] $ {cmd if shell else ' '.join(cmd)}\n")
    p = subprocess.run(cmd, capture_output=True, text=True, shell=shell)
    with open(logf, "a") as fh:
        fh.write(p.stdout + p.stderr + f"[exit {p.returncode}]\n")
    if p.returncode != 0:
        raise RuntimeError(f"command failed (see {logf}): {cmd}")


def _pairs(d, pat_f="_R1", pat_r="_R2"):
    fwd = sorted(glob.glob(os.path.join(d, f"*{pat_f}*")))
    return [(os.path.basename(f).split(pat_f)[0], f, f.replace(pat_f, pat_r)) for f in fwd]


def _cr(*args):
    return ["conda", "run", "-n", ENV, *args]


def _fastp(name, r1, r2, out, log, threads=4):
    o1, o2 = os.path.join(out, f"{name}_R1.fq.gz"), os.path.join(out, f"{name}_R2.fq.gz")
    _tee(_cr("fastp", "-i", r1, "-I", r2, "-o", o1, "-O", o2, "-w", str(threads),
             "-j", os.path.join(out, f"{name}.json"), "-h", os.path.join(out, f"{name}.html")), log)
    return o1, o2


def _host_remove(name, r1, r2, host_index, out, log, threads=4):
    base = os.path.join(out, f"{name}_clean")
    _tee(_cr("bash", "-c",
             f"bowtie2 -p {threads} -x {host_index} -1 {r1} -2 {r2} "
             f"--un-conc-gz {base}_%.fq.gz -S /dev/null"), log)
    return f"{base}_1.fq.gz", f"{base}_2.fq.gz"


def _metaphlan(name, r1, r2, db, out, log, threads=4):
    prof = os.path.join(out, f"{name}_profile.txt")
    _tee(_cr("metaphlan", f"{r1},{r2}", "--input_type", "fastq", "--nproc", str(threads),
             "--bowtie2db", db, "--bowtie2out", os.path.join(out, f"{name}.bt2.bz2"),
             "-o", prof), log)
    return prof


def _merge_metaphlan(profiles, out, log):
    merged = os.path.join(out, "metaphlan_merged.txt")
    _tee(_cr("bash", "-c", f"merge_metaphlan_tables.py {' '.join(profiles)} > {merged}"), log)
    return _metaphlan_to_table(merged, os.path.join(out, "abundance_table.csv"))


def _metaphlan_to_table(merged, out_csv):
    """species × samples relative abundance -> samples × species CSV."""
    import pandas as pd
    df = pd.read_csv(merged, sep="\t", skiprows=0, index_col=0)
    sp = df[[("|s__" in i and "|t__" not in i) for i in df.index]]
    sp.index = [i.split("|s__")[-1] for i in sp.index]
    sp.T.rename_axis("sample_id").to_csv(out_csv)
    return out_csv


def _kraken2_bracken(name, r1, r2, db, out, log, readlen=150, threads=4):
    rep = os.path.join(out, f"{name}.kreport")
    _tee(_cr("kraken2", "--db", db, "--paired", r1, r2, "--threads", str(threads),
             "--report", rep, "--output", os.path.join(out, f"{name}.kraken")), log)
    brk = os.path.join(out, f"{name}.bracken")
    _tee(_cr("bracken", "-d", db, "-i", rep, "-o", brk, "-r", str(readlen), "-l", "S"), log)
    return brk


def _combine_bracken(brackens, out, log):
    combined = os.path.join(out, "bracken_combined.txt")
    _tee(_cr("bash", "-c",
             f"combine_bracken_outputs.py --files {' '.join(brackens)} -o {combined}"), log)
    import pandas as pd
    df = pd.read_csv(combined, sep="\t")
    frac = [c for c in df.columns if c.endswith("_frac")]
    tab = df.set_index("name")[frac]
    tab.columns = [c[:-5] for c in frac]
    out_csv = os.path.join(out, "abundance_table.csv")
    tab.T.rename_axis("sample_id").to_csv(out_csv)
    return out_csv


def _humann(name, r1, r2, nuc_db, prot_db, out, log, threads=4):
    cat = os.path.join(out, f"{name}.cat.fastq.gz")
    _tee(_cr("bash", "-c", f"cat {r1} {r2} > {cat}"), log)
    _tee(_cr("humann", "--input", cat, "--output", out, "--threads", str(threads),
             "--nucleotide-database", nuc_db, "--protein-database", prot_db), log)
    return os.path.join(out, f"{name}.cat_pathabundance.tsv")


def run(input_dir, out_dir, profiler="metaphlan", host_index=None,
        metaphlan_db=None, kraken_db=None, readlen=150,
        humann_nuc_db=None, humann_prot_db=None, threads=4, logf=None):
    """FASTQ dir -> abundance_table.csv (path). Optional host removal + HUMAnN."""
    os.makedirs(out_dir, exist_ok=True)
    logf = logf or os.path.join(out_dir, "frontstages.log")
    qc = os.path.join(out_dir, "qc"); prof_dir = os.path.join(out_dir, "profiles")
    os.makedirs(qc, exist_ok=True); os.makedirs(prof_dir, exist_ok=True)

    profiles = []
    for name, r1, r2 in _pairs(input_dir):
        r1, r2 = _fastp(name, r1, r2, qc, logf, threads)
        if host_index:
            r1, r2 = _host_remove(name, r1, r2, host_index, qc, logf, threads)
        if profiler == "metaphlan":
            profiles.append(_metaphlan(name, r1, r2, metaphlan_db, prof_dir, logf, threads))
        elif profiler == "kraken2":
            profiles.append(_kraken2_bracken(name, r1, r2, kraken_db, prof_dir, logf, readlen, threads))
        else:
            raise ValueError(f"unknown profiler '{profiler}' (metaphlan | kraken2)")
        if humann_nuc_db and humann_prot_db:
            _humann(name, r1, r2, humann_nuc_db, humann_prot_db, prof_dir, logf, threads)

    if profiler == "metaphlan":
        return _merge_metaphlan(profiles, out_dir, logf)
    return _combine_bracken(profiles, out_dir, logf)
