# 📊 scientific-data-viz

<sub>[← SciCo-Skills](../../README.md) · a skill in the SciCo-Skills suite</sub>

Turn **real data** into **publication-quality journal figures** (Nature / Cell / eLife
style). Not an AI image generator — it writes `matplotlib` code that renders your **exact**
numbers, then exports an editable vector PDF plus a reproducible script.

<div align="center">
<img src="../../assets/plot_catalogue.png" width="82%" alt="Plot catalogue"/>
<img src="../../assets/palettes.png" width="66%" alt="Color palettes"/>
</div>

## Features

|  |  |
|---|---|
| 🎯 **Right plot, automatically** | Intent-based guide (`plot-selection.md`) maps data shape → the clearest chart |
| 🧑‍🔬 **Journal house style** | White background, minimal chrome, bold panel letters, filled points, editable PDF |
| 🎨 **20 palettes** | Colorblind-safe (Okabe-Ito, Paul Tol) · journal (NPG/AAAS/NEJM/Lancet/JAMA/JCO/D3) · many-category (tab20/igv/kelly) |
| 📐 **Legends outside** | Never overlap the data |
| 📈 **Optional statistics** | Welch's t / Mann–Whitney / paired-t / Wilcoxon / ANOVA / Kruskal / correlation / log-rank / **PERMANOVA**, full test names, Holm posthoc |
| 📁 **Structured output** | `images/*.png,*.pdf` + `script/*.py` |

## Supported plots

Comparison (bar+points, dot, grouped bar) · Distribution (box, violin, raincloud,
strip/swarm, histogram, KDE, ECDF) · Relationship (scatter+fit+CI, bubble, hexbin) ·
Trend (line+band, multi-line, area) · Composition (stacked, 100%-stacked, treemap, pie) ·
Ranking (ordered bar, lollipop) · Paired (slope, difference) · Effect size (forest) ·
Matrix (heatmap, clustermap, mosaic) · Survival (Kaplan–Meier, cumulative incidence) ·
Agreement (Bland–Altman) · Multivariate (PCA, UMAP, PCoA) · Flow (Sankey, chord).

## Usage

```python
import sys; sys.path.insert(0, "skills/scientific-data-viz")
import journal_style as J
J.set_style(palette="tab20")           # 20 palettes; default tab20
fig, axes = J.figure_grid(1, 3, width="2col", panel_h=2.6)
# ...plot exact data; J.legend_outside(ax); J.sig_bracket(...)...
J.save(fig, f"{images_dir}/figure1")   # -> .png (300 dpi) + editable .pdf
```

Optional statistics live in `stats.py` (`S.compare`, `S.posthoc`, `S.permanova`,
`S.report`). See **[`SKILL.md`](SKILL.md)** for the full workflow, palette catalogue,
and rules. Deps: `matplotlib`, `numpy`, `scipy`, `pandas`, `squarify`
([`requirements.txt`](requirements.txt)).
