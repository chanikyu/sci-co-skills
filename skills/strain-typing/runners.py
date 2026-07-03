"""
runners.py — strain-typing runners (MLST, serotyping, cgMLST). Tools run inside the
`scico-typing` conda env via `conda run`.

UNVERIFIED in-session (needs env + assemblies [+ a cgMLST scheme]). Standard tool usage.
"""
import os
import glob
import datetime
import subprocess

ENV = "scico-typing"
_FA = (".fasta", ".fa", ".fna", ".fasta.gz", ".fa.gz", ".fna.gz")


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
    """A single FASTA -> [path]; a directory -> every FASTA in it."""
    if os.path.isdir(path):
        gs = sorted(f for f in glob.glob(os.path.join(path, "*")) if f.lower().endswith(_FA))
        if not gs:
            raise ValueError(f"no FASTA genomes in {path}")
        return gs
    return [path]


def mlst(gs, out, log):
    """Run mlst on all genomes at once -> tables/mlst.tsv."""
    os.makedirs(out, exist_ok=True)
    tsv = os.path.join(out, "mlst.tsv")
    _tee(_cr("bash", "-c", f"mlst {' '.join(gs)} > {tsv}"), log)
    return tsv


def serotype(genome, out, tool, log, threads=4):
    """Organism-specific serotyping. tool = sistr (Salmonella) | ectyper (E. coli)."""
    os.makedirs(out, exist_ok=True)
    name = os.path.splitext(os.path.basename(genome))[0]
    if tool == "sistr":
        _tee(_cr("sistr", "-i", genome, name, "-f", "tab",
                 "-o", os.path.join(out, f"{name}.sistr"), "-t", str(threads)), log)
        return os.path.join(out, f"{name}.sistr.tab")
    if tool == "ectyper":
        _tee(_cr("ectyper", "-i", genome, "-o", os.path.join(out, name), "-c", str(threads)), log)
        return os.path.join(out, name)
    raise ValueError(f"unknown serotyper '{tool}' (sistr | ectyper)")


def cgmlst(gs_dir, out, scheme, log, threads=4):
    """chewBBACA allele calling against a user-provided scheme dir."""
    _tee(_cr("chewBBACA.py", "AlleleCall", "-i", gs_dir, "-g", scheme,
             "-o", os.path.join(out, "cgmlst"), "--cpu", str(threads)), log)
    return os.path.join(out, "cgmlst")
