---
name: amplicon-analysis
description: Use when the user has amplicon (16S/ITS) microbiome data — a feature/ASV/OTU table (counts or relative abundance) plus sample metadata — and wants standard community analysis: alpha diversity, beta diversity (distance + PCoA + PERMANOVA), and/or differential abundance between groups, with journal-quality figures. Triggers — "microbiome/amplicon 분석", "alpha/beta diversity 분석", "16S 분석", "차등존재비/differential abundance", "PCoA/PERMANOVA", "이 feature table 분석해줘". NOT for making a figure from already-computed numbers (use scientific-data-viz) or for metabolic modeling.
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

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/amplicon-analysis")
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

## Environment

**scikit-bio requires Python ≤ 3.12.** Create the venv accordingly:

```bash
uv venv --python 3.12 venv
uv pip install --python venv/bin/python -r skills/amplicon-analysis/requirements.txt
```

Depends on the sibling `scientific-data-viz` skill (imported by path) for `journal_style`
and `stats` — keep the two skills as siblings.

## Common mistakes

| Mistake | Fix |
|---|---|
| Rarefying without saying so | Report depth + dropped samples; offer the compositional alternative |
| Naive per-taxon test on relative abundance | Default to `clr_test` (compositional) |
| Uncorrected pairwise p-values | Always BH-FDR (built in) |
| `pydeseq2` on relative abundance | Refuse — it needs counts |
| Faith PD / UniFrac without a tree | Skip and say so |
| Dropping unmatched samples silently | Report IDs present in only one file |
