---
name: metatranscriptome-analysis
description: 'Use when the user has metatranscriptome (community RNA-seq) data — raw FASTQ, or a function/pathway or taxonomic abundance table — and wants the standard pipeline: QC + host removal, rRNA removal (SortMeRNA), functional profiling (HUMAnN) and taxonomic profiling (MetaPhlAn) of the ACTIVE community, then differential abundance + diversity between conditions with journal figures. Triggers — "metatranscriptome 분석", "메타전사체", "community RNA-seq", "active microbiome / expressed pathways", "SortMeRNA / HUMAnN RNA". NOT for bulk RNA-seq (use transcriptome-analysis), single-cell, amplicon, or shotgun DNA.'
---

# Metatranscriptome Analysis

Run the standard **community RNA-seq (metatranscriptome)** pipeline — QC → host removal →
**rRNA removal** → functional + taxonomic profiling → differential abundance + diversity — from
raw FASTQ or an abundance table. **Same design as `shotgun-analysis`**, which it reuses: the
difference is **rRNA depletion (SortMeRNA)** and that profiling is on RNA (the *active* community).
Downstream (diversity + differential abundance) reuses the **`amplicon-analysis` core**; figures
reuse **`scientific-data-viz`**.

## When to use

- Input is **metatranscriptome**: community RNA FASTQ, or a HUMAnN function/pathway table, or a
  MetaPhlAn taxonomic table, plus sample metadata with a condition column.
- **Not** for: bulk RNA-seq (→ `transcriptome-analysis`), shotgun DNA (→ `shotgun-analysis`),
  amplicon (→ `amplicon-analysis`), single-cell.

## Iron rule — honest methods

State every tool, version, DB, and threshold (QC, host genome, rRNA DB, profiler + DB, DA method
+ FDR). **rRNA removal is essential for metatranscriptomes** (report the % rRNA removed). A gene/
pathway abundance is expression, not just presence — say so. Missing DB → that stage is skipped
with a note, never faked.

## Pipeline (stages)

```
raw FASTQ ─(fastp QC + host removal[optional, Bowtie2])→ ─(rRNA removal: SortMeRNA)→ non-rRNA mRNA
mRNA ┬─(HUMAnN)→ pathway / gene-family abundance (expression of functions)
     └─(MetaPhlAn)→ species abundance (active community)
abundance table (functions OR taxa) ─(CORE, reused from amplicon-analysis: preprocess → alpha →
                 beta (PCoA, PERMANOVA) → differential abundance)→ tables/ images/ script/ logs/ report.md
```

Enter at any stage: **FASTQ → full; a function/taxonomic abundance table → diversity + differential.**

## Databases (user-provided — same policy as shotgun-analysis)

- **Host removal:** a Bowtie2 index (e.g. human GRCh38) — `--host-index PATH`.
- **rRNA (SortMeRNA):** rRNA reference DBs (SILVA / Rfam, shipped with SortMeRNA) — `--rrna-db PATH`.
- **HUMAnN:** ChocoPhlAn + UniRef DBs — `--humann-nuc-db`, `--humann-prot-db` (large).
- **MetaPhlAn:** its marker DB — `--metaphlan-db PATH` (~few GB).
Missing DB → that optional stage is skipped (with a clear note).

## Operating procedure — enter at ANY stage

`pipeline.run(input_path, metadata, condition, out_dir, from_stage=None, profiler="humann")`
detects the input and runs everything downstream. Every run:

0. **Environment** — ensure the `scico-metatx` conda env (below); create if missing (ask first).
1. **Input** — take the data path from the request.
2. **Detect the stage** — `stages.detect_stage(path)` → `fastq` | `feature_table` (abundance) |
   `distance_matrix` | `alpha_table`.
3–4. **Check + ask for DBs** — host / rRNA / HUMAnN / MetaPhlAn (`AskUserQuestion`); no path → skip.
5–6. **Pick options from the data** — fastp thresholds from quality; filter cutoffs from the abundance
   distribution — don't hardcode.
7. **Run + log** — each stage via `conda run -n scico-metatx`, teeing to `logs/<stage>.log`.
8. **Validate** — outputs exist and are sane; stop & report on failure.
9. **Next stage** — repeat downstream.

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/metatranscriptome-analysis")
import pipeline
pipeline.run(
    input_path="pathabundance.tsv",   # FASTQ dir / abundance table / distance matrix / alpha table
    metadata="metadata.csv",          # sample_id + condition column
    condition="condition",
    out_dir="/path/to/results",       # -> tables/ images/ script/ logs/ report.md
    profiler="humann",                # "humann" (functions) or "metaphlan" (taxa)
    from_stage=None,
)
```

## Differential abundance

Same as `amplicon-analysis` (reused): `clr_test` (default, compositional) · `kruskal_lfc` ·
`pydeseq2` (optional, counts); all BH-FDR corrected.

## Environment (conda — auto-created if missing)

One conda env, **`scico-metatx`** (`environment.yml`): Python 3.12 + fastp, bowtie2, samtools,
**sortmerna**, metaphlan, humann, and the core (scikit-bio, matplotlib, …). Create if missing (ask
first), then run via `conda run -n scico-metatx`.

```bash
conda env list | grep -q scico-metatx \
  || conda env create -f skills/metatranscriptome-analysis/environment.yml
```

Reuses the sibling **`shotgun-analysis`** (its QC / host / profiling helpers) and
**`amplicon-analysis`** (diversity + differential core) — keep them as siblings.

## Common mistakes

| Mistake | Fix |
|---|---|
| Skipping rRNA removal | Metatranscriptomes are rRNA-dominated; run SortMeRNA and report % removed |
| Treating expression as presence | Abundance here is expression of functions/taxa — say so |
| Naive per-feature test on relative abundance | Default to `clr_test` (compositional) |
| Uncorrected p-values | Always BH-FDR (built in) |
| Silently skipping a stage when a DB is missing | Say which DB is missing and what was skipped |
