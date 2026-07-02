<div align="center">

<img src="../assets/logo.png" width="150" alt="SciCo-Skills logo"/>

# SciCo-Skills

### Una colección de **skills de Claude Code** para investigación científica y publicación.

[English](../README.md) · [한국어](ko.md) · [日本語](ja.md) · [中文](zh.md) · **Español**

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skills-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skills">
  <img src="https://img.shields.io/badge/version-1.2.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-2ca02c?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
  <a href="https://github.com/chanikyu/SciCo-Skills/wiki"><img src="https://img.shields.io/badge/docs-Wiki-4DBBD5?style=for-the-badge&logo=github&logoColor=white" alt="Wiki"></a>
</p>

Describe tus datos en lenguaje natural y Claude ejecuta la skill adecuada —
resultados científicos **renderizados por código, exactos y honestos** (diversidad, estadísticas, figuras).

</div>

---

## 📦 Skills

| Skill | Qué hace |
|---|---|
| 🧬 **[amplicon-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/amplicon-analysis)** | Pipeline de microbioma 16S/ITS — preprocesamiento → diversidad **alfa** y **beta** (distancia, PCoA, PERMANOVA) → **abundancia diferencial** — con figuras de revista. Impulsado por scikit-bio; reutiliza `scientific-data-viz` para las figuras. |
| 📊 **[scientific-data-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-data-viz)** | Figuras de revista con calidad de publicación a partir de datos reales — renderizadas por código, por lo que cada valor es exacto. 20 paletas, leyendas fuera del gráfico, estadísticas opcionales (t / ANOVA / Mann–Whitney / Kruskal / correlación / log-rank / **PERMANOVA**), salida estructurada en `images/` + `script/`. |
| 🧫 **[scientific-workflow-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-workflow-viz)** | **Prompts de imagen para figuras conceptuales** estilo BioRender (workflow / mecanismo / comparación), con renderizado directo opcional mediante Google **Nano Banana** (API de imágenes de Gemini). |

## 🚀 Instalación

```bash
/plugin marketplace add chanikyu/SciCo-Skills
/plugin install SciCo-Skills
```

Cada skill declara sus dependencias de Python en `skills/<skill>/requirements.txt`. Se crea un
entorno virtual en el primer uso. Nota: **`amplicon-analysis` requiere Python ≤ 3.12** (scikit-bio).

---

## 🧬 amplicon-analysis

El flujo de trabajo estándar de **microbioma 16S/ITS**, de principio a fin, a partir de una tabla
de características (conteos o abundancia relativa) + metadatos de las muestras:

1. **Preprocesamiento** — detecta automáticamente conteos vs. relativa, une por `sample_id` (reporta discrepancias),
   filtra características de baja prevalencia, rarefacción opcional con semilla, CLR.
2. **Diversidad alfa** — observed / Shannon / Simpson / Pielou / Chao1, con una prueba de grupo con nombre completo.
3. **Diversidad beta** — Bray–Curtis / Jaccard → PCoA (% de varianza) → **PERMANOVA**.
4. **Abundancia diferencial** — `clr_test` (predeterminado, composicional) · `kruskal_lfc` · `pydeseq2` (opcional); BH-FDR.
5. **Salida** — `tables/`, `images/` (figuras de revista), `script/` y un `report.md` en lenguaje sencillo.

La diversidad/PCoA/PERMANOVA usan **scikit-bio**; las figuras y las anotaciones estadísticas con nombre completo reutilizan
`scientific-data-viz`. Honesto por diseño: los métodos y umbrales se declaran, las pruebas múltiples se
corrigen, la rarefacción es opcional y se reporta.

→ Guía completa: [`amplicon-analysis`](https://github.com/chanikyu/SciCo-Skills/wiki/amplicon-analysis)

---

## 📊 scientific-data-viz

Convierte datos reales en figuras **estilo Nature / Cell / eLife**. No es un generador de imágenes con IA —
escribe código `matplotlib` que renderiza tus números exactos, y luego exporta un
PDF vectorial editable más un script reproducible.

|  |  |
|---|---|
| 🎯 **El gráfico correcto, automáticamente** | Una guía basada en la intención mapea la forma de los datos → el gráfico más claro |
| 🎨 **20 paletas** | Seguras para daltonismo · de revista (NPG/AAAS/NEJM/Lancet/JAMA) · para muchas categorías (tab20/igv/kelly) |
| 📈 **Estadísticas opcionales** | Nombres completos de las pruebas, PERMANOVA, posthoc corregido por Holm |
| 📁 **Salida estructurada** | `images/*.png,*.pdf` + `script/*.py` |

<div align="center">
<img src="../assets/plot_catalogue.png" width="80%" alt="Plot catalogue"/>
<img src="../assets/palettes.png" width="66%" alt="Palettes"/>
</div>

→ Guía completa: [`scientific-data-viz`](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-data-viz)

---

## 🧫 scientific-workflow-viz

**Prompts de imagen para figuras conceptuales** estilo BioRender — workflow, pipeline, mecanismo,
comparación, línea de tiempo o infografía multipanel — listos para pegar en FigureLabs / BioRender
AI. Un método de 5 pasos (analizar → diseñar → componentes → ilustraciones → prompt) con un diseño
flexible. **Opcionalmente**, renderiza el prompt directamente a una imagen con Google **Nano Banana**
(API de imágenes de Gemini) — solo proporciona una clave.

Usa esto para esquemas/diagramas (sin datos detrás); usa `scientific-data-viz` para graficar datos reales.

→ Guía completa: [`scientific-workflow-viz`](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-workflow-viz)

---

## 🔬 Filosofía de diseño

- **Exacto, no aproximado** — las figuras de datos se renderizan por código; los valores nunca se inventan.
- **Estadísticas honestas** — la prueba utilizada se nombra por completo; se aplican correcciones; nada se inventa.
- **Reproducible** — cada ejecución genera el script y salidas vectoriales editables.
- **Componible** — las skills se reutilizan entre sí (amplicon-analysis renderiza a través de scientific-data-viz).

---

<div align="center">

Hecho para la ciencia reproducible con [Claude Code](https://claude.com/claude-code) · licencia [MIT](../LICENSE)

</div>
