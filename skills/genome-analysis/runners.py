"""
runners.py — genome-analysis stage runners (fastp QC, assembly, QUAST, CheckM2, annotation,
species ID). Tools run inside the `scico-genome` conda env via `conda run`.

UNVERIFIED in-session (needs env + reads/assembly + DBs). Standard tool usage; the caller
should pick options from the data (SKILL.md). A missing optional DB skips that stage.
"""
import os
import glob
import shutil
import datetime
import subprocess

ENV = "scico-genome"


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


def _pair(reads_dir, pat_f="_R1", pat_r="_R2"):
    """Return (r1, r2) for the single isolate's paired reads in reads_dir."""
    fwd = sorted(glob.glob(os.path.join(reads_dir, f"*{pat_f}*")))
    if not fwd:
        raise ValueError(f"no *{pat_f}* reads in {reads_dir}")
    return fwd[0], fwd[0].replace(pat_f, pat_r)


def fastp(r1, r2, out, log, threads=4):
    os.makedirs(out, exist_ok=True)
    o1, o2 = os.path.join(out, "trim_R1.fq.gz"), os.path.join(out, "trim_R2.fq.gz")
    _tee(_cr("fastp", "-i", r1, "-I", r2, "-o", o1, "-O", o2, "-w", str(threads),
             "-j", os.path.join(out, "fastp.json"), "-h", os.path.join(out, "fastp.html")), log)
    return o1, o2


# representative bacterial assemblers, by read type
SHORT_ASSEMBLERS = ("spades", "unicycler", "shovill", "skesa")   # Illumina, reads=(r1, r2)
LONG_ASSEMBLERS = ("flye", "canu", "raven")                       # ONT/PacBio, reads=long-read file


def assemble(reads, out, assembler, log, threads=8, long_reads=None):
    """Short-read assemblers take reads=(r1, r2); long-read take a single long-read file.
    Unicycler with `long_reads` set runs in HYBRID mode. Returns the contigs FASTA path."""
    os.makedirs(out, exist_ok=True)

    if assembler == "spades":
        r1, r2 = reads
        _tee(_cr("spades.py", "--isolate", "-1", r1, "-2", r2, "-o", out, "-t", str(threads)), log)
        return os.path.join(out, "contigs.fasta")
    if assembler == "unicycler":
        r1, r2 = reads
        cmd = _cr("unicycler", "-1", r1, "-2", r2, "-o", out, "-t", str(threads))
        if long_reads:                         # hybrid: short + long
            cmd += ["-l", long_reads]
        _tee(cmd, log)
        return os.path.join(out, "assembly.fasta")
    if assembler == "shovill":
        r1, r2 = reads
        _tee(_cr("shovill", "--R1", r1, "--R2", r2, "--outdir", out,
                 "--cpus", str(threads), "--force"), log)
        return os.path.join(out, "contigs.fa")
    if assembler == "skesa":
        r1, r2 = reads
        _tee(_cr("skesa", "--reads", f"{r1},{r2}", "--cores", str(threads),
                 "--contigs_out", os.path.join(out, "contigs.fasta")), log)
        return os.path.join(out, "contigs.fasta")

    lr = reads if isinstance(reads, str) else reads[0]
    if assembler == "flye":
        _tee(_cr("flye", "--nano-raw", lr, "-o", out, "-t", str(threads)), log)
        return os.path.join(out, "assembly.fasta")
    if assembler == "canu":
        _tee(_cr("canu", "-p", "asm", "-d", out, "genomeSize=5m", "-nanopore", lr,
                 "useGrid=false", f"maxThreads={threads}"), log)
        return os.path.join(out, "asm.contigs.fasta")
    if assembler == "raven":
        _tee(_cr("bash", "-c", f"raven -t {threads} {lr} > {os.path.join(out, 'raven.fasta')}"), log)
        return os.path.join(out, "raven.fasta")
    raise ValueError(f"unknown assembler '{assembler}' "
                     f"(short: {SHORT_ASSEMBLERS}; long: {LONG_ASSEMBLERS})")


def quast(contigs, out, log, threads=4):
    _tee(_cr("quast.py", contigs, "-o", out, "-t", str(threads)), log)
    return os.path.join(out, "report.tsv")


def checkm2(contigs, out, db, log, threads=4):
    """CheckM2 works on a directory of genomes — stage the contigs into one."""
    gdir = os.path.join(out, "genomes")
    os.makedirs(gdir, exist_ok=True)
    shutil.copy(contigs, os.path.join(gdir, "genome.fasta"))
    _tee(_cr("checkm2", "predict", "--input", gdir, "-x", "fasta", "--threads", str(threads),
             "--database_path", db, "--output-directory", os.path.join(out, "checkm2")), log)
    return os.path.join(out, "checkm2", "quality_report.tsv")


def annotate(contigs, out, annotator, db, log, threads=4):
    if annotator == "bakta":
        cmd = _cr("bakta", "--output", out, "--threads", str(threads), "--force")
        if db:
            cmd += ["--db", db]
        _tee(cmd + [contigs], log)
    elif annotator == "prokka":
        _tee(_cr("prokka", "--outdir", out, "--force", "--cpus", str(threads), contigs), log)
    else:
        raise ValueError(f"unknown annotator '{annotator}' (bakta | prokka)")
    return out


def species_id(contigs, out, method, db, ref, log, threads=4):
    """method = gtdbtk (needs db) | fastani (needs a reference list)."""
    os.makedirs(out, exist_ok=True)
    if method == "gtdbtk":
        gdir = os.path.join(out, "genomes")
        os.makedirs(gdir, exist_ok=True)
        shutil.copy(contigs, os.path.join(gdir, "genome.fasta"))
        _tee(_cr("bash", "-c",
                 f"GTDBTK_DATA_PATH={db} gtdbtk classify_wf --genome_dir {gdir} "
                 f"--out_dir {os.path.join(out, 'gtdbtk')} -x fasta "
                 f"--cpus {threads} --skip_ani_screen"), log)
        return os.path.join(out, "gtdbtk")
    if method == "fastani":
        res = os.path.join(out, "fastani.tsv")
        _tee(_cr("fastANI", "-q", contigs, "--rl", ref, "-o", res, "-t", str(threads)), log)
        return res
    raise ValueError(f"unknown species-ID method '{method}' (gtdbtk | fastani)")
