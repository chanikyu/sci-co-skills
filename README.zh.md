<div align="center">

# 🧪 sci-co-skills

### 一套面向科研与论文发表的 **Claude Code 技能**合集。

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · **中文** · [Español](README.es.md)

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skills-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skills">
  <img src="https://img.shields.io/badge/version-1.1.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-2ca02c?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
</p>

用自然语言描述你的数据，Claude 便会运行对应的技能 ——
产出**以代码渲染、精确、诚实**的科研成果（图表、多样性、统计）。

<img src="assets/hero_gallery.png" width="90%" alt="Journal-style figures"/>

</div>

---

## 📦 技能

| 技能 | 功能 |
|---|---|
| 📊 **[scientific-data-viz](skills/scientific-data-viz)** | 从真实数据生成可直接投稿的期刊级图表 —— 以代码渲染，每一个数值都精确无误。20 种配色方案、图例置于图外、可选统计检验（t / ANOVA / Mann–Whitney / Kruskal / 相关性 / log-rank / **PERMANOVA**），结构化的 `images/` + `script/` 输出。 |
| 🧬 **[amplicon-analysis](skills/amplicon-analysis)** | 16S/ITS 微生物组分析流程 —— 预处理 → **alpha** 与 **beta** 多样性（距离、PCoA、PERMANOVA）→ **差异丰度** —— 并附期刊级图表。由 scikit-bio 驱动；图表复用 `scientific-data-viz`。 |

## 🚀 安装

```bash
/plugin marketplace add chanikyu/sci-co-skills
/plugin install sci-co-skills
```

每个技能都在 `skills/<skill>/requirements.txt` 中声明其 Python 依赖。首次使用时会自动创建虚拟环境。注意：**`amplicon-analysis` 需要 Python ≤ 3.12**（scikit-bio）。

---

## 📊 scientific-data-viz

将真实数据转化为 **Nature / Cell / eLife 风格**的图表。它不是 AI 图像生成器 ——
它会编写 `matplotlib` 代码来渲染你的精确数值，然后导出可编辑的
矢量 PDF 以及可复现的脚本。

|  |  |
|---|---|
| 🎯 **自动选对图表** | 基于意图的指南将数据形态映射到最清晰的图表 |
| 🎨 **20 种配色方案** | 色盲友好 · 期刊配色（NPG/AAAS/NEJM/Lancet/JAMA）· 多类别（tab20/igv/kelly） |
| 📈 **可选统计检验** | 完整检验名称、PERMANOVA、Holm 校正的事后检验 |
| 📁 **结构化输出** | `images/*.png,*.pdf` + `script/*.py` |

<div align="center">
<img src="assets/plot_catalogue.png" width="80%" alt="Plot catalogue"/>
<img src="assets/palettes.png" width="66%" alt="Palettes"/>
</div>

→ 完整指南：[`skills/scientific-data-viz`](skills/scientific-data-viz)

---

## 🧬 amplicon-analysis

标准的 **16S/ITS 微生物组**工作流，从特征表
（计数或相对丰度）+ 样本元数据开始，端到端完成：

1. **预处理** —— 自动识别计数还是相对丰度，按 `sample_id` 连接（报告不匹配项），
   过滤低流行度特征，可选的带种子稀释（rarefaction），CLR。
2. **Alpha 多样性** —— observed / Shannon / Simpson / Pielou / Chao1，附带完整名称的组间检验。
3. **Beta 多样性** —— Bray–Curtis / Jaccard → PCoA（方差百分比）→ **PERMANOVA**。
4. **差异丰度** —— `clr_test`（默认，成分数据）· `kruskal_lfc` · `pydeseq2`（可选）；BH-FDR。
5. **输出** —— `tables/`、`images/`（期刊级图表）、`script/`，以及一份通俗易懂的 `report.md`。

多样性/PCoA/PERMANOVA 使用 **scikit-bio**；图表与完整名称的统计标注复用
`scientific-data-viz`。诚实为本：明确说明方法与阈值，进行多重检验
校正，稀释为可选项并如实报告。

→ 完整指南：[`skills/amplicon-analysis`](skills/amplicon-analysis)

---

## 🔬 设计理念

- **精确，而非近似** —— 数据图表以代码渲染；数值绝不凭空捏造。
- **诚实的统计** —— 完整写明所用检验；应用校正；绝不编造。
- **可复现** —— 每次运行都会输出脚本与可编辑的矢量文件。
- **可组合** —— 技能之间相互复用（amplicon-analysis 通过 scientific-data-viz 渲染图表）。

---

<div align="center">

为可复现的科研而打造，基于 [Claude Code](https://claude.com/claude-code) · 采用 [MIT](LICENSE) 许可

</div>
