<div align="center">

# 📊 scientific-data-viz

### 真实数据 → 可直接投稿的期刊级图表。**精确数值，而非 AI 猜测。**

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · **中文** · [Español](README.es.md)

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skill-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/version-1.0.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-Apache%202.0-2ca02c?style=for-the-badge" alt="Apache 2.0">
  <img src="https://img.shields.io/badge/python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
  <img src="https://img.shields.io/badge/matplotlib-journal%20style-11557C?style=for-the-badge" alt="matplotlib">
</p>

一个 **Claude Code Skill**，将你的数据转化为 **Nature / Cell / eLife 风格**的图表 ——
由 `matplotlib` **以代码渲染**，让每一根柱子、每一个数据点、每一条误差线都与你的数值精确对应。

<img src="assets/hero_gallery.png" width="90%" alt="Multi-panel journal figure"/>

</div>

---

> [!IMPORTANT]
> **这不是 AI 图像生成器。** 图像模型会编造柱子高度、坐标轴和误差线。
> 本技能*编写绘图代码*，以简洁的期刊风格渲染你的**精确**数值 ——
> 并导出可编辑的矢量 **PDF** 以及可复现的**脚本**。

---

## ✨ 特性

|  |  |
|---|---|
| 🎯 **自动选对图表** | 基于意图的指南将你数据的形态映射到最清晰的图表类型 |
| 🧑‍🔬 **期刊标准样式** | 白色背景、无多余装饰、加粗面板字母、实心数据点、可编辑 PDF |
| 🔢 **精确数值** | 柱子从零起始，标注误差类型（SD/SEM/CI），不做平滑、不凭空捏造 |
| 🎨 **20 种配色方案** | 色盲友好 · 期刊配色（NPG/AAAS/NEJM/Lancet/JAMA）· 多类别（tab20/igv/kelly） |
| 📐 **图例置于图外** | 绝不遮挡数据 |
| 📈 **可选统计检验** | t / ANOVA / Mann–Whitney / Kruskal / 相关性 / log-rank / **PERMANOVA**，附完整检验名称 |
| 🔗 **数据表 + 元数据** | 按 `sample_id` 连接特征表与元数据文件（组学风格） |
| 📁 **结构化输出** | `images/*.png,*.pdf` + `script/*.py` |

---

## 🖼️ 示例

<div align="center">

**内置图表目录的一页** &nbsp;·&nbsp; **20 种配色色板**

<img src="assets/plot_catalogue.png" width="88%" alt="Plot catalogue"/>
<img src="assets/palettes.png" width="70%" alt="Color palettes"/>

</div>

---

## 🤖 这是什么？

`scientific-data-viz` 是一个面向 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 的 **Skill** ——
你无需运行命令行工具，只需**描述你的数据或想要的图表**，Claude 便会加载该技能。
触发它的提示词示例：

```text
"make a publication figure from this CSV"
"draw a journal-style taxonomy bar plot / PCoA"
"plot a Kaplan–Meier / forest plot / heatmap for my paper"
```

---

## 🚀 安装

**1. 将插件添加到 Claude Code**

```bash
/plugin marketplace add chanikyu/scientific-data-viz
/plugin install scientific-data-viz
```

**2. Python 依赖**（首次使用时会自动创建 venv，也可手动配置）

```bash
python3 -m venv venv
./venv/bin/pip install -r skills/scientific-data-viz/requirements.txt
```

需要 `matplotlib`、`numpy`、`scipy`、`pandas`、`squarify`。

---

## 🧬 使用方法

描述你的需求；该技能会执行一套固定的工作流：

1. **导入与检查** —— 数据类型、样本量、配对/纵向、不确定性。可接受
   单个数据表**或**特征表 **+ 一个单独的元数据文件**，二者按 `sample_id` 连接。
2. **选定图表**，通过选择指南（`plot-selection.md`）完成。
3. **询问配色方案**（展示 20 种配色色板；默认 `tab20`）。
4. **（可选）统计检验** —— 仅在你提出要求或提供原始重复数据时执行。
5. 以期刊风格**渲染**，图例置于图外。
6. **输出** `images/<name>.png`（300 dpi）+ `images/<name>.pdf`（矢量）+ `script/<name>.py`。
7. **报告**所用的图表类型、配色方案、误差类型和检验方法。

### 📈 统计检验（可选启用）—— 以**完整检验名称**标注

| 情形 | 检验 | 标注 |
|---|---|---|
| 2 组，独立 | Welch's t-test / Mann–Whitney U | `Welch's t-test, t = 7.17, P < 0.001` |
| 2 组，配对 | paired t-test / Wilcoxon signed-rank | `Wilcoxon signed-rank test, W = 3.0, P = 0.002` |
| 3 组及以上 | one-way ANOVA / Kruskal–Wallis（+ Holm 事后检验） | `one-way ANOVA, F(3, 28) = 12.40, P < 0.001` |
| 相关性 | Pearson / Spearman | `Pearson correlation, r = 0.99, P < 0.001` |
| 生存分析 | log-rank | `log-rank test, chi2(1) = 6.1, P = 0.013` |
| Beta 多样性 | **PERMANOVA** | `PERMANOVA, pseudo-F = 27.10, R² = 0.55, P = 0.001` |

参数检验与非参数检验由 Shapiro–Wilk 正态性检验自动判定并予以报告。
本技能绝不凭空编造检验，也绝不伪造显著性。

---

## 📚 支持的图表

`比较类` bar+points · dot · grouped bar &nbsp;|&nbsp;
`分布类` box · violin · raincloud · strip/swarm · histogram · KDE · ECDF &nbsp;|&nbsp;
`关系类` scatter+fit+CI · bubble · hexbin &nbsp;|&nbsp;
`趋势类` line+band · multi-line · area &nbsp;|&nbsp;
`构成类` stacked · 100%-stacked · treemap · pie &nbsp;|&nbsp;
`排序类` ordered bar · lollipop &nbsp;|&nbsp;
`配对类` slope · difference &nbsp;|&nbsp;
`效应量` forest / coefficient &nbsp;|&nbsp;
`矩阵类` heatmap · clustermap · mosaic &nbsp;|&nbsp;
`生存类` Kaplan–Meier · cumulative incidence &nbsp;|&nbsp;
`一致性` Bland–Altman &nbsp;|&nbsp;
`多变量` PCA · UMAP · PCoA &nbsp;|&nbsp;
`流向类` Sankey/alluvial · chord

样式模块适用于**任何** matplotlib 图表 —— 上述只是经过精选、按意图映射的图表集合。

---

<div align="center">

为可复现的科研而打造，基于 [Claude Code](https://claude.com/claude-code) · 采用 **Apache-2.0** 许可

</div>
