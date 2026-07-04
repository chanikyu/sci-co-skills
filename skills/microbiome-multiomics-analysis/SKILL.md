---
name: microbiome-multiomics-analysis
description: 'Use when the user has PAIRED microbiome multi-omics — two or three feature tables on the SAME samples (metagenome taxa/function, metatranscriptome expression, metabolome) + shared sample metadata with a condition — and wants INTEGRATED analysis: sample alignment, per-omic compositional transform (CLR / log), per-omic PERMANOVA (condition footprint), cross-omic Spearman correlation network (BH-FDR), Procrustes + Mantel concordance, and optional MOFA+ shared factors. Part of the microbiome suite (community). Triggers — "multi-omics / 멀티오믹스 통합", "microbiome-metabolome integration", "metagenome + metabolome 통합", "cross-omic correlation", "MOFA". NOT for a single omic alone (use amplicon / shotgun / metatranscriptome / microbiome-metabolome-analysis) — this INTEGRATES them.'
---

# Microbiome Multi-Omics Analysis

**Integrate** two or three paired omics — metagenome (taxa / function), metatranscriptome
(expression), metabolome (metabolites) — measured on the **same samples**, into one analysis: which
layers carry the condition signal, which features couple across layers, and whether the layers agree.
**Same design as the other SciCo skills**: conda-managed Python, structured output + logs, honesty.
Figures reuse **`scientific-data-viz`**. Builds on the single-omic skills (`shotgun-analysis`,
`metatranscriptome-analysis`, `microbiome-metabolome-analysis`) — run those first to get each table.

## When to use

- Input is **paired multi-omics**: 2–3 feature tables (rows = samples, cols = features) on a shared
  sample set + metadata with a condition column.
- **Not** for a single omic (use the per-omic skill). Needs paired samples (same subjects across omics).

## Iron rule — honest integration

State the transform per omic, the test, and **BH-FDR** (cross-omic tests are huge: n_A × n_B — filter
to bound them and report the tested count). BH-FDR is applied **per omic-pair** (each A×B is one
hypothesis family), not globally across all pairs. **Compositional omics (taxa/genes/transcripts) are CLR-transformed**
before any correlation/Gaussian step — untransformed relative abundance manufactures spurious negative
correlations. **Correlation ≠ causation ≠ mechanism**; a shared driver (diet, batch, time) makes indirect
links. Below ~15–20 paired samples, everything is exploratory — say so. **DIABLO / block-sparse sPLS-DA
is R-only** (no trustworthy Python port) — not in this skill; a concatenated-CLR PLS-DA is offered instead.

## Pipeline (stages)

```
{omic tables} + metadata ─(align: intersect sample IDs; report drops; fail on low overlap)→
 per omic ─(filter: prevalence/abundance to bound tests)→ ─(transform: CLR [taxa/genes/transcripts] · log+scale [metabolome])→
 per omic ── PERMANOVA (Aitchison) + dispersion check → condition footprint (R², p) per layer
 cross-omic ── Spearman correlation (every A×B pair) + BH-FDR → significant pairs + bipartite network
 concordance ── Procrustes (PCoA overlay) + Mantel → do the layers arrange samples congruently?
 (optional) MOFA+ ── shared latent factors + variance-explained per omic (flag-gated; needs mofapy2)
 (optional) supervised ── concatenated-CLR PLS-DA (DIABLO substitute)
→ tables/ images/ (correlation heatmap/network, PERMANOVA, Procrustes) script/ logs/ report.md
```

## Transforms (per omic)

- **Compositional** (metagenome taxa, gene-family/pathway, metatranscriptome expression): closure →
  zero replacement (`multi_replace`) → **CLR** (scikit-bio). Aitchison distance = Euclidean on CLR.
- **Metabolome**: log10 (adaptive pseudocount) → auto-scale (it is intensity, not strictly compositional).
Override per omic if needed.

## Reliable core vs optional

- **Core (always on, robust at modest n):** align → CLR/log → PERMANOVA per omic → cross-omic Spearman
  network (BH-FDR) → Procrustes + Mantel. Deterministic, unit-testable.
- **Optional (flag-gated):** MOFA+ (`do_mofa=True`, needs `mofapy2`; stochastic) · concatenated-CLR
  PLS-DA (`do_plsda=True`). HAllA / SPIEC-EASI are noted as external upgrades, not bundled.

## Operating procedure

`pipeline.run(omics={"metagenome": pathA, "metatranscriptome": pathB, "metabolome": pathC},
metadata=..., group_col=..., out_dir=...)` — ensure the `scico-multiomics` conda env (create if
missing, ask first); align + report dropped samples; pick filters from the data; run the core; log
each step; validate; report.

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/microbiome-multiomics-analysis")
import pipeline
pipeline.run(
    omics={"metagenome": "taxa.csv", "metabolome": "metabolites.csv"},  # 2 or 3 tables (samples × features)
    metadata="metadata.csv", group_col="condition",
    out_dir="/path/to/results",
    min_prevalence=0.1, top_n=200,     # bound the cross-omic test count
    do_mofa=False, do_plsda=False,
)
```

## Environment (conda — auto-created if missing)

One conda env, **`scico-multiomics`** (`environment.yml`): Python 3.12 + numpy, pandas, scipy,
**scikit-bio** (CLR, Mantel, PERMANOVA, PCoA), statsmodels (BH-FDR), scikit-learn, matplotlib,
networkx (+ optional `mofapy2` for MOFA+). Create if missing (ask first), run via
`conda run -n scico-multiomics`. Reuses **`scientific-data-viz`** for figures.

## Common mistakes

| Mistake | Fix |
|---|---|
| Correlating raw relative abundance | CLR-transform compositional omics first (spurious negatives otherwise) |
| Unbounded A×B correlations | Prevalence/top-N filter each omic; report the test count; BH-FDR |
| Reading correlation as causation | It is association; a shared driver makes indirect links — say so |
| Integrating with too few samples | < ~15–20 paired → exploratory only; state it |
| PERMANOVA without dispersion check | Report permdisp too (location vs spread confound) |
| Expecting DIABLO | R-only; use the concatenated-CLR PLS-DA substitute (stated as such) |
