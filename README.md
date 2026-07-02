<div align="center">

# 🧪 sci-co-skills

### A collection of **Claude Code skills** for scientific research & publication.

**English** · [한국어](README.ko.md) · [日本語](README.ja.md) · [中文](README.zh.md) · [Español](README.es.md)

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skills-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skills">
  <img src="https://img.shields.io/badge/version-1.1.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-2ca02c?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
</p>

Describe your data in natural language and Claude runs the right skill —
**code-rendered, exact, honest** science outputs (figures, diversity, statistics).

<img src="assets/hero_gallery.png" width="90%" alt="Journal-style figures"/>

</div>

---

## 📦 Skills

| Skill | What it does |
|---|---|
| 📊 **[scientific-data-viz](skills/scientific-data-viz)** | Publication-quality journal figures from real data — code-rendered so every value is exact. 20 palettes, legends outside, optional statistics (t / ANOVA / Mann–Whitney / Kruskal / correlation / log-rank / **PERMANOVA**), structured `images/` + `script/` output. |
| 🧬 **[amplicon-analysis](skills/amplicon-analysis)** | 16S/ITS microbiome pipeline — preprocess → **alpha** & **beta** diversity (distance, PCoA, PERMANOVA) → **differential abundance** — with journal figures. Powered by scikit-bio; reuses `scientific-data-viz` for the figures. |

## 🚀 Installation

```bash
/plugin marketplace add chanikyu/sci-co-skills
/plugin install sci-co-skills
```

Each skill declares its Python dependencies in `skills/<skill>/requirements.txt`. A virtual
environment is created on first use. Note: **`amplicon-analysis` needs Python ≤ 3.12** (scikit-bio).

---

## 📊 scientific-data-viz

Turn real data into **Nature / Cell / eLife-style** figures. Not an AI image generator —
it writes `matplotlib` code that renders your exact numbers, then exports an editable
vector PDF plus a reproducible script.

|  |  |
|---|---|
| 🎯 **Right plot, automatically** | Intent-based guide maps data shape → the clearest chart |
| 🎨 **20 palettes** | Colorblind-safe · journal (NPG/AAAS/NEJM/Lancet/JAMA) · many-category (tab20/igv/kelly) |
| 📈 **Optional statistics** | Full test names, PERMANOVA, Holm-corrected posthoc |
| 📁 **Structured output** | `images/*.png,*.pdf` + `script/*.py` |

<div align="center">
<img src="assets/plot_catalogue.png" width="80%" alt="Plot catalogue"/>
<img src="assets/palettes.png" width="66%" alt="Palettes"/>
</div>

→ Full guide: [`skills/scientific-data-viz`](skills/scientific-data-viz)

---

## 🧬 amplicon-analysis

The standard **16S/ITS microbiome** workflow, end to end, from a feature table
(counts or relative abundance) + sample metadata:

1. **Preprocess** — auto-detect counts vs relative, join on `sample_id` (report mismatches),
   filter low-prevalence features, optional seeded rarefaction, CLR.
2. **Alpha diversity** — observed / Shannon / Simpson / Pielou / Chao1, with a full-name group test.
3. **Beta diversity** — Bray–Curtis / Jaccard → PCoA (% variance) → **PERMANOVA**.
4. **Differential abundance** — `clr_test` (default, compositional) · `kruskal_lfc` · `pydeseq2` (optional); BH-FDR.
5. **Output** — `tables/`, `images/` (journal figures), `script/`, and a plain-language `report.md`.

Diversity/PCoA/PERMANOVA use **scikit-bio**; figures and full-name stat annotations reuse
`scientific-data-viz`. Honest by design: methods and thresholds stated, multiple testing
corrected, rarefaction opt-in and reported.

→ Full guide: [`skills/amplicon-analysis`](skills/amplicon-analysis)

---

## 🔬 Design philosophy

- **Exact, not approximate** — data figures are code-rendered; values are never fabricated.
- **Honest statistics** — the test used is named in full; corrections applied; nothing invented.
- **Reproducible** — every run emits the script and editable vector outputs.
- **Composable** — skills reuse each other (amplicon-analysis renders through scientific-data-viz).

---

<div align="center">

Made for reproducible science with [Claude Code](https://claude.com/claude-code) · [MIT](LICENSE) licensed

</div>
