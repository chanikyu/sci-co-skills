<div align="center">

# 📊 scientific-data-viz

### Datos reales → figuras de revista listas para publicar. **Valores exactos, no suposiciones de la IA.**

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [中文](README.zh.md) · **Español**

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skill-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/version-1.0.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-Apache%202.0-2ca02c?style=for-the-badge" alt="Apache 2.0">
  <img src="https://img.shields.io/badge/python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
  <img src="https://img.shields.io/badge/matplotlib-journal%20style-11557C?style=for-the-badge" alt="matplotlib">
</p>

Un **Skill de Claude Code** que convierte tus datos en figuras al **estilo de Nature / Cell / eLife** —
**renderizadas por código** con `matplotlib` para que cada barra, punto y barra de error coincida con tus números.

<img src="assets/hero_gallery.png" width="90%" alt="Multi-panel journal figure"/>

</div>

---

> [!IMPORTANT]
> **Esto no es un generador de imágenes con IA.** Los modelos de imagen inventan alturas de barras, ejes y
> barras de error. Este skill *escribe código de graficación* que renderiza tus valores **exactos** en un
> estilo de revista limpio, y exporta un **PDF** vectorial editable junto con un **script** reproducible.

---

## ✨ Características

|  |  |
|---|---|
| 🎯 **El gráfico correcto, automáticamente** | Una guía basada en la intención asigna la forma de tus datos al gráfico más claro |
| 🧑‍🔬 **Estilo propio de revista** | Fondo blanco, sin adornos, letras de panel en negrita, puntos rellenos, PDF editable |
| 🔢 **Valores exactos** | Las barras empiezan en cero, el tipo de error (SD/SEM/CI) se etiqueta, nada se suaviza ni se inventa |
| 🎨 **20 paletas de colores** | Seguras para daltónicos · de revista (NPG/AAAS/NEJM/Lancet/JAMA) · de muchas categorías (tab20/igv/kelly) |
| 📐 **Leyendas fuera del gráfico** | Nunca se superponen con los datos |
| 📈 **Estadística opcional** | t / ANOVA / Mann–Whitney / Kruskal / correlación / log-rank / **PERMANOVA**, con los nombres completos de las pruebas |
| 🔗 **Tabla + metadatos** | Une una tabla de características con un archivo de metadatos por `sample_id` (estilo ómico) |
| 📁 **Salida estructurada** | `images/*.png,*.pdf` + `script/*.py` |

---

## 🖼️ Ejemplos

<div align="center">

**Una página del catálogo de gráficos integrado** &nbsp;·&nbsp; **el muestrario de 20 paletas**

<img src="assets/plot_catalogue.png" width="88%" alt="Plot catalogue"/>
<img src="assets/palettes.png" width="70%" alt="Color palettes"/>

</div>

---

## 🤖 ¿Qué es esto?

`scientific-data-viz` es un **Skill** para [Claude Code](https://docs.anthropic.com/en/docs/claude-code) —
no ejecutas una CLI, solo **describes tus datos o tu figura** y Claude carga el skill.
Instrucciones que lo activan:

```text
"make a publication figure from this CSV"
"draw a journal-style taxonomy bar plot / PCoA"
"plot a Kaplan–Meier / forest plot / heatmap for my paper"
```

---

## 🚀 Instalación

**1. Añade el plugin a Claude Code**

```bash
/plugin marketplace add chanikyu/scientific-data-viz
/plugin install scientific-data-viz
```

**2. Dependencias de Python** (se crea un venv en el primer uso, o configúralo manualmente)

```bash
python3 -m venv venv
./venv/bin/pip install -r skills/scientific-data-viz/requirements.txt
```

Requiere `matplotlib`, `numpy`, `scipy`, `pandas`, `squarify`.

---

## 🧬 Uso

Describe lo que quieres; el skill ejecuta un flujo de trabajo fijo:

1. **Ingesta e inspección** — tipos, tamaño de muestra, datos apareados/longitudinales, incertidumbre. Acepta una
   sola tabla **o** una tabla de características **+ un archivo de metadatos separado** unidos por `sample_id`.
2. **Elige el gráfico** mediante la guía de selección (`plot-selection.md`).
3. **Pregunta qué paleta** usar (muestra el muestrario de 20 paletas; por defecto `tab20`).
4. **(Opcional) estadística** — solo cuando lo pides o proporcionas réplicas en bruto.
5. **Renderiza** al estilo de revista, con las leyendas fuera del gráfico.
6. **Salida** `images/<name>.png` (300 dpi) + `images/<name>.pdf` (vectorial) + `script/<name>.py`.
7. **Informa** de qué gráfico, paleta, tipo de error y prueba se usaron.

### 📈 Estadística (opcional) — anotada con el **nombre completo de la prueba**

| Situación | Prueba | Anotación |
|---|---|---|
| 2 grupos, independientes | prueba t de Welch / U de Mann–Whitney | `Welch's t-test, t = 7.17, P < 0.001` |
| 2 grupos, apareados | prueba t apareada / rangos con signo de Wilcoxon | `Wilcoxon signed-rank test, W = 3.0, P = 0.002` |
| 3+ grupos | ANOVA de una vía / Kruskal–Wallis (+ posthoc de Holm) | `one-way ANOVA, F(3, 28) = 12.40, P < 0.001` |
| correlación | Pearson / Spearman | `Pearson correlation, r = 0.99, P < 0.001` |
| supervivencia | log-rank | `log-rank test, chi2(1) = 6.1, P = 0.013` |
| diversidad beta | **PERMANOVA** | `PERMANOVA, pseudo-F = 27.10, R² = 0.55, P = 0.001` |

La elección entre paramétrico y no paramétrico se decide automáticamente mediante una prueba de normalidad de Shapiro–Wilk y se informa.
El skill nunca inventa una prueba ni fabrica significancia.

---

## 📚 Gráficos admitidos

`Comparación` barras+puntos · puntos · barras agrupadas &nbsp;|&nbsp;
`Distribución` caja · violín · raincloud · strip/swarm · histograma · KDE · ECDF &nbsp;|&nbsp;
`Relación` dispersión+ajuste+CI · burbujas · hexbin &nbsp;|&nbsp;
`Tendencia` línea+banda · multilínea · área &nbsp;|&nbsp;
`Composición` apilado · apilado al 100% · treemap · circular &nbsp;|&nbsp;
`Ranking` barras ordenadas · lollipop &nbsp;|&nbsp;
`Apareado` pendiente · diferencia &nbsp;|&nbsp;
`Tamaño del efecto` forest / coeficientes &nbsp;|&nbsp;
`Matriz` heatmap · clustermap · mosaico &nbsp;|&nbsp;
`Supervivencia` Kaplan–Meier · incidencia acumulada &nbsp;|&nbsp;
`Concordancia` Bland–Altman &nbsp;|&nbsp;
`Multivariante` PCA · UMAP · PCoA &nbsp;|&nbsp;
`Flujo` Sankey/aluvial · cuerda

El módulo de estilo funciona con **cualquier** gráfico de matplotlib — este es solo el conjunto curado y asignado por intención.

---

<div align="center">

Hecho para la ciencia reproducible con [Claude Code](https://claude.com/claude-code) · licencia **Apache-2.0**

</div>
