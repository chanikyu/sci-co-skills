<div align="center">

# 📊 scientific-data-viz

### Real data → publication-ready journal figures. **Exact values, not AI guesses.**

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skill-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/version-1.0.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-2ca02c?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
  <img src="https://img.shields.io/badge/matplotlib-journal%20style-11557C?style=for-the-badge" alt="matplotlib">
</p>

A **Claude Code Skill** that turns your data into **Nature / Cell / eLife-style** figures —
**code-rendered** with `matplotlib` so every bar, point, and error bar matches your numbers.

<img src="assets/hero_multipanel.png" width="90%" alt="Multi-panel journal figure"/>

</div>

---

> [!IMPORTANT]
> **This is not an AI image generator.** Image models fabricate bar heights, axes, and
> error bars. This skill *writes plotting code* that renders your **exact** values in a
> clean journal style — and exports an editable vector **PDF** plus a reproducible **script**.

---

## ✨ Features

|  |  |
|---|---|
| 🎯 **Right plot, automatically** | Intent-based guide maps your data's shape to the clearest chart |
| 🧑‍🔬 **Journal house style** | White background, no chrome, bold panel letters, filled points, editable PDF |
| 🔢 **Exact values** | Bars start at zero, error type (SD/SEM/CI) labeled, nothing smoothed or invented |
| 🎨 **20 color palettes** | Colorblind-safe · journal (NPG/AAAS/NEJM/Lancet/JAMA) · many-category (tab20/igv/kelly) |
| 📐 **Legends outside** | Never overlap the data |
| 📈 **Optional statistics** | t / ANOVA / Mann–Whitney / Kruskal / correlation / log-rank / **PERMANOVA**, full test names |
| 🔗 **Table + metadata** | Join a feature table and a metadata file on `sample_id` (omics-style) |
| 📁 **Structured output** | `images/*.png,*.pdf` + `script/*.py` |

---

## 🖼️ Examples

<div align="center">

**Taxonomy bar plot** — many-category palette, legend outside the plot

<img src="assets/example_taxonomy_barplot.png" width="88%" alt="Taxonomy bar plot"/>

<table>
  <tr>
    <td width="50%" valign="top">
      <img src="assets/example_alpha_diversity.png" width="100%" alt="Alpha diversity"/>
      <br/><sub><b>Alpha diversity</b> — box + points, with the <b>computed</b> test written out in full</sub>
    </td>
    <td width="50%" valign="top">
      <img src="assets/example_beta_pcoa.png" width="100%" alt="Beta diversity PCoA"/>
      <br/><sub><b>Beta diversity (PCoA)</b> — % variance axes + <b>PERMANOVA</b></sub>
    </td>
  </tr>
</table>

**A page of the built-in plot catalogue** &nbsp;·&nbsp; **the 20-palette swatch**

<img src="assets/plot_catalogue.png" width="88%" alt="Plot catalogue"/>
<img src="assets/palettes.png" width="70%" alt="Color palettes"/>

</div>

---

## 🤖 What is this?

`scientific-data-viz` is a **Skill** for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) —
you don't run a CLI, you just **describe your data or figure** and Claude loads the skill.
Prompts that trigger it:

```text
"이 CSV로 논문 figure 그려줘"          "make a publication figure from this data"
"저널 스타일 taxonomy barplot / PCoA"   "draw a Kaplan–Meier / forest plot / heatmap for my paper"
```

---

## 🚀 Installation

**1. Add the plugin to Claude Code**

```bash
/plugin marketplace add chanikyu/scientific-data-viz
/plugin install scientific-data-viz
```

**2. Python dependencies** (a venv is created on first use, or set it up manually)

```bash
python3 -m venv venv
./venv/bin/pip install -r skills/scientific-data-viz/requirements.txt
```

Requires `matplotlib`, `numpy`, `scipy`, `pandas`, `squarify`.

---

## 🧬 Usage

Describe what you want; the skill runs a fixed workflow:

1. **Ingest & inspect** — types, sample size, paired/longitudinal, uncertainty. Accepts a
   single table **or** a feature table **+ a separate metadata file** joined on `sample_id`.
2. **Pick the plot** via the selection guide (`plot-selection.md`).
3. **Ask which palette** (shows the 20-palette swatch; default `tab20`).
4. **(Optional) statistics** — only when you ask or provide raw replicates.
5. **Render** in journal style, legends outside.
6. **Output** `images/<name>.png` (300 dpi) + `images/<name>.pdf` (vector) + `script/<name>.py`.
7. **Report** which plot, palette, error type, and test were used.

### 📈 Statistics (opt-in) — annotated with the **full test name**

| Situation | Test | Annotation |
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

## 📚 Supported plots

`Comparison` bar+points · dot · grouped bar &nbsp;|&nbsp;
`Distribution` box · violin · raincloud · strip/swarm · histogram · KDE · ECDF &nbsp;|&nbsp;
`Relationship` scatter+fit+CI · bubble · hexbin &nbsp;|&nbsp;
`Trend` line+band · multi-line · area &nbsp;|&nbsp;
`Composition` stacked · 100%-stacked · treemap · pie &nbsp;|&nbsp;
`Ranking` ordered bar · lollipop &nbsp;|&nbsp;
`Paired` slope · difference &nbsp;|&nbsp;
`Effect size` forest / coefficient &nbsp;|&nbsp;
`Matrix` heatmap · clustermap · mosaic &nbsp;|&nbsp;
`Survival` Kaplan–Meier · cumulative incidence &nbsp;|&nbsp;
`Agreement` Bland–Altman &nbsp;|&nbsp;
`Multivariate` PCA · UMAP · PCoA &nbsp;|&nbsp;
`Flow` Sankey/alluvial · chord

The style module works with **any** matplotlib plot — this is just the curated, intent-mapped set.

---

## 🗂️ Repository layout

```
.claude-plugin/plugin.json        plugin manifest
skills/scientific-data-viz/
  SKILL.md                        workflow + rules (skill entry point)
  plot-selection.md               data-nature -> best-plot guide
  journal_style.py                house-style module (palettes, legends, helpers)
  stats.py                        optional tests + PCoA / PERMANOVA
  palette_reference.py / .png     the 20-palette swatch
  requirements.txt                Python deps
assets/                           example figures for this README
```

---

<div align="center">

Made for reproducible science with [Claude Code](https://claude.com/claude-code) · **MIT** licensed

</div>
