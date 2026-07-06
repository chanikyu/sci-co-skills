<div align="center">

<img src="../assets/logo.png" width="150" alt="SciCo-Skills logo"/>

# SciCo-Skills

### Una colección de **skills de Claude Code** para investigación científica y publicación.

[English](../README.md) · [한국어](ko.md) · [日本語](ja.md) · [中文](zh.md) · **Español**

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skills-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skills">
  <img src="https://img.shields.io/badge/version-1.11.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-2ca02c?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
  <a href="https://github.com/chanikyu/SciCo-Skills/wiki"><img src="https://img.shields.io/badge/docs-Wiki-4DBBD5?style=for-the-badge&logo=github&logoColor=white" alt="Wiki"></a>
</p>

Describe tus datos en lenguaje natural y Claude ejecuta la skill adecuada —
resultados científicos **renderizados por código, exactos y honestos** (diversidad, estadísticas, figuras).

📖 **[Lee la documentación en la Wiki »](https://github.com/chanikyu/SciCo-Skills/wiki)**

</div>

---

## 📦 Skills

| Skill | Qué hace |
|---|---|
| 🧬 [amplicon-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/amplicon-analysis) | Pipeline de microbioma 16S/ITS — FASTQ (DADA2) o tabla de features → preprocesado → diversidad alfa y beta (distancia, PCoA, PERMANOVA) → abundancia diferencial — con figuras de revista. Entra en cualquier etapa; basado en scikit-bio; reutiliza scientific-data-viz. |
| 🦠 [shotgun-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/shotgun-analysis) | Metagenómica shotgun — QC + eliminación del hospedador → perfilado basado en lecturas (MetaPhlAn / Kraken2+Bracken, HUMAnN) o MAGs basados en ensamblaje (MEGAHIT → MetaBAT2 + CONCOCT + SemiBin2 → DAS_Tool, CheckM2, GTDB-Tk) → diversidad y abundancia diferencial. Reutiliza el núcleo de amplicon-analysis. |
| 👾 [virome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/virome-analysis) | Viroma / fagos a partir de un metagenoma — identificación viral con geNomad → QC con CheckV → vOTUs (95% ANI/85% AF) → abundancia con CoverM (amplitud de cobertura ≥75%) → diversidad y abundancia diferencial. Reutiliza el núcleo de amplicon-analysis; se apoya en el ensamblaje de shotgun. |
| 💊 [resistome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/resistome-analysis) | Resistoma / AMR de comunidad a partir de las lecturas de un metagenoma — detección de ARG (RGI/CARD, DeepARG, AMR++/MEGARes) → hAMRonization → normalización (RPKM + por célula) → agregación por clase de fármaco → ARG × muestras → diversidad y diferencial. Reutiliza el núcleo de amplicon-analysis (frente a amr-profiling para un único aislado). |
| 🧭 [strain-tracking](https://github.com/chanikyu/SciCo-Skills/wiki/strain-tracking) | Seguimiento de cepas a lo largo de una cohorte de metagenomas — compartición / transmisión / persistencia de una misma cepa: perfilado por muestra (StrainPhlAn 4; inStrain popANI ≥99.999%) → matrices de distancia de cepas por especie → una red de compartición + persistencia longitudinal. Para una cohorte de metagenomas (frente a strain-typing para un único aislado). |
| 🔬 [genome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/genome-analysis) | Backbone de genoma de aislado bacteriano — FASTQ o contigs → QC → ensamblaje (SPAdes/Unicycler/Shovill/SKESA/Flye/Canu/Raven) → QC del ensamblaje (QUAST, CheckM2) → anotación (Bakta/Prokka) → identificación de especie (GTDB-Tk/ANI). Entra en cualquier etapa. |
| 🏷️ [strain-typing](https://github.com/chanikyu/SciCo-Skills/wiki/strain-typing) | Tipificación de cepas de genomas ensamblados — tipo de secuencia MLST (mlst), serotipado opcional (SISTR/ECTyper) y cgMLST (chewBBACA). |
| 🛡️ [amr-profiling](https://github.com/chanikyu/SciCo-Skills/wiki/amr-profiling) | Cribado de genomas ensamblados para genes de AMR, factores de virulencia y replicones de plásmidos — AMRFinderPlus + abricate (CARD/ResFinder, VFDB, PlasmidFinder). |
| 📈 [transcriptome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/transcriptome-analysis) | RNA-seq masivo (bulk) — FASTQ o matriz de conteos → QC → cuantificación (Salmon/kallisto/STAR vía --aligner) → expresión diferencial (pydeseq2) → enriquecimiento, con PCA / volcano / heatmap. Entra en cualquier etapa. |
| ⚛️ [metabolomics-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/metabolomics-analysis) | Metabolómica upstream — LC-MS/GC-MS crudo (mzML/.CDF) → detección de features (asari/XCMS · eRah/MS-DIAL) → alineamiento → QC (RSD, deriva QC-RLSC) → anotación (matchms, niveles MSI) → tabla de features anotada. Pasa el testigo a microbiome-metabolome-analysis. |
| 🧪 [metatranscriptome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/metatranscriptome-analysis) | RNA-seq de comunidad — QC + eliminación del hospedador → eliminación de rRNA (SortMeRNA) → perfilado funcional (HUMAnN) y taxonómico (MetaPhlAn) de la comunidad activa → diversidad y abundancia diferencial. Reutiliza el núcleo de shotgun + amplicon. |
| ⚗️ [microbiome-metabolome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/microbiome-metabolome-analysis) | Metabolómica a partir de una tabla de features anotada — filtrado/imputación → PQN → log+Pareto → univariante (BH-FDR, volcano) → PCA / PLS-DA + VIP + permutación → heatmap; ORA de rutas opcional. |
| 🔗 [microbiome-multiomics-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/microbiome-multiomics-analysis) | Integra metagenoma + metatranscriptoma + metaboloma emparejados — CLR/log por ómica → PERMANOVA → red de Spearman inter-ómica (BH-FDR) → concordancia por Procrustes/Mantel; MOFA+ opcional. |
| 📊 [scientific-data-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-data-viz) | Figuras de revista con calidad de publicación a partir de datos reales — renderizadas por código, de modo que cada valor es exacto. 20 paletas, leyendas fuera del gráfico, estadísticas opcionales (t / ANOVA / Mann–Whitney / Kruskal / correlación / log-rank / **PERMANOVA**), salida estructurada en `images/` + `script/`. |
| 🧫 [scientific-workflow-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-workflow-viz) | **Prompts de imagen para figuras conceptuales** estilo BioRender (flujo de trabajo / mecanismo / comparación), con renderizado directo opcional mediante Google **Nano Banana** (API de imágenes de Gemini). |
| 🛠️ [bioinfo-tool-builder](https://github.com/chanikyu/SciCo-Skills/wiki/bioinfo-tool-builder) | Construye de forma autónoma una nueva herramienta bioinformática a partir de un objetivo de investigación — estudio profundo de artículos/herramientas → diseño de algoritmo → viabilidad → benchmark honesto frente a los competidores reales (más cerca de la verdad), aislado en conda, revisión de dos lentes, CLI de baja fricción. Informa solo en 4 gates. |

## 🚀 Inicio rápido

```
/plugin marketplace add chanikyu/SciCo-Skills
/plugin install scico-skills
```

Configuración completa en la página de [Instalación](https://github.com/chanikyu/SciCo-Skills/wiki/Installation).

## 🔬 Filosofía de diseño

- **Exacto, no aproximado** — las figuras de datos se renderizan por código; los valores nunca se inventan.
- **Estadística honesta** — la prueba utilizada se nombra por completo; se aplican las correcciones; nada se inventa.
- **Reproducible** — cada ejecución emite el script y salidas vectoriales editables.
- **Componible** — las skills se reutilizan entre sí (amplicon-analysis renderiza a través de scientific-data-viz).
- **Effortless** — las herramientas se construyen con baja fricción (CLI de un comando, valores por defecto sensatos, IO estándar).

---

<div align="center">

[Documentación](https://github.com/chanikyu/SciCo-Skills/wiki) · [MIT](../LICENSE) · hecho para la ciencia reproducible con [Claude Code](https://claude.com/claude-code)

</div>
