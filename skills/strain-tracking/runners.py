"""runners.py — strain-tracking profilers (reads -> per-species cross-sample strain distance/identity
matrices). External tools run in the `scico-straintrack` conda env via `conda run`.

UNVERIFIED in-session (needs many samples' reads + DBs: MetaPhlAn markers ~15 GB; inStrain needs a
genome/MAG Bowtie2 index). StrainPhlAn -> normalized nucleotide/phylogenetic DISTANCE per species;
inStrain compare -> popANI IDENTITY per species (same strain at popANI >= 99.999%).
"""
import os
import glob
import shlex
import datetime
import subprocess
import pandas as pd

ENV = "scico-straintrack"


def _tee(cmd, logf, timeout=None):
    with open(logf, "a") as fh:
        fh.write(f"[{datetime.datetime.now():%H:%M:%S}] $ {' '.join(cmd)}\n")
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"command timed out after {timeout}s (see {logf})")
    with open(logf, "a") as fh:
        fh.write(p.stdout + p.stderr + f"[exit {p.returncode}]\n")
    if p.returncode != 0:
        raise RuntimeError(f"command failed (see {logf}): {' '.join(cmd)}")
    return p


def _cr(*args):
    return ["conda", "run", "-n", ENV, *args]


def _pairs(d, pat_f="_R1", pat_r="_R2"):
    out = []
    for f in sorted(glob.glob(os.path.join(d, f"*{pat_f}*"))):
        b = os.path.basename(f)
        out.append((b.split(pat_f)[0], f, os.path.join(os.path.dirname(f), b.replace(pat_f, pat_r, 1))))
    return out


def strainphlan_profile(reads_dir, out_dir, log, threads=4):
    """MetaPhlAn (consensus markers) per sample -> sample2markers -> strainphlan per species -> per-species
    normalized distance matrices. Returns {species: distance DataFrame} (metric='distance')."""
    os.makedirs(out_dir, exist_ok=True)
    cons = os.path.join(out_dir, "consensus"); os.makedirs(cons, exist_ok=True)
    for name, r1, r2 in _pairs(reads_dir):
        sam = os.path.join(out_dir, f"{name}.sam.bz2")
        _tee(_cr("metaphlan", f"{r1},{r2}", "--input_type", "fastq", "-s", sam,
                 "--bowtie2out", os.path.join(out_dir, f"{name}.bt2.bz2"),
                 "-o", os.path.join(out_dir, f"{name}_profile.tsv"), "--nproc", str(threads)), log)
        _tee(_cr("sample2markers.py", "-i", sam, "-o", cons, "-n", str(threads)), log)
    # per detected species: strainphlan builds a tree; distances parsed from its output .info / RAxML tree.
    # (scaffold) return {species: DataFrame}. Wired in pipeline; parsing is per-species below.
    return _parse_strainphlan(out_dir), "distance"


def instrain_profile(reads_dir, genomes_fasta, out_dir, log, threads=4):
    """Bowtie2-map each sample to a genome/MAG set, inStrain profile, then inStrain compare -> popANI.
    Returns {species/genome: popANI IDENTITY DataFrame} (metric='identity', threshold 99.999)."""
    os.makedirs(out_dir, exist_ok=True)
    idx = os.path.join(out_dir, "ref")
    _tee(_cr("bowtie2-build", "--threads", str(threads), genomes_fasta, idx), log)
    profiles = []
    for name, r1, r2 in _pairs(reads_dir):
        bam = os.path.join(out_dir, f"{name}.bam")
        _tee(_cr("bash", "-c",
                 f"bowtie2 -p {threads} -x {shlex.quote(idx)} -1 {shlex.quote(r1)} -2 {shlex.quote(r2)} "
                 f"| samtools sort -@ {threads} -o {shlex.quote(bam)}"), log)
        prof = os.path.join(out_dir, f"{name}.IS")
        _tee(_cr("inStrain", "profile", bam, genomes_fasta, "-o", prof, "-p", str(threads)), log)
        profiles.append(prof)
    _tee(_cr("inStrain", "compare", "-i", *profiles, "-o", os.path.join(out_dir, "compare"),
             "-p", str(threads)), log)
    return _parse_instrain(os.path.join(out_dir, "compare")), "identity"


def _parse_strainphlan(out_dir):
    """StrainPhlAn 4 emits per-species trees/alignments, NOT a distance matrix directly — the
    tree -> normalized-genetic-distance (nGD) step is NOT wired here. Pre-computed per-species nGD
    matrices dropped as *_nGD.tsv in out_dir are loaded; otherwise this raises loudly (not a silent {})."""
    mats = {}
    for f in glob.glob(os.path.join(out_dir, "*_nGD.tsv")):
        mats[os.path.basename(f).split(".")[0]] = pd.read_csv(f, sep="\t", index_col=0)
    if not mats:
        raise NotImplementedError(
            "StrainPhlAn produced trees but the tree -> nGD distance step is not wired. Provide per-species "
            "*_nGD.tsv matrices in the profile dir, or use engine='instrain'.")
    return mats


def _parse_instrain(compare_dir, min_breadth=0.5):
    """inStrain compare genomeWide_compare.tsv -> per-genome popANI IDENTITY matrix (percent). popANI is
    MASKED to NaN (undetermined) where percent_genome_compared < min_breadth, so low-breadth pairs are
    NOT called 'same strain' (inStrain's default breadth gate). Concatenates all compare tables found."""
    tsv = glob.glob(os.path.join(compare_dir, "**", "*genomeWide_compare.tsv"), recursive=True)
    if not tsv:
        raise RuntimeError(f"no *genomeWide_compare.tsv under {compare_dir} — did `inStrain compare` finish?")
    df = pd.concat([pd.read_csv(f, sep="\t") for f in tsv], ignore_index=True)
    if "percent_genome_compared" in df.columns:
        df.loc[df["percent_genome_compared"] < min_breadth, "popANI"] = float("nan")   # breadth gate
    mats = {}
    for g, sub in df.groupby("genome"):
        piv = sub.pivot_table(index="name1", columns="name2", values="popANI", aggfunc="mean")
        ids = sorted(set(piv.index) | set(piv.columns))
        m = piv.reindex(index=ids, columns=ids)
        m = (m.combine_first(m.T)) * 100.0                     # symmetric, popANI as percent
        for i in ids:
            m.loc[i, i] = 100.0
        mats[str(g)] = m
    return mats


def detect_strains(reads_dir, out_dir, engine="strainphlan", genomes_fasta=None, log=None):
    """Dispatch to the chosen profiler. Returns ({species: matrix}, metric)."""
    log = log or os.path.join(out_dir, "profile.log")
    if engine == "strainphlan":
        return strainphlan_profile(reads_dir, out_dir, log)
    if engine == "instrain":
        if not genomes_fasta:
            raise ValueError("engine='instrain' needs genomes_fasta (a genome/MAG set to map to).")
        return instrain_profile(reads_dir, genomes_fasta, out_dir, log)
    raise NotImplementedError(f"engine '{engine}' not wired — use 'strainphlan' or 'instrain'.")
