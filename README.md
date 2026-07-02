# scientific-data-viz

> A **Claude Code Skill** (packaged as a plugin) that turns your **real data** into
> **publication-quality journal figures** — Nature/Cell/eLife house style, **code-rendered**
> with `matplotlib` so every value is exact.

![Multi-panel journal figure](assets/hero_multipanel.png)

This is **not** an AI image generator. Image models fabricate bar heights, axes, and
error bars. This skill writes plotting code that renders the *exact* numbers you provide,
in a clean journal style, and exports an editable vector PDF plus a reproducible script.

---

## What is this?

`scientific-data-viz` is a **Skill** for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).
You don't call a CLI — you describe your data or figure in natural language and Claude
loads the skill and does the work. Example prompts that trigger it:

- "이 CSV로 논문 figure 그려줘" / "make a publication figure from this data"
- "저널 스타일 box plot / taxonomy barplot / PCoA 그려줘"
- "draw a Kaplan–Meier / forest plot / heatmap for my paper"

The plugin bundles the skill and its Python helpers.

---

## Features

- **Right plot for the data.** An intent-based selection guide maps your data's shape to
  the chart a reader understands fastest (bar, box, violin, raincloud, scatter+fit, line,
  heatmap, forest, Kaplan–Meier, PCoA, Sankey, chord, and more).
- **Journal house style.** White background, no decorative chrome, bold panel letters,
  filled data points, left/bottom spines only, colorblind-safe defaults.
- **Exact values.** Bars start at zero; error type (SD/SEM/CI) is always labeled; nothing
  is smoothed, rounded for looks, or invented.
- **20 color palettes** (default `tab20`): colorblind-safe (Okabe-Ito, Paul Tol), journal
  house colors (NPG, AAAS, NEJM, Lancet, JAMA, JCO, D3), ColorBrewer, and many-category
  sets (tab20, igv, kelly) for figures with lots of groups/taxa. Visual swatch included.
- **Legends outside** the plot so they never overlap data.
- **Optional statistics** with correct, fully-named tests (see below).
- **Separate table + metadata** input (join on `sample_id`, omics-style).
- **Structured output:** `<folder>/images/*.png,*.pdf` + `<folder>/script/*.py`.

---

## Examples

Real figures produced by the skill from fake-but-realistic data.

**Taxonomy bar plot** — 9 genera, samples grouped by condition, many-category palette,
legend outside:

![Taxonomy bar plot](assets/example_taxonomy_barplot.png)

**Alpha diversity** — box + individual points, with a **computed** test annotated by its
**full name** (never a bare `t, p`):

![Alpha diversity](assets/example_alpha_diversity.png)

**Beta diversity (PCoA)** — from a distance matrix, axes labeled with **% variance
explained**, group separation tested with **PERMANOVA**:

![Beta diversity PCoA](assets/example_beta_pcoa.png)

**Plot variety** — one page of the built-in catalogue (comparison & distribution):

![Plot catalogue](assets/plot_catalogue.png)

**Color palettes** — 20 sets, grouped by purpose:

![Palettes](assets/palettes.png)

---

## Installation

### 1. Add the plugin to Claude Code

```
/plugin marketplace add chanikyu/scientific-data-viz
/plugin install scientific-data-viz
```

### 2. Python dependencies

A virtual environment is created on first use; or set it up manually:

```bash
python3 -m venv venv
./venv/bin/pip install -r skills/scientific-data-viz/requirements.txt
```

Requires `matplotlib`, `numpy`, `scipy`, `pandas`, `squarify`.

---

## Usage

Just describe what you want. The skill follows a fixed workflow:

1. **Ingest & inspect** the data (types, sample size, paired/longitudinal, uncertainty).
   Supports a single table, or a **feature table + a separate metadata file** joined on
   `sample_id`.
2. **Pick the plot** using the selection guide (`plot-selection.md`).
3. **Ask which color palette** to use (shows the 20-palette swatch; default `tab20`).
4. **(Optional) run statistics** — only if you ask, or provide raw replicates.
5. **Render** in journal style with legends outside the plot.
6. **Output** `images/<name>.png` (300 dpi) + `images/<name>.pdf` (vector, editable) +
   `script/<name>.py` (reproducible).
7. **Report** which plot, palette, error type, and test were used.

### Statistics (opt-in)

Computed by `stats.py`, annotated with the **full test name**:

| Situation | Test | Annotation example |
|---|---|---|
| 2 groups, independent | Welch's t-test / Mann–Whitney U | `Welch's t-test, t = 7.17, P < 0.001` |
| 2 groups, paired | paired t-test / Wilcoxon signed-rank | `Wilcoxon signed-rank test, W = 3.0, P = 0.002` |
| 3+ groups | one-way ANOVA / Kruskal–Wallis (+ Holm posthoc) | `one-way ANOVA, F(3, 28) = 12.40, P < 0.001` |
| correlation | Pearson / Spearman | `Pearson correlation, r = 0.99, P < 0.001` |
| survival | log-rank | `log-rank test, chi2(1) = 6.1, P = 0.013` |
| beta diversity | **PERMANOVA** | `PERMANOVA, pseudo-F = 27.10, R² = 0.55, P = 0.001` |

Parametric vs non-parametric is auto-decided by a Shapiro–Wilk normality test and reported.
The skill never invents a test or fabricates significance.

---

## Supported plots

Comparison (bar+points, dot plot, grouped bar) · Distribution (box, violin, raincloud,
strip/swarm, histogram, KDE, ECDF) · Relationship (scatter+fit+CI, bubble, hexbin) ·
Trend (line+band, multi-line, area) · Composition (stacked / 100%-stacked, treemap, pie) ·
Ranking (ordered bar, lollipop) · Paired (slope, difference) · Effect size (forest /
coefficient) · Matrix (heatmap, clustermap, mosaic) · Survival (Kaplan–Meier, cumulative
incidence) · Agreement (Bland–Altman) · Multivariate (PCA, UMAP, PCoA) · Flow (Sankey/
alluvial, chord). The style module works with **any** matplotlib plot — this list is the
curated, intent-mapped set.

---

## Repository layout

```
.claude-plugin/plugin.json        plugin manifest
skills/scientific-data-viz/
  SKILL.md                        workflow + rules (skill entry point)
  plot-selection.md               data-nature -> best-plot guide
  journal_style.py                house-style module (palettes, legends, helpers)
  stats.py                        optional tests + PCoA / PERMANOVA
  palette_reference.py            render the palette swatch
  palette_reference.png           bundled swatch of all 20 palettes
  requirements.txt                Python deps
assets/                           example figures for this README
```

## License

[MIT](LICENSE)
