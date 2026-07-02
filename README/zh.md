<div align="center">

<img src="../assets/logo.png" width="150" alt="SciCo-Skills logo"/>

# SciCo-Skills

### 一套面向科学研究与论文发表的 **Claude Code skills** 集合。

[English](../README.md) · [한국어](ko.md) · [日本語](ja.md) · **中文** · [Español](es.md)

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skills-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skills">
  <img src="https://img.shields.io/badge/version-1.2.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-2ca02c?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
</p>

用自然语言描述你的数据，Claude 就会运行合适的 skill——生成
**由代码渲染、精确、诚实**的科学成果（多样性、统计、图表）。

</div>

---

## 📦 Skills

| Skill | 功能说明 |
|---|---|
| 🧬 **[amplicon-analysis](../skills/amplicon-analysis)** | 16S/ITS 微生物组流程——预处理 → **alpha** 与 **beta** 多样性（距离、PCoA、PERMANOVA）→ **差异丰度**——并配套期刊级图表。基于 scikit-bio，并复用 `scientific-data-viz` 生成图表。 |
| 📊 **[scientific-data-viz](../skills/scientific-data-viz)** | 从真实数据生成可发表的期刊级图表——由代码渲染，因此每一个数值都精确无误。20 种配色方案、图例置于图外、可选统计检验（t / ANOVA / Mann–Whitney / Kruskal / 相关性 / log-rank / **PERMANOVA**），并输出结构化的 `images/` 与 `script/`。 |
| 🧫 **[scientific-workflow-viz](../skills/scientific-workflow-viz)** | BioRender 风格的**概念图图像提示词**（工作流 / 机制 / 对比），并可选通过 Google **Nano Banana**（Gemini image API）直接渲染出图。 |

## 🚀 安装

```bash
/plugin marketplace add chanikyu/SciCo-Skills
/plugin install SciCo-Skills
```

每个 skill 都在 `skills/<skill>/requirements.txt` 中声明其 Python 依赖。首次使用时会自动创建虚拟
环境。注意：**`amplicon-analysis` 需要 Python ≤ 3.12**（scikit-bio）。

---

## 🧬 amplicon-analysis

标准的 **16S/ITS 微生物组**工作流，从特征表
（计数或相对丰度）+ 样本元数据出发，端到端完成：

1. **预处理**——自动识别计数与相对丰度，按 `sample_id` 连接（报告不匹配项），
   过滤低流行率特征，可选带种子的稀释（rarefaction），CLR。
2. **Alpha 多样性**——observed / Shannon / Simpson / Pielou / Chao1，并附带全称组间检验。
3. **Beta 多样性**——Bray–Curtis / Jaccard → PCoA（方差百分比）→ **PERMANOVA**。
4. **差异丰度**——`clr_test`（默认，成分数据）· `kruskal_lfc` · `pydeseq2`（可选）；BH-FDR。
5. **输出**——`tables/`、`images/`（期刊级图表）、`script/`，以及一份通俗易懂的 `report.md`。

多样性 / PCoA / PERMANOVA 使用 **scikit-bio**；图表与全称统计标注复用
`scientific-data-viz`。诚实为本的设计：方法与阈值明确说明、进行多重检验校正、
稀释为可选项并如实报告。

→ 完整指南：[`skills/amplicon-analysis`](../skills/amplicon-analysis)

---

## 📊 scientific-data-viz

把真实数据转化为 **Nature / Cell / eLife 风格**的图表。它并非 AI 图像生成器——
而是编写 `matplotlib` 代码，将你的确切数值渲染出来，随后导出可编辑的
矢量 PDF 以及一份可复现的脚本。

|  |  |
|---|---|
| 🎯 **自动选对图表** | 基于意图的指南将数据形态 → 映射到最清晰的图表 |
| 🎨 **20 种配色方案** | 色盲友好 · 期刊风（NPG/AAAS/NEJM/Lancet/JAMA）· 多类别（tab20/igv/kelly） |
| 📈 **可选统计检验** | 检验全称、PERMANOVA、Holm 校正的事后检验 |
| 📁 **结构化输出** | `images/*.png,*.pdf` + `script/*.py` |

<div align="center">
<img src="../assets/plot_catalogue.png" width="80%" alt="Plot catalogue"/>
<img src="../assets/palettes.png" width="66%" alt="Palettes"/>
</div>

→ 完整指南：[`skills/scientific-data-viz`](../skills/scientific-data-viz)

---

## 🧫 scientific-workflow-viz

BioRender 风格的**概念图图像提示词**——工作流、流程、机制、
对比、时间线或多面板信息图——可直接粘贴到 FigureLabs / BioRender
AI 中使用。采用 5 步方法（分析 → 设计 → 组件 → 插图 → 提示词），布局灵活。
**可选**通过 Google **Nano Banana**（Gemini image API）将提示词直接渲染成
图像——只需提供一个密钥即可。

用它来绘制示意图 / 图解（背后没有数据）；如需绘制真实数据，请使用 `scientific-data-viz`。

→ 完整指南：[`skills/scientific-workflow-viz`](../skills/scientific-workflow-viz)

---

## 🔬 设计理念

- **精确，而非近似**——数据图表由代码渲染；数值绝不臆造。
- **诚实的统计**——所用检验以全称标明；应用校正；不无中生有。
- **可复现**——每次运行都会输出脚本与可编辑的矢量成果。
- **可组合**——各 skill 相互复用（amplicon-analysis 通过 scientific-data-viz 渲染图表）。

---

<div align="center">

为可复现的科学而打造，基于 [Claude Code](https://claude.com/claude-code) · 采用 [MIT](../LICENSE) 许可证

</div>
