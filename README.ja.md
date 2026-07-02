<div align="center">

# 🧪 sci-co-skills

### 科学研究と論文発表のための **Claude Code スキル** 集。

[English](README.md) · [한국어](README.ko.md) · **日本語** · [中文](README.zh.md) · [Español](README.es.md)

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skills-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skills">
  <img src="https://img.shields.io/badge/version-1.1.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-2ca02c?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
</p>

自然言語でデータを説明するだけで、Claude が適切なスキルを実行します —
**コード描画・正確・誠実** な科学的アウトプット（図、多様性、統計）。

<img src="assets/hero_gallery.png" width="90%" alt="Journal-style figures"/>

</div>

---

## 📦 スキル

| スキル | 機能 |
|---|---|
| 📊 **[scientific-data-viz](skills/scientific-data-viz)** | 実データから論文投稿レベルのジャーナル図を作成 — コード描画なので、すべての値が正確です。20種のパレット、外側に配置する凡例、オプションの統計（t / ANOVA / Mann–Whitney / Kruskal / 相関 / log-rank / **PERMANOVA**）、構造化された `images/` + `script/` 出力。 |
| 🧬 **[amplicon-analysis](skills/amplicon-analysis)** | 16S/ITS マイクロバイオームパイプライン — 前処理 → **アルファ** & **ベータ** 多様性（距離、PCoA、PERMANOVA）→ **示差存在量** — ジャーナル図付き。scikit-bio を採用し、図の描画には `scientific-data-viz` を再利用します。 |

## 🚀 インストール

```bash
/plugin marketplace add chanikyu/sci-co-skills
/plugin install sci-co-skills
```

各スキルは Python の依存関係を `skills/<skill>/requirements.txt` に宣言します。仮想環境は初回使用時に作成されます。注意：**`amplicon-analysis` には Python ≤ 3.12 が必要です**（scikit-bio）。

---

## 📊 scientific-data-viz

実データを **Nature / Cell / eLife スタイル** の図に変換します。AI 画像生成ツールではなく、
あなたの正確な数値を描画する `matplotlib` コードを書き、編集可能な
ベクター PDF と再現可能なスクリプトを出力します。

|  |  |
|---|---|
| 🎯 **適切なプロットを自動で** | 意図ベースのガイドがデータの形状を最も明快なチャートに対応づけます |
| 🎨 **20種のパレット** | 色覚多様性に配慮 · ジャーナル（NPG/AAAS/NEJM/Lancet/JAMA）· 多カテゴリ（tab20/igv/kelly） |
| 📈 **オプションの統計** | 検定名を省略せず記載、PERMANOVA、Holm 補正付き事後検定 |
| 📁 **構造化された出力** | `images/*.png,*.pdf` + `script/*.py` |

<div align="center">
<img src="assets/plot_catalogue.png" width="80%" alt="Plot catalogue"/>
<img src="assets/palettes.png" width="66%" alt="Palettes"/>
</div>

→ 完全ガイド：[`skills/scientific-data-viz`](skills/scientific-data-viz)

---

## 🧬 amplicon-analysis

標準的な **16S/ITS マイクロバイオーム** ワークフローを、特徴量テーブル
（カウントまたは相対存在量）+ サンプルメタデータから、エンドツーエンドで実行します：

1. **前処理** — カウントか相対存在量かを自動判定し、`sample_id` で結合（不一致を報告）、
   低頻度の特徴量をフィルタ、オプションでシード付きレアファクション、CLR。
2. **アルファ多様性** — observed / Shannon / Simpson / Pielou / Chao1、検定名を省略しない群間検定付き。
3. **ベータ多様性** — Bray–Curtis / Jaccard → PCoA（分散の %）→ **PERMANOVA**。
4. **示差存在量** — `clr_test`（デフォルト、組成的）· `kruskal_lfc` · `pydeseq2`（オプション）；BH-FDR。
5. **出力** — `tables/`、`images/`（ジャーナル図）、`script/`、そして平易な言葉の `report.md`。

多様性 / PCoA / PERMANOVA には **scikit-bio** を使用し、図と検定名を省略しない統計注記には
`scientific-data-viz` を再利用します。設計から誠実であること：手法と閾値を明記し、多重検定を
補正し、レアファクションはオプトインで報告します。

→ 完全ガイド：[`skills/amplicon-analysis`](skills/amplicon-analysis)

---

## 🔬 設計思想

- **近似ではなく正確に** — データ図はコード描画され、値が捏造されることはありません。
- **誠実な統計** — 使用した検定を省略せず記載し、補正を適用し、何も創作しません。
- **再現可能** — すべての実行がスクリプトと編集可能なベクター出力を生成します。
- **組み合わせ可能** — スキルは互いに再利用します（amplicon-analysis は scientific-data-viz を通じて描画します）。

---

<div align="center">

再現可能な科学のために [Claude Code](https://claude.com/claude-code) で作成 · [MIT](LICENSE) ライセンス

</div>
