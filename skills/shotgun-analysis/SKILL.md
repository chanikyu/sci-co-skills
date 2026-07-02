---
name: shotgun-analysis
description: 'Use when the user has shotgun metagenomics data — raw FASTQ reads, or a taxonomic/functional abundance table — and wants the standard pipeline: QC + host removal, taxonomic profiling (MetaPhlAn or Kraken2+Bracken), functional profiling (HUMAnN), and community analysis (alpha & beta diversity, PCoA, PERMANOVA, differential abundance) with journal figures. Triggers — "shotgun 분석", "metagenomics 분석", "MetaPhlAn/Kraken2", "HUMAnN 기능 분석", "이 metagenome 분석해줘". NOT for amplicon/16S (use amplicon-analysis) or for making a figure from numbers (use scientific-data-viz).'
---

# Shotgun Analysis

Run the standard shotgun-metagenomics pipeline — QC → host removal → taxonomic profiling →
(functional profiling) → alpha/beta diversity + differential abundance — from raw FASTQ or an
abundance table, into a structured results folder. **Same design as `amplicon-analysis`**:
enter at any stage, conda-managed tools, user-provided DBs, and the downstream community
analysis (diversity + differential abundance) **reuses the `amplicon-analysis` core**;
figures reuse `scientific-data-viz`.

## When to use

- Input is **shotgun** metagenomics: raw FASTQ, or a species × samples abundance table
  (MetaPhlAn/Bracken), or a HUMAnN functional table, plus sample metadata with a group column.
- **Not** for: amplicon/16S/ITS (→ `amplicon-analysis`), or plotting numbers you already have
  (→ `scientific-data-viz`).

## Iron rule — honest methods, no fabrication

State every tool, version, DB, and threshold (QC settings, host genome, profiler + DB,
filters, DA method + FDR). Correct for multiple comparisons. Host removal and functional
profiling are opt-in and reported. Never invent significance. DBs are large — the user
provides their paths; the skill does not bundle or silently download them.

## Pipeline (stages)

```
raw FASTQ ─(fastp QC + host removal[optional, Bowtie2])→ clean reads
clean reads ┬─ READ track (default) ─(MetaPhlAn | Kraken2+Bracken)→ species × samples abundance
            │                         (+ optional HUMAnN → pathway / gene-family abundance)
            └─ ASSEMBLY track ─(MEGAHIT|metaSPAdes → map → bin: MetaBAT2 + CONCOCT + SemiBin2
                                → DAS_Tool consensus → CheckM2 QC → GTDB-Tk taxonomy → CoverM)
                                → MAG × samples abundance
abundance table (taxa OR MAGs) ─(CORE, reused from amplicon-analysis: preprocess → alpha →
                 beta (PCoA, PERMANOVA) → differential abundance)→ tables/ images/ script/ logs/ report.md
```

Pick the track with `track="read"` (default) or `track="assembly"`.

## Databases (user-provided — same policy as amplicon-analysis)

DBs are big; the user downloads them and passes paths. The skill validates and reports.
- **Host removal:** a Bowtie2 index of the host genome (e.g. human GRCh38). `--host-index PATH`.
- **MetaPhlAn:** its marker DB dir (`--metaphlan-db PATH`; a few GB).
- **Kraken2 + Bracken:** a Kraken2/Bracken DB dir (`--kraken-db PATH`; **standard DB is 50–100 GB+**).
- **HUMAnN:** ChocoPhlAn + UniRef DBs (`--humann-nuc-db`, `--humann-prot-db`; large).
- **CheckM2** (assembly track): its DIAMOND DB — `--checkm2-db PATH`.
- **GTDB-Tk** (assembly track): the GTDB release dir — `--gtdbtk-db PATH` (**~100 GB**).
Missing DB → that optional stage is skipped (with a clear note), never faked.

## Operating procedure — enter at ANY stage

`pipeline.run(input_path, metadata, group_col, out_dir, from_stage=None, profiler="metaphlan")`
detects the input and runs everything downstream. Every run:

0. **Environment** — ensure the `scico-shotgun` conda env (below); create if missing (ask first).
1. **Input** — take the data path from the request.
2. **Detect the stage** — `stages.detect_stage(path)` → `fastq` | `feature_table`
   (abundance table) | `distance_matrix` | `alpha_table`, plus the downstream steps.
3. **Confirm downstream + check DBs** — which DBs each chosen stage needs (host / profiler / HUMAnN).
4. **Ask for DB paths** — use `AskUserQuestion` for the user-downloaded DB paths of the
   stages that will run. No path → skip that optional stage (run on what you have).
5–6. **Pick each tool's options from the data** — e.g. fastp thresholds from read quality,
   Bracken read-length from the FASTQ, filter cutoffs from the abundance distribution — don't hardcode.
7. **Run + log** — run each stage via `conda run -n scico-shotgun`, teeing stdout/stderr to `logs/<stage>.log`.
8. **Validate** — outputs exist and are sane (non-empty tables, expected columns, no crash); stop & report on failure.
9. **Next stage** — repeat for each downstream step.

Entry points: raw FASTQ → full pipeline; **abundance table → diversity + differential (reused,
tested)**; distance matrix → PCoA + PERMANOVA; alpha table → group test. Stages 0–2 (QC / host /
profiling / HUMAnN) are the shotgun-specific front stages.

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/shotgun-analysis")
import pipeline
pipeline.run(
    input_path="abundance.tsv",          # FASTQ dir / abundance table / distance matrix / alpha table
    metadata="metadata.csv",             # sample_id + group column
    group_col="group",
    out_dir="/path/to/results",          # -> tables/ images/ script/ logs/ report.md
    profiler="metaphlan",                # read track: "metaphlan" or "kraken2" (big DB)
    track="read",                        # or "assembly" (MEGAHIT -> MetaBAT2+CONCOCT+SemiBin2 -> DAS_Tool)
    from_stage=None,
)
```

## Differential-abundance methods

Same as `amplicon-analysis` (reused): `clr_test` (default, compositional) · `kruskal_lfc` ·
`pydeseq2` (optional, counts); all BH-FDR corrected.

## Environment (conda — auto-created if missing)

One conda env, **`scico-shotgun`** (`environment.yml`): Python 3.12 + fastp, bowtie2, samtools,
metaphlan, kraken2, bracken, humann, and the core (scikit-bio, matplotlib, …). Step 0 of every
run: create it if missing (ask first — it's large), then run tools via `conda run -n scico-shotgun`.

```bash
conda env list | grep -q scico-shotgun \
  || conda env create -f skills/shotgun-analysis/environment.yml
```

Reuses the sibling **`amplicon-analysis`** skill (its `analyze` / `diversity` / `figures` core)
and **`scientific-data-viz`** — keep all three as siblings.

## Common mistakes

| Mistake | Fix |
|---|---|
| Skipping host removal on host-associated samples | Offer it; report the host genome + % removed |
| Using Kraken2 without noting the huge DB | State the DB + size; user provides the path |
| Naive per-feature test on relative abundance | Default to `clr_test` (compositional) |
| Uncorrected p-values | Always BH-FDR (built in) |
| Silently skipping a stage when a DB is missing | Say which DB is missing and what was skipped |
