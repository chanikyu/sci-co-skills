"""runners.py — transcriptome front-stage runners (fastp QC + quantification to a gene count matrix).
Tools run inside the `scico-transcriptome` conda env via `conda run`.

UNVERIFIED in-session (needs env + reads + a reference index). Standard salmon/kallisto/STAR usage;
the caller (pipeline) picks fastp thresholds from the read-quality profile.
"""
import os
import glob
import datetime
import subprocess
import pandas as pd

ENV = "scico-transcriptome"


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


def fastp(name, r1, r2, out, log, threads=4):
    os.makedirs(out, exist_ok=True)
    o1, o2 = os.path.join(out, f"{name}_R1.fq.gz"), os.path.join(out, f"{name}_R2.fq.gz")
    _tee(_cr("fastp", "-i", r1, "-I", r2, "-o", o1, "-O", o2, "-w", str(threads),
             "-j", os.path.join(out, f"{name}.json"), "-h", os.path.join(out, f"{name}.html")), log)
    return o1, o2


def _tx2gene(counts_by_tx, tx2gene_path):
    m = pd.read_csv(tx2gene_path, sep=None, engine="python", header=None, index_col=0).iloc[:, 0]
    df = counts_by_tx.copy()
    df["gene"] = df.index.map(m)
    return df.groupby("gene").sum()


def quantify(input_dir, out_dir, aligner, index, tx2gene, gtf, log, threads=4):
    """QC + quantify all sample pairs -> a gene × samples count matrix CSV (path)."""
    os.makedirs(out_dir, exist_ok=True)
    qc = os.path.join(out_dir, "qc"); os.makedirs(qc, exist_ok=True)
    per_sample = {}
    for name, r1, r2 in _pairs(input_dir):
        t1, t2 = fastp(name, r1, r2, qc, log, threads)
        sdir = os.path.join(out_dir, "quant", name); os.makedirs(sdir, exist_ok=True)
        if aligner == "salmon":
            _tee(_cr("salmon", "quant", "-i", index, "-l", "A", "-1", t1, "-2", t2,
                     "-p", str(threads), "-o", sdir), log)
            q = pd.read_csv(os.path.join(sdir, "quant.sf"), sep="\t", index_col=0)["NumReads"]
        elif aligner == "kallisto":
            _tee(_cr("kallisto", "quant", "-i", index, "-o", sdir, "-t", str(threads), t1, t2), log)
            q = pd.read_csv(os.path.join(sdir, "abundance.tsv"), sep="\t", index_col=0)["est_counts"]
        elif aligner == "star":
            _tee(_cr("bash", "-c",
                     f"STAR --genomeDir {index} --sjdbGTFfile {gtf} --readFilesIn {t1} {t2} "
                     f"--readFilesCommand zcat --runThreadN {threads} --outSAMtype BAM SortedByCoordinate "
                     f"--outFileNamePrefix {sdir}/"), log)
            per_sample[name] = os.path.join(sdir, "Aligned.sortedByCoord.out.bam")
            continue
        else:
            raise ValueError(f"unknown aligner '{aligner}' (salmon | kallisto | star)")
        per_sample[name] = q

    if aligner == "star":                              # featureCounts across all BAMs
        bams = [per_sample[n] for n in per_sample]
        fc = os.path.join(out_dir, "featurecounts.txt")
        _tee(_cr("featureCounts", "-a", gtf, "-o", fc, "-T", str(threads), "-p", *bams), log)
        cnt = pd.read_csv(fc, sep="\t", comment="#", index_col=0).iloc[:, 5:]
        cnt.columns = list(per_sample.keys())
        counts = cnt
    else:
        tx = pd.DataFrame(per_sample)                  # transcripts × samples
        counts = _tx2gene(tx, tx2gene) if tx2gene else tx

    out_csv = os.path.join(out_dir, "gene_counts.csv")
    counts.round().astype(int).to_csv(out_csv)
    return out_csv
