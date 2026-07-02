# scientific-data-viz

A Claude Code plugin that turns **real data** into **publication-quality journal
figures** (Nature/Cell/eLife style). Figures are **code-rendered** (matplotlib) so the
exact data values are drawn faithfully — never an AI image that fabricates numbers.

## What it does

- **Picks the right plot** for your data from an intent-based guide (bar, box, violin,
  scatter+fit, line, heatmap, forest, Kaplan–Meier, PCoA, Sankey, …). See
  `skills/scientific-data-viz/plot-selection.md`.
- **Journal house style** — white background, minimal chrome, bold panel letters,
  filled points, left/bottom spines only, editable vector PDF output.
- **20 color palettes** — colorblind-safe (Okabe-Ito, Paul Tol), journal house colors
  (NPG/AAAS/NEJM/Lancet/JAMA/JCO/D3), ColorBrewer, and many-category sets (tab20, igv,
  kelly…). Default `tab20`. Visual swatch in `palette_reference.png`.
- **Legends outside** the plot area so they never overlap data.
- **Optional statistics** (`stats.py`) — Welch's t-test, Mann–Whitney U, paired t /
  Wilcoxon, one-way ANOVA, Kruskal–Wallis, correlation, chi-squared, log-rank, and
  **PERMANOVA** for beta diversity — with Shapiro–Wilk-based parametric choice and
  Holm-corrected posthoc. Annotations use the **full test name** (e.g. "Mann–Whitney U
  test, U = 41.0, P = 0.003").
- **Separate table + metadata** input supported (join on `sample_id`, omics-style).
- **Structured output** — `<base>/images/*.png,*.pdf` and `<base>/script/*.py`.

## Install

Add this plugin to Claude Code, then invoke the skill by describing your data/figure
(e.g. "이 데이터로 논문 figure 그려줘", "make a publication figure from this CSV").

Python dependencies (a venv is created on first use):

```bash
python3 -m venv venv && ./venv/bin/pip install -r skills/scientific-data-viz/requirements.txt
```

## Layout

```
skills/scientific-data-viz/
  SKILL.md              workflow + rules (entry point)
  plot-selection.md     data-nature -> best plot guide
  journal_style.py      house-style matplotlib module (palettes, legends, helpers)
  stats.py              optional statistical tests + PCoA/PERMANOVA
  palette_reference.py  render the palette swatch
  palette_reference.png bundled swatch of all 20 palettes
  requirements.txt      Python deps
```

## License

MIT
