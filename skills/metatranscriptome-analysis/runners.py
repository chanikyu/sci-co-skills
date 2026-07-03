"""runners.py — metatranscriptome front stages (fastp QC -> host removal -> rRNA removal ->
functional/taxonomic profiling), producing a features × samples abundance table for the shared core.
Tools run inside the `scico-metatx` conda env via `conda run`.

UNVERIFIED in-session (needs env + reads + DBs). Standard tool usage; a missing optional DB skips
that stage. rRNA removal (SortMeRNA) is the metatranscriptome-specific step.
"""
import os
import glob
import datetime
import subprocess

ENV = "scico-metatx"


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


def _pairs(d, pat_f="_R1", pat_r="_R2"):
    fwd = sorted(glob.glob(os.path.join(d, f"*{pat_f}*")))
    return [(os.path.basename(f).split(pat_f)[0], f, f.replace(pat_f, pat_r)) for f in fwd]


def _fastp(name, r1, r2, out, log, threads=4):
    o1, o2 = os.path.join(out, f"{name}_R1.fq.gz"), os.path.join(out, f"{name}_R2.fq.gz")
    _tee(_cr("fastp", "-i", r1, "-I", r2, "-o", o1, "-O", o2, "-w", str(threads),
             "-j", os.path.join(out, f"{name}.json"), "-h", os.path.join(out, f"{name}.html")), log)
    return o1, o2


def _host_remove(name, r1, r2, host_index, out, log, threads=4):
    base = os.path.join(out, f"{name}_clean")
    _tee(_cr("bash", "-c", f"bowtie2 -p {threads} -x {host_index} -1 {r1} -2 {r2} "
                           f"--un-conc-gz {base}_%.fq.gz -S /dev/null"), log)
    return f"{base}_1.fq.gz", f"{base}_2.fq.gz"


def _sortmerna(name, r1, r2, rrna_db, out, log, threads=4):
    """Remove rRNA reads; return the non-rRNA (mRNA-enriched) paired reads."""
    wd = os.path.join(out, f"{name}_smr")
    ref = " ".join(f"--ref {r}" for r in rrna_db.split(",")) if rrna_db else ""
    other = os.path.join(out, f"{name}_mRNA")
    _tee(_cr("bash", "-c",
             f"sortmerna {ref} --reads {r1} --reads {r2} --workdir {wd} --fastx --paired_in "
             f"--other {other} --threads {threads} --out2"), log)
    return f"{other}_fwd.fq.gz", f"{other}_rev.fq.gz"


def _metaphlan(name, r1, r2, db, out, log, threads=4):
    prof = os.path.join(out, f"{name}_profile.txt")
    _tee(_cr("metaphlan", f"{r1},{r2}", "--input_type", "fastq", "--nproc", str(threads),
             "--bowtie2db", db, "--bowtie2out", os.path.join(out, f"{name}.bt2.bz2"), "-o", prof), log)
    return prof


def _merge_metaphlan(profiles, out, log):
    merged = os.path.join(out, "metaphlan_merged.txt")
    _tee(_cr("bash", "-c", f"merge_metaphlan_tables.py {' '.join(profiles)} > {merged}"), log)
    import pandas as pd
    df = pd.read_csv(merged, sep="\t", index_col=0)
    sp = df[[("|s__" in i and "|t__" not in i) for i in df.index]]
    sp.index = [i.split("|s__")[-1] for i in sp.index]
    out_csv = os.path.join(out, "abundance_table.csv")
    sp.T.rename_axis("sample_id").to_csv(out_csv)
    return out_csv


def _humann(name, r1, r2, nuc_db, prot_db, out, log, threads=4):
    cat = os.path.join(out, f"{name}.cat.fastq.gz")
    _tee(_cr("bash", "-c", f"cat {r1} {r2} > {cat}"), log)
    _tee(_cr("humann", "--input", cat, "--output", out, "--threads", str(threads),
             "--nucleotide-database", nuc_db, "--protein-database", prot_db), log)
    return os.path.join(out, f"{name}.cat_pathabundance.tsv")


def run(input_dir, out_dir, profiler="humann", host_index=None, rrna_db=None,
        metaphlan_db=None, humann_nuc_db=None, humann_prot_db=None, threads=4, logf=None):
    """FASTQ dir -> features × samples abundance_table.csv (path). rRNA removal always attempted."""
    os.makedirs(out_dir, exist_ok=True)
    logf = logf or os.path.join(out_dir, "frontstages.log")
    qc = os.path.join(out_dir, "qc"); prof_dir = os.path.join(out_dir, "profiles")
    os.makedirs(qc, exist_ok=True); os.makedirs(prof_dir, exist_ok=True)

    profiles, humann_tables = [], []
    for name, r1, r2 in _pairs(input_dir):
        r1, r2 = _fastp(name, r1, r2, qc, logf, threads)
        if host_index:
            r1, r2 = _host_remove(name, r1, r2, host_index, qc, logf, threads)
        r1, r2 = _sortmerna(name, r1, r2, rrna_db, qc, logf, threads)     # rRNA removal
        if profiler == "metaphlan":
            profiles.append(_metaphlan(name, r1, r2, metaphlan_db, prof_dir, logf, threads))
        elif profiler == "humann":
            humann_tables.append(_humann(name, r1, r2, humann_nuc_db, humann_prot_db, prof_dir, logf, threads))
        else:
            raise ValueError(f"unknown profiler '{profiler}' (humann | metaphlan)")

    if profiler == "metaphlan":
        return _merge_metaphlan(profiles, out_dir, logf)
    # HUMAnN: join per-sample pathabundance into features × samples
    import pandas as pd
    cols = {}
    for t in humann_tables:
        s = pd.read_csv(t, sep="\t", index_col=0).iloc[:, 0]
        cols[os.path.basename(t).split(".cat")[0]] = s
    tab = pd.DataFrame(cols)
    out_csv = os.path.join(out_dir, "abundance_table.csv")
    tab.rename_axis("feature").T.rename_axis("sample_id").to_csv(out_csv)
    return out_csv
