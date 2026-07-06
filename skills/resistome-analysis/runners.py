"""runners.py — resistome ARG-detection runners (reads -> ARG READ COUNTS). External tools run in the
`scico-resistome` conda env via `conda run`.

UNVERIFIED in-session (needs reads + DBs; DeepARG models are bundled, RGI needs CARD ~200 MB).
Design notes (from review): ARG **read counts** come from each tool's NATIVE output (DeepARG
`.mapping.ARG`, RGI `gene_mapping_data`), the **library size** (total reads) from `seqkit stats` — NOT
summed from the ARG table. hAMRonization harmonizes DETECTIONS and is used only for the drug-class map.
"""
import os
import glob
import shlex
import datetime
import subprocess
import pandas as pd

ENV = "scico-resistome"


def _tee(cmd, logf, shell=False, timeout=None):
    with open(logf, "a") as fh:
        fh.write(f"[{datetime.datetime.now():%H:%M:%S}] $ {cmd if shell else ' '.join(cmd)}\n")
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, shell=shell, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"command timed out after {timeout}s (see {logf}): {cmd}")
    with open(logf, "a") as fh:
        fh.write(p.stdout + p.stderr + f"[exit {p.returncode}]\n")
    if p.returncode != 0:
        raise RuntimeError(f"command failed (see {logf}): {cmd}")
    return p


def _cr(*args):
    return ["conda", "run", "-n", ENV, *args]


def _pairs(d, pat_f="_R1", pat_r="_R2"):
    out = []
    for f in sorted(glob.glob(os.path.join(d, f"*{pat_f}*"))):
        b = os.path.basename(f)
        r2 = os.path.join(os.path.dirname(f), b.replace(pat_f, pat_r, 1))   # replace in filename only
        out.append((b.split(pat_f)[0], f, r2))
    return out


def _lib_size(r1, r2, log):
    """Total read count (library size) for RPKM's depth denominator — via seqkit stats (NOT the ARG table)."""
    p = _tee(_cr("bash", "-c", f"seqkit stats -T {shlex.quote(r1)} {shlex.quote(r2)}"), log)
    rows = [ln.split("\t") for ln in p.stdout.strip().splitlines()[1:]]
    return int(sum(int(r[3].replace(",", "")) for r in rows if len(r) > 3))   # num_seqs column


def deeparg(name, r1, r2, out_dir, log):
    os.makedirs(out_dir, exist_ok=True)
    pref = os.path.join(out_dir, name)
    _tee(_cr("deeparg", "short_reads_pipeline", "--forward_pe_file", r1, "--reverse_pe_file", r2,
             "--output_file", pref), log)
    out = pref + ".mapping.ARG"
    if not os.path.exists(out):
        raise RuntimeError(f"DeepARG produced no ARG mapping for {name} ({out})")
    return out


def rgi_bwt(name, r1, r2, out_dir, card_db, log):
    os.makedirs(out_dir, exist_ok=True)
    if card_db:
        _tee(_cr("rgi", "load", "--card_json", card_db, "--local"), log)   # honor the requested CARD DB
    pref = os.path.join(out_dir, name)
    _tee(_cr("rgi", "bwt", "-1", r1, "-2", r2, "-o", pref, "--local"), log)
    out = pref + ".gene_mapping_data.txt"
    if not os.path.exists(out):
        raise RuntimeError(f"RGI bwt produced no gene mapping for {name} ({out})")
    return out


def _parse_counts(report, engine):
    """ARG read counts + gene lengths from a tool's NATIVE output. Returns (Series ARG->reads, {ARG: bp})."""
    df = pd.read_csv(report, sep="\t")
    if engine == "deeparg":
        gene = "#ARG" if "#ARG" in df.columns else "best-hit"
        cnt = "counts" if "counts" in df.columns else df.columns[-1]
        length = "length" if "length" in df.columns else None
    else:                                                    # RGI gene_mapping_data
        gene = "ARO Term" if "ARO Term" in df.columns else df.columns[0]
        cnt = next((c for c in df.columns if "Mapped Reads" in c), df.columns[-1])
        length = "Reference Length" if "Reference Length" in df.columns else None
    counts = df.groupby(gene)[cnt].sum()
    lengths = df.groupby(gene)[length].median().to_dict() if length else {}
    return counts, lengths


def detect_args(reads_dir, out_dir, engine="deeparg", card_db=None, log=None):
    """Run the chosen ARG detector per sample → ARG × samples read counts + gene lengths + library sizes;
    hAMRonize the detections to derive a drug-class map. Returns (counts, gene_lengths, total_reads, arg_to_class)."""
    if engine == "amrplusplus":
        raise NotImplementedError("AMR++/MEGARes engine is not yet wired — use engine='deeparg' or 'rgi'.")
    os.makedirs(out_dir, exist_ok=True)
    log = log or os.path.join(out_dir, "detect.log")
    per, gene_lengths, total_reads, reports = {}, {}, {}, []
    for name, r1, r2 in _pairs(reads_dir):
        rep = deeparg(name, r1, r2, out_dir, log) if engine == "deeparg" \
            else rgi_bwt(name, r1, r2, out_dir, card_db, log)
        s, gl = _parse_counts(rep, engine)
        per[name] = s; gene_lengths.update(gl); total_reads[name] = _lib_size(r1, r2, log)
        reports.append(rep)
    counts = pd.DataFrame(per).fillna(0.0)                   # ARG × samples read counts
    arg_to_class = _drug_class_map(reports, out_dir, log)
    return counts, gene_lengths, total_reads, arg_to_class


def _drug_class_map(reports, out_dir, log):
    """Derive {ARG: drug_class} from hAMRonization's harmonized table (its drug_class / ARO field)."""
    harm = os.path.join(out_dir, "harmonized.tsv")
    _tee(_cr("hamronize", "summarize", "-t", "tsv", "-o", harm, *reports), log)
    h = pd.read_csv(harm, sep="\t")
    if "gene_symbol" not in h.columns:
        raise ValueError(f"hAMRonization output missing 'gene_symbol' (got {list(h.columns)})")
    if "drug_class" not in h.columns:
        return {}
    return h.dropna(subset=["drug_class"]).groupby("gene_symbol")["drug_class"].first().to_dict()
