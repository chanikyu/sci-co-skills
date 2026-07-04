---
name: microbiome-metabolome-analysis
description: 'Use when the user has an ANNOTATED metabolomics feature table (rows = samples, cols = annotated metabolites with intensities) + sample metadata with a group column, and wants the standard statistical workflow: filtering/imputation, sample normalization (PQN), transformation + scaling (log + Pareto), univariate stats (t / Mann-Whitney / ANOVA / Kruskal + BH-FDR + fold-change/volcano), multivariate (PCA, PLS-DA + VIP + permutation test), heatmap, and optional pathway enrichment (ORA; needs KEGG/HMDB IDs). Part of the microbiome suite (community). Triggers — "metabolome / 메타볼롬 분석", "metabolomics", "이 metabolite table 분석", "PLS-DA / VIP", "MetaboAnalyst 같은 분석". NOT for raw LC-MS peak picking, or multi-omics integration (use metagenome+metatranscriptome+metabolome → microbiome-multiomics-analysis).'
---

# Microbiome Metabolome Analysis

Run the standard **untargeted-metabolomics statistical workflow** — filtering → normalization →
transformation + scaling → univariate stats → multivariate (PCA / PLS-DA) → heatmap → optional
enrichment — starting from an **annotated feature table** (the MetaboAnalyst "Statistical Analysis"
scope; raw peak-picking is assumed done). **Same design as the other SciCo skills**: enter at any
stage, conda-managed Python, structured output + logs. Figures reuse **`scientific-data-viz`**.

## When to use

- Input is an **annotated metabolite feature table**: rows = samples, cols = metabolites (intensities),
  plus sample metadata with a group column.
- **Not** for: raw LC-MS/GC-MS peak picking (XCMS/MZmine first), or integrating metabolome with
  metagenome/metatranscriptome (→ `microbiome-multiomics-analysis`).

## Iron rule — honest metabolomics

State every step: imputation, filtering (group-**blind**), normalization, transform, scaling, the
test used, and **BH-FDR**. **PLS-DA overfits** — always report cross-validated accuracy **and a
permutation test**; never present class separation without it. Fold-change is on the original
(non-log) scale. Enrichment needs KEGG/HMDB IDs and inherits **annotation-confidence (MSI level 1–4)**
uncertainty — say so. A feature filtered out (missingness/variance) is reported, not silently dropped.

## Pipeline (stages)

```
annotated table ─(clean: drop >50% missing → half-min impute[KNN opt] → prevalence/variance filter, group-blind)→
   ─(sample normalize: PQN [median / TSS opt])→ ─(transform: log10 / glog)→ ─(scale: Pareto [auto/range opt])→
univariate: t-test / Mann-Whitney (2 grp) · ANOVA / Kruskal (>2) + fold-change → BH-FDR → volcano
multivariate: PCA (QC / outliers) → PLS-DA + VIP + CV accuracy + permutation test → heatmap (top features)
(optional, separate helper `enrichment.ora` — NOT auto-run) ORA (hypergeometric) — needs KEGG/HMDB IDs
→ tables/ images/ (PCA, volcano, PLS-DA + VIP, heatmap) script/ logs/ report.md
```

Enter at any stage: **feature table → full; a stats/results table → figures.**

## Order matters (do not reorder)

filter → **sample** normalization → transform → **feature** scaling → stats. Never scale before
transforming; never normalize after scaling; all filtering/normalization is **group-blind** (no leakage).

## Defaults (three toggles that matter)

- **Imputation:** half-minimum (`--impute knn` alternative).
- **Normalization:** PQN (`--norm median|tss`; TSS warns about compositionality).
- **Scaling:** Pareto (`--scale auto|range`).
Everything else is sensible + fixed (log10 transform, BH-FDR, VIP>1 shortlist, permutation on PLS-DA).

## Operating procedure — enter at ANY stage

`pipeline.run(input_path, metadata, group_col, out_dir, from_stage=None, ...)` detects the input and
runs everything downstream. Every run: ensure the `scico-metabolome` conda env (create if missing,
ask first); detect the stage (`stages.detect_stage`); pick the toggles from the data (missingness,
QC presence, group count) — don't hardcode; run + log each step; validate outputs; report.

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/microbiome-metabolome-analysis")
import pipeline
pipeline.run(
    input_path="metabolites.csv",  # samples × metabolites, OR a results table
    metadata="metadata.csv",       # sample_id + group column
    group_col="group",
    out_dir="/path/to/results",    # -> tables/ images/ script/ logs/ report.md
    impute="halfmin", norm="pqn", scale="pareto",
    from_stage=None,
)
```

## Environment (conda — auto-created if missing)

One conda env, **`scico-metabolome`** (`environment.yml`): Python 3.12 + numpy, pandas, scipy,
statsmodels, scikit-learn, matplotlib (+ optional `gseapy` for enrichment). No external CLI tools —
it is pure-Python statistics. Create if missing (ask first), run via `conda run -n scico-metabolome`.
Reuses **`scientific-data-viz`** for figures — keep them as siblings.

## Common mistakes

| Mistake | Fix |
|---|---|
| Scaling before transforming | Order is transform → scale (Pareto on log data) |
| Group-aware filtering | Filter on QC/variance/prevalence only — never the t-test (leakage) |
| PLS-DA separation without validation | Report CV accuracy + permutation test; separation of noise is easy |
| Fold-change on log data | Compute FC on the original / normalized (non-log) scale |
| Uncorrected p-values | Always BH-FDR across features |
| Enrichment sold as fact | State MSI annotation level; only KEGG/HMDB-mapped features enter |
