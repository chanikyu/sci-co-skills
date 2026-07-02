# 🧬 amplicon-analysis

<sub>[← SciCo-Skills](../../README.md) · a skill in the SciCo-Skills suite</sub>

The standard **16S/ITS microbiome** workflow, end to end, from a feature table (counts or
relative abundance) + sample metadata. Diversity/PCoA/PERMANOVA use **scikit-bio**; figures
and full-name statistics reuse **[scientific-data-viz](../scientific-data-viz)**.

<div align="center">
<img src="../../assets/amplicon_workflow.png" width="92%" alt="amplicon-analysis pipeline: input → preprocess → alpha / beta / differential abundance → output"/>
</div>

## Pipeline

1. **Preprocess** — auto-detect counts vs relative; join on `sample_id` (report mismatches,
   never silently drop); filter low-prevalence features; optional seeded rarefaction; CLR.
2. **Alpha diversity** — observed / Shannon / Simpson / Pielou / Chao1, with a full-name
   group test (parametric vs non-parametric chosen by a Shapiro–Wilk normality test).
3. **Beta diversity** — Bray–Curtis / Jaccard → PCoA (% variance axis labels) → **PERMANOVA**.
4. **Differential abundance** — BH-FDR corrected:
   - `clr_test` (default) — CLR + Mann–Whitney / Kruskal (compositional-aware)
   - `kruskal_lfc` — Kruskal–Wallis + log2 fold-change
   - `pydeseq2` (optional) — DESeq2-style negative-binomial, **counts only**
5. **Output** — `tables/*.csv`, `images/*.png,*.pdf` (alpha box, beta PCoA, DA volcano + bar),
   `script/run_amplicon_analysis.py`, and a plain-language `report.md`.

## Usage

```python
import sys; sys.path.insert(0, "skills/amplicon-analysis")
import analyze
analyze.run(
    feature_table="feature_table.csv",   # samples × taxa (counts or relative); index=sample_id
    metadata="metadata.csv",             # sample_id + group column
    group_col="group",
    out_dir="results",
    da_method="clr_test",                # or "kruskal_lfc", "pydeseq2"
    metric="braycurtis",                 # or "jaccard"
    do_rarefy=False,                     # True (counts only) to rarefy; reported
)
```

## Environment

**scikit-bio requires Python ≤ 3.12.** Create the venv accordingly:

```bash
uv venv --python 3.12 venv
uv pip install --python venv/bin/python -r skills/amplicon-analysis/requirements.txt
```

## Honesty

Methods and thresholds are always stated; multiple testing is corrected; rarefaction is
opt-in and reported (with the compositional alternative offered); Faith PD / UniFrac only
with a supplied tree; significance is never invented. Full rules: **[`SKILL.md`](SKILL.md)**.
