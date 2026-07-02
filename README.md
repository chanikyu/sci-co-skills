<div align="center">

<img src="assets/logo.png" width="150" alt="SciCo-Skills logo"/>

# SciCo-Skills

### A collection of **Claude Code skills** for scientific research & publication.

**English** · [한국어](README/ko.md) · [日本語](README/ja.md) · [中文](README/zh.md) · [Español](README/es.md)

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skills-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skills">
  <img src="https://img.shields.io/badge/version-1.3.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-2ca02c?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
  <a href="https://github.com/chanikyu/SciCo-Skills/wiki"><img src="https://img.shields.io/badge/docs-Wiki-4DBBD5?style=for-the-badge&logo=github&logoColor=white" alt="Wiki"></a>
</p>

Describe your data in natural language and Claude runs the right skill —
**code-rendered, exact, honest** science outputs (diversity, statistics, figures).

📖 **[Read the docs on the Wiki »](https://github.com/chanikyu/SciCo-Skills/wiki)**

</div>

---

## 📦 Skills

| Skill | What it does |
|---|---|
| 🧬 [amplicon-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/amplicon-analysis) | 16S/ITS microbiome pipeline — FASTQ (DADA2) or feature table → preprocess → **alpha** & **beta** diversity (distance, PCoA, PERMANOVA) → **differential abundance** — with journal figures. Enter at any stage; powered by scikit-bio; reuses `scientific-data-viz`. |
| 🦠 [shotgun-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/shotgun-analysis) | Shotgun metagenomics — QC + host removal → **read-based** profiling (MetaPhlAn / Kraken2+Bracken, HUMAnN) **or** **assembly-based** MAGs (MEGAHIT → MetaBAT2 + CONCOCT + SemiBin2 → DAS_Tool, CheckM2, GTDB-Tk) → diversity & **differential abundance**. Reuses the amplicon-analysis core. |
| 📊 [scientific-data-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-data-viz) | Publication-quality journal figures from real data — code-rendered so every value is exact. 20 palettes, legends outside, optional statistics (t / ANOVA / Mann–Whitney / Kruskal / correlation / log-rank / **PERMANOVA**), structured `images/` + `script/` output. |
| 🧫 [scientific-workflow-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-workflow-viz) | BioRender-style **concept-figure image prompts** (workflow / mechanism / comparison), with optional direct rendering via Google **Nano Banana** (Gemini image API). |

## 🚀 Quick start

```
/plugin marketplace add chanikyu/SciCo-Skills
/plugin install SciCo-Skills
```

Full setup on the [Installation](https://github.com/chanikyu/SciCo-Skills/wiki/Installation) page.

## 🔬 Design philosophy

- **Exact, not approximate** — data figures are code-rendered; values are never fabricated.
- **Honest statistics** — the test used is named in full; corrections applied; nothing invented.
- **Reproducible** — every run emits the script and editable vector outputs.
- **Composable** — skills reuse each other (amplicon-analysis renders through scientific-data-viz).

---

<div align="center">

[Documentation](https://github.com/chanikyu/SciCo-Skills/wiki) · [MIT](LICENSE) · made for reproducible science with [Claude Code](https://claude.com/claude-code)

</div>
