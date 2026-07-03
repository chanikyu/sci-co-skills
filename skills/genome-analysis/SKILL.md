---
name: genome-analysis
description: 'Use when the user has a single bacterial isolate genome — raw FASTQ reads or an assembled contigs FASTA — and wants the standard isolate-genomics backbone: read QC, assembly, assembly QC (QUAST + CheckM2), annotation (Bakta/Prokka), and species identification (GTDB-Tk / fastANI). Triggers — "genome 분석", "isolate/균주 유전체 조립", "assembly + annotation", "이 genome 조립/주석해줘", "species identification / ANI". NOT for metagenomes (use shotgun-analysis) or amplicon (use amplicon-analysis). Strain typing / AMR / virulence / plasmid / pangenome are SEPARATE skills.'
---

# Genome Analysis

Run the standard **bacterial isolate** genome backbone — read QC → assembly → assembly QC →
annotation → species identification — from raw FASTQ or an assembled contigs FASTA, into a
structured results folder. **Same design as `shotgun-analysis`**: enter at any stage,
conda-managed tools, user-provided databases, structured output + logs, honest reporting.

## When to use

- Input is ONE bacterial isolate: paired FASTQ reads, or an assembled contigs FASTA.
- User wants a QC'd assembly, an annotation, and a species/taxonomy call.
- **Not** for: metagenomes / mixed communities (→ `shotgun-analysis`), amplicon/16S
  (→ `amplicon-analysis`), or eukaryotic genomes (different, much heavier tooling).
- **Out of scope by design** (each is its own skill): MLST/strain typing, AMR genes,
  virulence factors, plasmids, pangenome, phylogenomics.

## Iron rule — honest methods, no fabrication

State every tool, version, DB, and threshold (QC settings, assembler, annotation DB, species
method). Always report assembly QC (contiguity + completeness/contamination) so the user knows
whether the assembly is trustworthy before believing the annotation. A missing DB → that stage
is skipped with a clear note, never faked. Never invent a species call.

## Pipeline (stages)

```
raw FASTQ ─(fastp QC)→ trimmed ─(assembler)→ contigs.fasta
   assembler — Illumina: SPAdes | Unicycler | Shovill | SKESA · long-read: Flye | Canu | Raven · hybrid: Unicycler(+long)
contigs.fasta ┬─(QUAST contiguity: N50, #contigs, length)──────────────┐
              ├─(CheckM2 completeness / contamination)─────────────────┤ assembly QC
              ├─(Bakta | Prokka)→ annotation (GFF / GBK / proteins)
              └─(GTDB-Tk | fastANI)→ species identification
→ assembly/ qc/ annotation/ species/ logs/ report.md
```

Enter at any stage: **FASTQ → full pipeline; contigs FASTA → from assembly QC onward.**

## Databases (user-provided — same policy as shotgun-analysis)

- **CheckM2:** its DIAMOND DB — `--checkm2-db PATH`.
- **Bakta:** its DB (`--bakta-db PATH`; ~30–70 GB). (Prokka bundles its own; no path needed.)
- **GTDB-Tk:** the GTDB release dir — `--gtdbtk-db PATH` (**~100 GB**).
- **fastANI (alt species ID):** a reference-genome list — `--fastani-ref PATH`.
Missing DB → that stage is skipped with a note, never faked.

## Operating procedure — enter at ANY stage

`pipeline.run(input_path, out_dir, from_stage=None, assembler="spades", annotator="bakta",
speciesid="gtdbtk")` detects the input and runs everything downstream. Every run:

0. **Environment** — ensure the `scico-genome` conda env (below); create if missing (ask first).
1. **Input** — take the data path from the request.
2. **Detect the stage** — `stages.detect_stage(path)` → `fastq` | `assembly` (contigs FASTA).
3. **Confirm downstream + check DBs** — which DBs the chosen annotator / species method need.
4. **Ask for DB paths** — `AskUserQuestion` for the user-downloaded DBs (Bakta / CheckM2 /
   GTDB-Tk). No path → skip that stage (still emit the assembly / QUAST).
5–6. **Pick each tool's options from the data** — assembler by read type (short → SPAdes/Unicycler,
   long → Flye); fastp thresholds from read quality — don't hardcode.
7. **Run + log** — run each stage via `conda run -n scico-genome`, teeing to `logs/<stage>.log`.
8. **Validate** — outputs exist and are sane (non-empty contigs, QUAST report present, no crash);
   stop & report on failure.
9. **Next stage** — repeat for each downstream step.

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/genome-analysis")
import pipeline
pipeline.run(
    input_path="reads/",          # FASTQ dir (paired) OR a contigs .fasta
    out_dir="/path/to/results",   # -> assembly/ qc/ annotation/ species/ logs/ report.md
    assembler="spades",           # Illumina: spades/unicycler/shovill/skesa · long: flye/canu/raven
    long_reads=None,              # path to long reads -> Unicycler hybrid (short+long)
    annotator="bakta",            # or "prokka" (bundles its own DB)
    speciesid="gtdbtk",           # or "fastani"
    from_stage=None,              # or "assembly" to start from a contigs FASTA
)
```

## Environment (conda — auto-created if missing)

One conda env, **`scico-genome`** (`environment.yml`): Python 3.12 + fastp, spades, unicycler,
flye, quast, checkm2, prokka, bakta, gtdb-tk, fastani. Step 0 of every run: create it if missing
(ask first — it's large), then run tools via `conda run -n scico-genome`.

```bash
conda env list | grep -q scico-genome \
  || conda env create -f skills/genome-analysis/environment.yml
```

Reuses **`scientific-data-viz`** for any summary figures — keep them as siblings.

## Common mistakes

| Mistake | Fix |
|---|---|
| Annotating without assembly QC | Always run QUAST + CheckM2 first; report contiguity + completeness |
| Trusting a contaminated assembly | CheckM2 contamination high → flag it, don't proceed silently |
| Species call with no DB | Skip and say so — never guess the species |
| Using short-read assembler on long reads | Pick Flye for Nanopore/PacBio; SPAdes/Unicycler for Illumina |
| Doing MLST/AMR/pangenome here | Out of scope — those are separate skills |
