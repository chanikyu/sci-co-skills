<div align="center">

# 🧪 SciCo-Skills

### 科学研究と論文発表のための **Claude Code スキル** 集。

[English](../README.md) · [한국어](ko.md) · **日本語** · [中文](zh.md) · [Español](es.md)

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skills-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skills">
  <img src="https://img.shields.io/badge/version-1.2.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-2ca02c?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
</p>

データを自然言語で説明すれば、Claude が適切なスキルを実行します。
**コードで描画され、正確で、誠実な** 科学的アウトプット（多様性、統計、図）を生成します。

<img src="../assets/hero_gallery.png" width="90%" alt="Journal-style figures"/>

</div>

---

## 📦 スキル

| スキル | 機能 |
|---|---|
| 🧬 **[amplicon-analysis](../skills/amplicon-analysis)** | 16S/ITS マイクロバイオームパイプライン — 前処理 → **アルファ** 多様性と **ベータ** 多様性（距離、PCoA、PERMANOVA）→ **示差存在量** — ジャーナル品質の図付き。scikit-bio を利用し、図には `scientific-data-viz` を再利用します。 |
| 📊 **[scientific-data-viz](../skills/scientific-data-viz)** | 実データから作る論文品質のジャーナル図 — コードで描画するため、すべての値が正確です。20 のパレット、凡例の外側配置、任意の統計（t / ANOVA / Mann–Whitney / Kruskal / 相関 / log-rank / **PERMANOVA**）、構造化された `images/` + `script/` 出力。 |
| 🧫 **[scientific-workflow-viz](../skills/scientific-workflow-viz)** | BioRender スタイルの **コンセプト図イメージプロンプト**（ワークフロー / メカニズム / 比較）。Google の **Nano Banana**（Gemini image API）による直接描画も任意で可能です。 |

## 🚀 インストール

```bash
/plugin marketplace add chanikyu/SciCo-Skills
/plugin install SciCo-Skills
```

各スキルは Python の依存関係を `skills/<skill>/requirements.txt` に宣言します。仮想環境は初回使用時に作成されます。注意: **`amplicon-analysis` には Python ≤ 3.12 が必要です**（scikit-bio）。

---

## 🧬 amplicon-analysis

フィーチャーテーブル（カウントまたは相対存在量）＋サンプルメタデータから始まる、標準的な **16S/ITS マイクロバイオーム** ワークフローをエンドツーエンドで実行します:

1. **前処理** — カウントか相対存在量かを自動判定し、`sample_id` で結合（不一致を報告）、低出現頻度のフィーチャーをフィルタリング、任意のシード付きレアファクション、CLR。
2. **アルファ多様性** — observed / Shannon / Simpson / Pielou / Chao1 を、正式名称付きのグループ検定とともに算出。
3. **ベータ多様性** — Bray–Curtis / Jaccard → PCoA（分散の %）→ **PERMANOVA**。
4. **示差存在量** — `clr_test`（デフォルト、組成的）· `kruskal_lfc` · `pydeseq2`（任意）; BH-FDR。
5. **出力** — `tables/`、`images/`（ジャーナル図）、`script/`、および平易な言葉で書かれた `report.md`。

多様性 / PCoA / PERMANOVA には **scikit-bio** を使用し、図と正式名称付きの統計注釈には `scientific-data-viz` を再利用します。誠実さを設計思想としています: 手法としきい値を明示し、多重検定を補正し、レアファクションはオプトインで報告されます。

→ 完全ガイド: [`skills/amplicon-analysis`](../skills/amplicon-analysis)

---

## 📊 scientific-data-viz

実データを **Nature / Cell / eLife スタイル** の図に変換します。AI 画像生成ツールではなく、あなたの正確な数値を描画する `matplotlib` コードを書き、編集可能なベクター PDF と再現可能なスクリプトをエクスポートします。

|  |  |
|---|---|
| 🎯 **適切なプロットを自動で** | 意図ベースのガイドがデータの形状 → 最も明快なチャートへとマッピング |
| 🎨 **20 のパレット** | 色覚多様性に配慮 · ジャーナル（NPG/AAAS/NEJM/Lancet/JAMA）· 多カテゴリ（tab20/igv/kelly） |
| 📈 **任意の統計** | 検定の正式名称、PERMANOVA、Holm 補正済み事後検定 |
| 📁 **構造化された出力** | `images/*.png,*.pdf` + `script/*.py` |

<div align="center">
<img src="../assets/plot_catalogue.png" width="80%" alt="Plot catalogue"/>
<img src="../assets/palettes.png" width="66%" alt="Palettes"/>
</div>

→ 完全ガイド: [`skills/scientific-data-viz`](../skills/scientific-data-viz)

---

## 🧫 scientific-workflow-viz

BioRender スタイルの **コンセプト図イメージプロンプト** — ワークフロー、パイプライン、メカニズム、比較、タイムライン、マルチパネルのインフォグラフィック — を、FigureLabs / BioRender AI にそのまま貼り付けられる形で生成します。柔軟なレイアウトを備えた 5 ステップの手法（分析 → デザイン → コンポーネント → イラスト → プロンプト）。**任意で** プロンプトを Google の **Nano Banana**（Gemini image API）で直接画像に描画できます — キーを指定するだけです。

これは（背後にデータのない）模式図 / 図解に使用します。実データをプロットするには `scientific-data-viz` を使用してください。

→ 完全ガイド: [`skills/scientific-workflow-viz`](../skills/scientific-workflow-viz)

---

## 🔬 設計思想

- **近似ではなく正確に** — データ図はコードで描画され、値がねつ造されることはありません。
- **誠実な統計** — 使用した検定を正式名称で明示し、補正を適用し、何もでっち上げません。
- **再現可能** — 実行のたびにスクリプトと編集可能なベクター出力を生成します。
- **組み合わせ可能** — スキル同士が互いを再利用します（amplicon-analysis は scientific-data-viz を通じて描画します）。

---

<div align="center">

再現可能な科学のために [Claude Code](https://claude.com/claude-code) で作成 · [MIT](../LICENSE) ライセンス

</div>
