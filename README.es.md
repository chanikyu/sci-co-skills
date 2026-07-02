<div align="center">

# 🧪 sci-co-skills

### Una colección de **skills de Claude Code** para la investigación y publicación científica.

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [中文](README.zh.md) · **Español**

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skills-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skills">
  <img src="https://img.shields.io/badge/version-1.1.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-2ca02c?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
</p>

Describe tus datos en lenguaje natural y Claude ejecuta el skill adecuado —
resultados científicos **renderizados por código, exactos y honestos** (figuras, diversidad, estadística).

<img src="assets/hero_gallery.png" width="90%" alt="Journal-style figures"/>

</div>

---

## 📦 Skills

| Skill | Qué hace |
|---|---|
| 📊 **[scientific-data-viz](skills/scientific-data-viz)** | Figuras de revista con calidad de publicación a partir de datos reales — renderizadas por código para que cada valor sea exacto. 20 paletas, leyendas fuera del gráfico, estadística opcional (t / ANOVA / Mann–Whitney / Kruskal / correlación / log-rank / **PERMANOVA**), salida estructurada en `images/` + `script/`. |
| 🧬 **[amplicon-analysis](skills/amplicon-analysis)** | Pipeline de microbioma 16S/ITS — preprocesamiento → diversidad **alfa** y **beta** (distancia, PCoA, PERMANOVA) → **abundancia diferencial** — con figuras de revista. Basado en scikit-bio; reutiliza `scientific-data-viz` para las figuras. |

## 🚀 Instalación

```bash
/plugin marketplace add chanikyu/sci-co-skills
/plugin install sci-co-skills
```

Cada skill declara sus dependencias de Python en `skills/<skill>/requirements.txt`. Se crea un
entorno virtual en el primer uso. Nota: **`amplicon-analysis` necesita Python ≤ 3.12** (scikit-bio).

---

## 📊 scientific-data-viz

Convierte datos reales en figuras al **estilo de Nature / Cell / eLife**. No es un generador de imágenes con IA —
escribe código de `matplotlib` que renderiza tus números exactos y luego exporta un
PDF vectorial editable junto con un script reproducible.

|  |  |
|---|---|
| 🎯 **El gráfico correcto, automáticamente** | Una guía basada en la intención asigna la forma de tus datos → el gráfico más claro |
| 🎨 **20 paletas** | Seguras para daltónicos · de revista (NPG/AAAS/NEJM/Lancet/JAMA) · de muchas categorías (tab20/igv/kelly) |
| 📈 **Estadística opcional** | Nombres completos de las pruebas, PERMANOVA, posthoc con corrección de Holm |
| 📁 **Salida estructurada** | `images/*.png,*.pdf` + `script/*.py` |

<div align="center">
<img src="assets/plot_catalogue.png" width="80%" alt="Plot catalogue"/>
<img src="assets/palettes.png" width="66%" alt="Palettes"/>
</div>

→ Guía completa: [`skills/scientific-data-viz`](skills/scientific-data-viz)

---

## 🧬 amplicon-analysis

El flujo de trabajo estándar de **microbioma 16S/ITS**, de principio a fin, a partir de una tabla de características
(recuentos o abundancia relativa) + metadatos de muestra:

1. **Preprocesamiento** — detecta automáticamente recuentos frente a relativa, une por `sample_id` (informa de las discrepancias),
   filtra características de baja prevalencia, rarefacción opcional con semilla, CLR.
2. **Diversidad alfa** — observed / Shannon / Simpson / Pielou / Chao1, con una prueba de grupo con nombre completo.
3. **Diversidad beta** — Bray–Curtis / Jaccard → PCoA (% de varianza) → **PERMANOVA**.
4. **Abundancia diferencial** — `clr_test` (por defecto, composicional) · `kruskal_lfc` · `pydeseq2` (opcional); BH-FDR.
5. **Salida** — `tables/`, `images/` (figuras de revista), `script/` y un `report.md` en lenguaje sencillo.

La diversidad/PCoA/PERMANOVA usan **scikit-bio**; las figuras y las anotaciones estadísticas con nombre completo reutilizan
`scientific-data-viz`. Honesto por diseño: se declaran los métodos y umbrales, se corrigen las pruebas
múltiples, la rarefacción es opcional y se informa.

→ Guía completa: [`skills/amplicon-analysis`](skills/amplicon-analysis)

---

## 🔬 Filosofía de diseño

- **Exacto, no aproximado** — las figuras de datos se renderizan por código; los valores nunca se inventan.
- **Estadística honesta** — la prueba usada se nombra por completo; se aplican correcciones; nada se inventa.
- **Reproducible** — cada ejecución emite el script y salidas vectoriales editables.
- **Componible** — los skills se reutilizan entre sí (amplicon-analysis renderiza a través de scientific-data-viz).

---

<div align="center">

Hecho para la ciencia reproducible con [Claude Code](https://claude.com/claude-code) · licencia [MIT](LICENSE)

</div>
