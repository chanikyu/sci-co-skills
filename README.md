<div align="center">

<img src="assets/logo.png" width="150" alt="SciCo-Skills logo"/>

# SciCo-Skills

### A collection of **Claude Code skills** for scientific research & publication.

**English** · [한국어](README/ko.md) · [日本語](README/ja.md) · [中文](README/zh.md) · [Español](README/es.md)

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skills-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skills">
  <img src="https://img.shields.io/badge/version-1.10.0-1f77b4?style=for-the-badge" alt="version">
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
| 👾 [virome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/virome-analysis) | **Virome / phages** from a metagenome — geNomad viral identification → CheckV QC → **vOTUs** (95% ANI/85% AF) → CoverM abundance (breadth ≥75%) → diversity & **differential**. Reuses the amplicon-analysis core; builds on shotgun assembly. |
| 💊 [resistome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/resistome-analysis) | **Resistome / community AMR** from a metagenome's reads — ARG detection (RGI/CARD, DeepARG, AMR++/MEGARes) → hAMRonization → normalize (RPKM + per-cell) → drug-class aggregation → ARG × samples → diversity & **differential**. Reuses the amplicon-analysis core (vs [amr-profiling](https://github.com/chanikyu/SciCo-Skills/wiki/amr-profiling) for a single isolate). |
| 🔬 [genome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/genome-analysis) | Bacterial **isolate genome** backbone — FASTQ or contigs → QC → assembly (SPAdes/Unicycler/Shovill/SKESA/Flye/Canu/Raven) → **assembly QC** (QUAST, CheckM2) → annotation (Bakta/Prokka) → **species ID** (GTDB-Tk/ANI). Enter at any stage. |
| 🏷️ [strain-typing](https://github.com/chanikyu/SciCo-Skills/wiki/strain-typing) | Strain typing of assembled genomes — **MLST** sequence type (mlst), optional **serotyping** (SISTR/ECTyper) and **cgMLST** (chewBBACA). |
| 🛡️ [amr-profiling](https://github.com/chanikyu/SciCo-Skills/wiki/amr-profiling) | Screen assembled genomes for **AMR genes**, **virulence factors**, and **plasmid replicons** — AMRFinderPlus + abricate (CARD/ResFinder, VFDB, PlasmidFinder). |
| 📈 [transcriptome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/transcriptome-analysis) | Bulk **RNA-seq** — FASTQ or count matrix → QC → quantify (Salmon/kallisto/STAR via `--aligner`) → **differential expression (pydeseq2)** → enrichment, with PCA / volcano / heatmap. Enter at any stage. |
| ⚛️ [metabolomics-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/metabolomics-analysis) | **Metabolomics upstream** — raw LC-MS/GC-MS (mzML/.CDF) → feature detection (asari/XCMS · eRah/MS-DIAL) → alignment → **QC (RSD, QC-RLSC drift)** → **annotation (matchms, MSI levels)** → annotated feature table. Hands off to microbiome-metabolome-analysis. |
| 🧪 [metatranscriptome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/metatranscriptome-analysis) | Community **RNA-seq** — QC + host removal → **rRNA removal (SortMeRNA)** → functional (HUMAnN) & taxonomic (MetaPhlAn) profiling of the active community → diversity & **differential abundance**. Reuses shotgun + amplicon core. |
| ⚗️ [microbiome-metabolome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/microbiome-metabolome-analysis) | **Metabolomics** from an annotated feature table — filtering/imputation → PQN → log+Pareto → univariate (BH-FDR, volcano) → PCA / **PLS-DA + VIP + permutation** → heatmap; optional pathway ORA. Enter at any stage. |
| 🔗 [microbiome-multiomics-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/microbiome-multiomics-analysis) | **Integrate** paired metagenome + metatranscriptome + metabolome — CLR/log per omic → per-omic **PERMANOVA** → cross-omic **Spearman network (BH-FDR)** → **Procrustes/Mantel** concordance; optional MOFA+. |
| 📊 [scientific-data-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-data-viz) | Publication-quality journal figures from real data — code-rendered so every value is exact. 20 palettes, legends outside, optional statistics (t / ANOVA / Mann–Whitney / Kruskal / correlation / log-rank / **PERMANOVA**), structured `images/` + `script/` output. |
| 🧫 [scientific-workflow-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-workflow-viz) | BioRender-style **concept-figure image prompts** (workflow / mechanism / comparison), with optional direct rendering via Google **Nano Banana** (Gemini image API). |
| 🛠️ [bioinfo-tool-builder](https://github.com/chanikyu/SciCo-Skills/wiki/bioinfo-tool-builder) | Autonomously **build a new bioinformatics tool** from a research goal — deep paper/tool survey → algorithm design → feasibility → **honest benchmark vs the real competitors** (closer to ground truth), conda-isolated, two-lens review, low-friction CLI. Reports only at 4 gates. |

## 🚀 Quick start

```
/plugin marketplace add chanikyu/SciCo-Skills
/plugin install scico-skills
```

Full setup on the [Installation](https://github.com/chanikyu/SciCo-Skills/wiki/Installation) page.

## 🔬 Design philosophy

- **Exact, not approximate** — data figures are code-rendered; values are never fabricated.
- **Honest statistics** — the test used is named in full; corrections applied; nothing invented.
- **Reproducible** — every run emits the script and editable vector outputs.
- **Composable** — skills reuse each other (amplicon-analysis renders through scientific-data-viz).
- **Effortless** — tools are built low-friction (one-command CLIs, sensible defaults, standard IO).

---

<div align="center">

[Documentation](https://github.com/chanikyu/SciCo-Skills/wiki) · [MIT](LICENSE) · made for reproducible science with [Claude Code](https://claude.com/claude-code)

</div>
