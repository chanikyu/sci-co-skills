---
name: amplicon-analysis
description: 'Use when the user has amplicon (16S/ITS) microbiome data — a feature/ASV/OTU table (counts or relative abundance) plus sample metadata — and wants standard community analysis: alpha diversity, beta diversity (distance + PCoA + PERMANOVA), and/or differential abundance between groups, with journal-quality figures. Triggers — "microbiome/amplicon 분석", "alpha/beta diversity 분석", "16S 분석", "차등존재비/differential abundance", "PCoA/PERMANOVA", "이 feature table 분석해줘". NOT for making a figure from already-computed numbers (use scientific-data-viz) or for metabolic modeling.'
---

# Amplicon Analysis

Run the standard amplicon (16S/ITS) pipeline — preprocess → alpha diversity → beta
diversity → differential abundance — from a feature table + metadata, and emit a
structured results folder (tables + journal figures + report). Diversity/PCoA/PERMANOVA
use **scikit-bio**; figure style and full-name stat annotations reuse the sibling
**scientific-data-viz** skill.

## When to use

- Input is a microbiome **feature table** (samples × ASV/OTU/taxa; counts or relative)
  plus **sample metadata** with a grouping column.
- User wants alpha/beta diversity and/or differential abundance between groups.
- **Not** for: rendering a figure from numbers you already have (→ `scientific-data-viz`),
  metabolic modeling, or non-amplicon omics.

## Iron rule — honest methods, no fabrication

State every method and threshold (filter cutoff, rarefaction depth, distance metric, DA
method + FDR). Always correct for multiple comparisons. Rarefaction discards data — it is
opt-in and reported, with the compositional (no-rarefaction) alternative offered. Faith PD /
UniFrac only when a phylogenetic tree is provided. Never invent significance.

## Workflow

1. **Load & validate** — read the feature table + metadata; auto-detect counts vs relative;
   join on `sample_id` and REPORT any unmatched IDs (never silently drop).
2. **Preprocess** — filter low-prevalence features; optional rarefaction (counts only, seeded,
   reported); derive relative-abundance and CLR views.
3. **Alpha** — observed / Shannon / Simpson / Pielou (+ Chao1 for counts); compare groups
   (test chosen by normality; annotated with its full name).
4. **Beta** — distance (Bray–Curtis / Jaccard) → PCoA (% variance) → PERMANOVA.
5. **Differential abundance** — pick a method (default `clr_test`); BH-FDR.
6. **Output** — `<base>/tables/*.csv`, `<base>/images/*.png,*.pdf`, `<base>/script/*.py`,
   `<base>/report.md`. Tell the user the layout and the key results.

## Operating procedure — enter at ANY stage

`pipeline.run(input_path, metadata, group_col, out_dir, from_stage=None)` detects what the
input is and runs everything downstream. Follow this every run:

0. **Environment** — ensure the `scico-amplicon` conda env (below); create if missing (ask first).
1. **Input** — take the data path from the request.
2. **Detect the stage** — `stages.detect_stage(path)` → `fastq` | `feature_table` |
   `distance_matrix` | `alpha_table`, plus the downstream steps.
3. **Confirm downstream + check DB** — a taxonomy DB is needed ONLY for FASTQ → taxonomy;
   everything else runs without it.
4. **Ask for the DB path** — if taxonomy is wanted, use `AskUserQuestion` for the
   user-downloaded reference DB (16S → SILVA, ITS → UNITE). No path → skip taxonomy (run on ASVs).
5–6. **Pick each tool's options from the data** — e.g. DADA2 `truncLen`/`maxEE` from the
   read-quality profile, filter thresholds from the prevalence distribution — don't hardcode.
7. **Run + log** — run each stage via `conda run`, teeing stdout/stderr to `logs/<stage>.log`.
8. **Validate** — outputs exist and are sane (files non-empty, p ∈ [0,1], no crash); stop &
   report on failure.
9. **Next stage** — repeat for each downstream step.

Entry points (tested): feature table → full pipeline; distance matrix → PCoA + PERMANOVA;
alpha table → group test + figure. FASTQ (Stage 0, DADA2) is the pluggable front stage.

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/amplicon-analysis")
import pipeline
pipeline.run(                            # enters at whatever stage the input is
    input_path="feature_table.csv",      # FASTQ dir / feature table / distance matrix / alpha table
    metadata="metadata.csv",             # sample_id + group column
    group_col="group",
    out_dir="/path/to/results",          # -> tables/ images/ script/ logs/ report.md
    from_stage=None,                      # or force e.g. "feature_table"
)

# or the core directly (feature table onward):
import analyze
analyze.run(
    feature_table="feature_table.csv",   # samples × taxa (counts or relative); index=sample_id
    metadata="metadata.csv",             # sample_id + group column
    group_col="group",
    out_dir="/path/to/results",
    da_method="clr_test",                # or "kruskal_lfc", "pydeseq2" (counts only)
    metric="braycurtis",                 # or "jaccard"
    min_prevalence=0.1,
    do_rarefy=False,                     # True (counts only) to rarefy; reported
    palette="okabe_ito",                 # any scientific-data-viz palette
)
```

Modules: `preprocess` (load/detect/join/filter/rarefy/clr), `diversity` (alpha + beta +
PCoA + PERMANOVA via scikit-bio), `differential` (clr_test / kruskal_lfc / pydeseq2),
`figures` (journal-style plots), `analyze` (orchestrator).

## Differential-abundance methods

- **`clr_test`** (default) — CLR transform + per-taxon Mann–Whitney (2 groups) / Kruskal (3+)
  + BH-FDR. Compositional-aware, pure-Python.
- **`kruskal_lfc`** — Kruskal–Wallis on relative abundance + log2 fold-change + BH-FDR.
- **`pydeseq2`** (optional) — DESeq2-style negative-binomial; **counts only**; used only if
  the `pydeseq2` package is installed. Refuses on relative-abundance input.

## Environment (conda — auto-created if missing)

All tools live in ONE conda env, **`scico-amplicon`** (`environment.yml`: Python 3.12 +
scikit-bio, and for FASTQ Stage 0, R + `bioconductor-dada2` + `cutadapt`).

**Step 0 of every run — ensure the env, create it if it's missing** (ask the user first: it's
a large ~1–2 GB, ~10–15 min install), then run every tool through it:

```bash
conda env list | grep -q scico-amplicon \
  || conda env create -f skills/amplicon-analysis/environment.yml   # one-time; mamba/libmamba is faster
conda run -n scico-amplicon python -m amplicon ...                  # all tools via `conda run -n scico-amplicon`
```

Created once, reused after. Depends on the sibling `scientific-data-viz` skill (imported by
path) for `journal_style` and `stats` — keep the two as siblings.

## Common mistakes

| Mistake | Fix |
|---|---|
| Rarefying without saying so | Report depth + dropped samples; offer the compositional alternative |
| Naive per-taxon test on relative abundance | Default to `clr_test` (compositional) |
| Uncorrected pairwise p-values | Always BH-FDR (built in) |
| `pydeseq2` on relative abundance | Refuse — it needs counts |
| Faith PD / UniFrac without a tree | Skip and say so |
| Dropping unmatched samples silently | Report IDs present in only one file |
