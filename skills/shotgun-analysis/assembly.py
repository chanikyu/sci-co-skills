"""
assembly.py — shotgun assembly-based track: clean reads -> assembly -> mapping -> binning
(MAGs) -> QC (CheckM2) -> taxonomy (GTDB-Tk) -> MAG abundance table for the shared core.
Reuses the QC/host helpers from frontstages. Runs tools in the `scico-shotgun` conda env.

UNVERIFIED in-session (needs env + reads + big DBs [CheckM2, GTDB-Tk ~100 GB] + high RAM for
assembly). Standard MEGAHIT/MetaBAT2/CheckM2/GTDB-Tk/CoverM usage; verify against your data.
"""
import os
from frontstages import _tee, _pairs, _cr, _fastp, _host_remove  # reuse QC helpers + conda-run


def _assemble(pairs, out, assembler, coassembly, log, threads):
    asm = os.path.join(out, "assembly")
    r1s = [p[1] for p in pairs]
    r2s = [p[2] for p in pairs]
    if assembler == "megahit":
        if not coassembly:  # simplest: co-assembly OR first sample; default co-assembly
            pass
        _tee(_cr("megahit", "-1", ",".join(r1s), "-2", ",".join(r2s),
                 "-o", asm, "-t", str(threads)), log)
        return os.path.join(asm, "final.contigs.fa")
    # metaSPAdes needs single files
    c1, c2 = os.path.join(out, "all_R1.fq.gz"), os.path.join(out, "all_R2.fq.gz")
    _tee(_cr("bash", "-c", f"cat {' '.join(r1s)} > {c1} && cat {' '.join(r2s)} > {c2}"), log)
    _tee(_cr("spades.py", "--meta", "-1", c1, "-2", c2, "-o", asm, "-t", str(threads)), log)
    return os.path.join(asm, "contigs.fasta")


def _map(contigs, pairs, out, log, threads):
    os.makedirs(out, exist_ok=True)
    idx = os.path.join(out, "contigs_idx")
    _tee(_cr("bowtie2-build", "--threads", str(threads), contigs, idx), log)
    bams = []
    for name, r1, r2 in pairs:
        bam = os.path.join(out, f"{name}.sorted.bam")
        _tee(_cr("bash", "-c",
                 f"bowtie2 -p {threads} -x {idx} -1 {r1} -2 {r2} | "
                 f"samtools sort -@ {threads} -o {bam} - && samtools index {bam}"), log)
        bams.append(bam)
    return bams


def _ensemble_bin(contigs, bams, out, log, threads):
    """Ensemble binning: MetaBAT2 + CONCOCT + SemiBin2, refined to a consensus set by DAS_Tool.
    Returns the DAS_Tool refined-bins dir."""
    os.makedirs(out, exist_ok=True)

    # --- MetaBAT2 ---
    depth = os.path.join(out, "depth.txt")
    _tee(_cr("bash", "-c",
             f"jgi_summarize_bam_contig_depths --outputDepth {depth} {' '.join(bams)}"), log)
    mb = os.path.join(out, "metabat"); os.makedirs(mb, exist_ok=True)
    _tee(_cr("metabat2", "-i", contigs, "-a", depth, "-o", os.path.join(mb, "bin"),
             "-t", str(threads)), log)

    # --- CONCOCT ---
    cc = os.path.join(out, "concoct"); os.makedirs(cc, exist_ok=True)
    bed, cut = os.path.join(cc, "contigs_10K.bed"), os.path.join(cc, "contigs_10K.fa")
    _tee(_cr("bash", "-c", f"cut_up_fasta.py {contigs} -c 10000 -o 0 --merge_last -b {bed} > {cut}"), log)
    cov = os.path.join(cc, "coverage.tsv")
    _tee(_cr("bash", "-c", f"concoct_coverage_table.py {bed} {' '.join(bams)} > {cov}"), log)
    _tee(_cr("concoct", "--composition_file", cut, "--coverage_file", cov,
             "-b", os.path.join(cc, "out"), "-t", str(threads)), log)
    _tee(_cr("bash", "-c",
             f"merge_cutup_clustering.py {os.path.join(cc, 'out_clustering_gt1000.csv')} "
             f"> {os.path.join(cc, 'merged.csv')}"), log)
    ccbins = os.path.join(cc, "bins"); os.makedirs(ccbins, exist_ok=True)
    _tee(_cr("bash", "-c",
             f"extract_fasta_bins.py {contigs} {os.path.join(cc, 'merged.csv')} --output_path {ccbins}"), log)

    # --- SemiBin2 ---
    sb = os.path.join(out, "semibin")
    _tee(_cr("SemiBin2", "single_easy_bin", "-i", contigs, "-b", *bams,
             "-o", sb, "-t", str(threads), "--self-supervised"), log)
    sbbins = os.path.join(sb, "output_bins")

    # --- contig-to-bin tables + DAS_Tool consensus ---
    def _c2b(bindir, ext, name):
        tsv = os.path.join(out, f"{name}.contigs2bin.tsv")
        _tee(_cr("bash", "-c", f"Fasta_to_Contig2Bin.sh -i {bindir} -e {ext} > {tsv}"), log)
        return tsv
    tables = ",".join([_c2b(mb, "fa", "metabat2"), _c2b(ccbins, "fa", "concoct"),
                       _c2b(sbbins, "fa.gz", "semibin2")])
    dt = os.path.join(out, "dastool")
    _tee(_cr("DAS_Tool", "-i", tables, "-l", "metabat2,concoct,semibin2",
             "-c", contigs, "-o", os.path.join(dt, "out"), "--write_bins", "-t", str(threads)), log)
    return os.path.join(dt, "out_DASTool_bins")


