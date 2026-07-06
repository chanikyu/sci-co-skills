---
name: virome-analysis
description: 'Use when the user has metagenome data for VIRAL / phage community analysis (the virome) — assembled contigs (or reads to assemble), or a vOTU abundance table — and wants: viral contig identification (geNomad), QC + completeness (CheckV, provirus excision), dereplication into vOTUs (95% ANI / 85% AF, MIUViG), taxonomy (geNomad / vConTACT3), optional host prediction (iPHoP) and lifestyle (BACPHLIP), read-mapped vOTU abundance (CoverM, coverage-breadth cutoff), then diversity + differential abundance (reusing the amplicon-analysis core). Part of the microbiome suite (Metagenome / DNA). Triggers — "virome / 바이롬", "viral metagenomics", "phage 분석", "geNomad / CheckV / vOTU". NOT for bacterial profiling (use shotgun-analysis) or 16S (amplicon-analysis).'
---

# Virome Analysis (metagenomic viruses / phages)

Recover and analyze the **virome** — the viruses and bacteriophages that bacterial profilers
(MetaPhlAn / Kraken) ignore — from a metagenome: identify viral contigs → QC → dereplicate into
**vOTUs** → taxonomy / host / lifestyle → read-mapped abundance → diversity + differential. **Same
design as the other SciCo skills**: enter at any stage, conda-managed tools, user-provided DBs,
honesty. The downstream (diversity + differential) **reuses the `amplicon-analysis` core**; figures
reuse **`scientific-data-viz`**. Builds on `shotgun-analysis` (assembly).

## When to use

- Input is a metagenome for **viral** analysis: assembled contigs FASTA (or reads to assemble), or a
  **vOTU × samples** abundance table + metadata.
- **Not** for bacterial taxonomic profiling (→ `shotgun-analysis`) or 16S/ITS (→ `amplicon-analysis`).

## Iron rule — honest viromics

State every tool + version + DB + threshold. **Host prediction is low-confidence** (most vOTUs
unassigned — say so); **viral taxonomy is coarse** (often only family/order); a vOTU counts as
**present only above the coverage-breadth cutoff** (≥75% of its length covered) — not on a single read.
CheckV completeness is a **database estimate** (uncultivated viruses underestimated). Report the
quality tiers and how many vOTUs passed. Viral **RPKM is compositional** (same caveats as taxa — CLR
handles it, but virome tables are sparse, so use a higher `min_prevalence`). **Richness (observed
vOTUs) is depth-confounded** (RPKM is not rarefiable) — say so. Report **Jaccard (presence/absence)**
alongside Bray–Curtis, since detection is already breadth-gated.

## Pipeline (stages)

```
contigs (≥1.5 kb; reuse shotgun assembly) ─(geNomad: viral contig identification, score ≥0.7)→ viral contigs
   ─(CheckV: completeness/contamination + provirus excision; keep Medium+ ≥50%)→ QC'd viral genomes
   ─(dereplicate: 95% ANI / 85% AF, MIUViG)→ vOTU representatives
vOTUs ┬─(optional, external — NOT auto-run: taxonomy · iPHoP host · BACPHLIP lifestyle · vConTACT3)
      └─(map reads: CoverM/bowtie2, breadth ≥75%)→ vOTU × samples abundance   ← the wired path
abundance ─(CORE, reused from amplicon-analysis: preprocess → alpha → beta (PCoA, PERMANOVA)
           → differential abundance)→ tables/ images/ script/ logs/ report.md
```

Enter at any stage: **contigs → full; a vOTU abundance table → diversity + differential.**

## Databases (user-provided — large)

- **geNomad DB** (~1.4 GB, `genomad download-database`).
- **CheckV DB** (~10 GB).
- **iPHoP DB** (~40 GB) — host prediction is **optional** (heavy); off by default.
- VirSorter2 / vConTACT3 DBs if those engines are chosen.
A missing DB → that stage is skipped with a clear note; iPHoP off unless `--host`.

## Operating procedure — enter at ANY stage

`pipeline.run(input_path, metadata, group_col, out_dir, from_stage=None, reads_dir=None, ...)` detects
the input and runs downstream. Every run: ensure the `scico-virome` conda env (create if missing, ask
first); detect the stage; pick cutoffs from the data (score, completeness tier, breadth) — don't
hardcode; run + log each stage via `conda run -n scico-virome`; validate; report the quality tiers.
Before a heavy install/DB download or large mapping job, report the estimate and confirm.

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/virome-analysis")
import pipeline
pipeline.run(
    input_path="contigs.fasta",   # contigs FASTA / vOTU abundance table / distance matrix
    metadata="metadata.csv",      # sample_id + group column
    group_col="group",
    out_dir="/path/to/results",
    reads_dir="qc_reads/",        # for vOTU abundance (map reads back)
)
```

## Reliable core vs external

- **External CLI (conda, needs big DBs — scaffolded):** geNomad, CheckV, VirSorter2, iPHoP, CoverM, bowtie2.
- **Python-native (testable):** vOTU **dereplication** (greedy ANI/AF clustering), **abundance-table
  assembly** (breadth cutoff), and the whole **downstream** (reuses amplicon-analysis core).
- **Wired in `pipeline.run`:** geNomad identify → CheckV QC (**keeps Medium+**) → dereplicate → CoverM
  abundance → downstream. **Optional / not auto-run:** viral taxonomy table, iPHoP host, BACPHLIP
  lifestyle, vConTACT3, VirSorter2 — available in the env, but invoked separately.

## Environment (conda — auto-created if missing)

One conda env, **`scico-virome`** (`environment.yml`): Python 3.10 + genomad, checkv, coverm, bowtie2,
seqkit, and the core (scikit-bio, matplotlib, …) (+ optional virsorter2, iphop, bacphlip). Create if
missing (ask first), run via `conda run -n scico-virome`. Reuses `amplicon-analysis` (core) +
`scientific-data-viz` (figures) — keep them as siblings.

## Common mistakes

| Mistake | Fix |
|---|---|
| Counting a vOTU present on 1 read | Require **coverage breadth ≥ 75%** before calling present |
| Trusting host predictions | iPHoP is low-confidence; most vOTUs unassigned — state it |
| Skipping CheckV / provirus excision | QC + trim host regions before dereplication |
| Over-reading viral taxonomy | Often only family/order; don't over-claim species |
| Not dereplicating | Cluster to vOTUs (95% ANI / 85% AF) before abundance |
