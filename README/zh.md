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
  <a href="https://github.com/chanikyu/SciCo-Skills/wiki"><img src="https://img.shields.io/badge/docs-Wiki-4DBBD5?style=for-the-badge&logo=github&logoColor=white" alt="Wiki"></a>
</p>

用自然语言描述你的数据，Claude 便会运行合适的 skill——
生成**由代码渲染、精确、诚实**的科学成果（多样性、统计、图表）。

📖 **[前往 Wiki 阅读文档 »](https://github.com/chanikyu/SciCo-Skills/wiki)**

</div>

---

## 📦 Skills

| Skill | 功能说明 |
|---|---|
| 🧬 [amplicon-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/amplicon-analysis) | 16S/ITS 微生物组流程——预处理 → **alpha** 与 **beta** 多样性（距离、PCoA、PERMANOVA）→ **差异丰度** ——并配套期刊级图表。基于 scikit-bio；图表部分复用 `scientific-data-viz`。 |
| 📊 [scientific-data-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-data-viz) | 从真实数据生成可发表的期刊级图表——由代码渲染，因此每个数值都精确无误。20 种配色方案、图例置于图外、可选统计检验（t / ANOVA / Mann–Whitney / Kruskal / 相关性 / log-rank / **PERMANOVA**），并输出结构化的 `images/` + `script/`。 |
| 🧫 [scientific-workflow-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-workflow-viz) | BioRender 风格的**概念图图像提示词**（工作流 / 机制 / 对比），可选通过 Google **Nano Banana**（Gemini 图像 API）直接渲染成图。 |

## 🚀 快速开始

```
/plugin marketplace add chanikyu/SciCo-Skills
/plugin install SciCo-Skills
```

完整安装说明请见 [Installation](https://github.com/chanikyu/SciCo-Skills/wiki/Installation) 页面。

## 🔬 设计理念

- **精确，而非近似**——数据图表由代码渲染；数值绝不臆造。
- **诚实的统计**——所用检验方法完整标明；应用相应校正；绝不编造。
- **可复现**——每次运行都会输出脚本以及可编辑的矢量图。
- **可组合**——各 skill 相互复用（amplicon-analysis 通过 scientific-data-viz 渲染图表）。

---

<div align="center">

[文档](https://github.com/chanikyu/SciCo-Skills/wiki) · [MIT](../LICENSE) · 为可复现的科学而打造，基于 [Claude Code](https://claude.com/claude-code)

</div>