def _checkm2(bins, out, db, log, threads):
    _tee(_cr("checkm2", "predict", "--input", bins, "-x", "fa", "--threads", str(threads),
             "--database_path", db, "--output-directory", os.path.join(out, "checkm2")), log)


def _gtdbtk(bins, out, db, log, threads):
    _tee(_cr("bash", "-c",
             f"GTDBTK_DATA_PATH={db} gtdbtk classify_wf --genome_dir {bins} "
             f"--out_dir {os.path.join(out, 'gtdbtk')} --extension fa "
             f"--cpus {threads} --skip_ani_screen"), log)


def _mag_abundance(bins, bams, out, log, threads):
    os.makedirs(out, exist_ok=True)
    tsv = os.path.join(out, "mag_abundance.tsv")
    _tee(_cr("bash", "-c",
             f"coverm genome -b {' '.join(bams)} --genome-fasta-directory {bins} "
             f"-x fa -m relative_abundance -t {threads} -o {tsv}"), log)
    import pandas as pd
    df = pd.read_csv(tsv, sep="\t").set_index(pd.read_csv(tsv, sep="\t").columns[0])
    out_csv = os.path.join(out, "abundance_table.csv")
    df.T.rename_axis("sample_id").to_csv(out_csv)   # samples × MAGs
    return out_csv


def run(input_dir, out_dir, assembler="megahit", coassembly=True, host_index=None,
        checkm2_db=None, gtdbtk_db=None, threads=8, logf=None):
    """FASTQ dir -> MAG abundance_table.csv (path). Optional CheckM2 QC + GTDB-Tk taxonomy."""
    os.makedirs(out_dir, exist_ok=True)
    logf = logf or os.path.join(out_dir, "assembly.log")
    qc = os.path.join(out_dir, "qc")
    os.makedirs(qc, exist_ok=True)

    cleaned = []
    for name, r1, r2 in _pairs(input_dir):
        r1, r2 = _fastp(name, r1, r2, qc, logf, threads)
        if host_index:
            r1, r2 = _host_remove(name, r1, r2, host_index, qc, logf, threads)
        cleaned.append((name, r1, r2))

    contigs = _assemble(cleaned, out_dir, assembler, coassembly, logf, threads)
    bams = _map(contigs, cleaned, os.path.join(out_dir, "mapping"), logf, threads)
    bins = _ensemble_bin(contigs, bams, os.path.join(out_dir, "binning"), logf, threads)
    if checkm2_db:
        _checkm2(bins, out_dir, checkm2_db, logf, threads)   # MAG completeness/contamination
    if gtdbtk_db:
        _gtdbtk(bins, out_dir, gtdbtk_db, logf, threads)     # MAG taxonomy
    return _mag_abundance(bins, bams, os.path.join(out_dir, "abundance"), logf, threads)
