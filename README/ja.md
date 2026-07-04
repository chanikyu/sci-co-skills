<div align="center">

<img src="../assets/logo.png" width="150" alt="SciCo-Skills logo"/>

# SciCo-Skills

### 科学研究・論文発表のための **Claude Code スキル** 集。

[English](../README.md) · [한국어](ko.md) · **日本語** · [中文](zh.md) · [Español](es.md)

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skills-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skills">
  <img src="https://img.shields.io/badge/version-1.7.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-2ca02c?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
  <a href="https://github.com/chanikyu/SciCo-Skills/wiki"><img src="https://img.shields.io/badge/docs-Wiki-4DBBD5?style=for-the-badge&logo=github&logoColor=white" alt="Wiki"></a>
</p>

データを自然言語で説明すれば、Claude が適切なスキルを実行し —
**コードで描画され、正確で、誠実な** 科学的アウトプット（多様性、統計、図）を生成します。

📖 **[Wiki でドキュメントを読む »](https://github.com/chanikyu/SciCo-Skills/wiki)**

</div>

---

## 📦 Skills

| Skill | 機能 |
|---|---|
| 🧬 [amplicon-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/amplicon-analysis) | 16S/ITS マイクロバイオームパイプライン — FASTQ(DADA2)または feature table → 前処理 → α・β多様性(距離, PCoA, PERMANOVA) → 差次的存在量 — ジャーナル図まで。任意のステージから開始可能; scikit-bio ベース; scientific-data-viz を再利用。 |
| 🦠 [shotgun-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/shotgun-analysis) | ショットガンメタゲノミクス — QC + 宿主除去 → リードベースのプロファイリング(MetaPhlAn / Kraken2+Bracken, HUMAnN)またはアセンブリベースの MAG(MEGAHIT → MetaBAT2 + CONCOCT + SemiBin2 → DAS_Tool, CheckM2, GTDB-Tk) → 多様性 & 差次的存在量。amplicon-analysis のコアを再利用。 |
| 🔬 [genome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/genome-analysis) | 細菌分離株ゲノムのバックボーン — FASTQ または contigs → QC → アセンブリ(SPAdes/Unicycler/Shovill/SKESA/Flye/Canu/Raven) → アセンブリQC(QUAST, CheckM2) → アノテーション(Bakta/Prokka) → 菌種同定(GTDB-Tk/ANI)。任意のステージから開始可能。 |
| 🏷️ [strain-typing](https://github.com/chanikyu/SciCo-Skills/wiki/strain-typing) | アセンブリゲノムの株タイピング — MLST sequence type(mlst)、オプションで serotyping(SISTR/ECTyper)と cgMLST(chewBBACA)。 |
| 🛡️ [amr-profiling](https://github.com/chanikyu/SciCo-Skills/wiki/amr-profiling) | アセンブリゲノムから AMR遺伝子・ビルレンス因子・プラスミドレプリコンをスクリーニング — AMRFinderPlus + abricate(CARD/ResFinder, VFDB, PlasmidFinder)。 |
| 📈 [transcriptome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/transcriptome-analysis) | バルク RNA-seq — FASTQ または count matrix → QC → 定量(Salmon/kallisto/STAR、--aligner) → 差次的発現(pydeseq2) → エンリッチメント、PCA/volcano/heatmap。任意のステージから開始可能。 |
| 🧪 [metatranscriptome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/metatranscriptome-analysis) | 群集 RNA-seq — QC + 宿主除去 → rRNA除去(SortMeRNA) → 機能(HUMAnN)・分類(MetaPhlAn)プロファイリング(活性群集) → 多様性 & 差次的存在量。shotgun+amplicon のコアを再利用。 |
| ⚗️ [microbiome-metabolome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/microbiome-metabolome-analysis) | アノテーション済み feature table からのメタボロミクス — フィルタリング/欠測値補完 → PQN → log+Pareto → 単変量解析(BH-FDR, volcano) → PCA / PLS-DA + VIP + 並べ替え検定 → ヒートマップ; オプションでパスウェイ ORA。 |
| 🔗 [microbiome-multiomics-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/microbiome-multiomics-analysis) | ペアリングされたメタゲノム + メタトランスクリプトーム + メタボロームを統合 — オミクスごとの CLR/log → PERMANOVA → オミクス間 Spearman ネットワーク(BH-FDR) → Procrustes/Mantel 一致性; オプションで MOFA+。 |
| 📊 [scientific-data-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-data-viz) | 実データから作る論文品質のジャーナル図 — コードで描画するため、すべての値が正確です。20 種類のパレット、凡例を図の外側に配置、任意の統計処理（t 検定 / ANOVA / Mann–Whitney / Kruskal / 相関 / log-rank / **PERMANOVA**）、構造化された `images/` + `script/` 出力。 |
| 🧫 [scientific-workflow-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-workflow-viz) | BioRender スタイルの **コンセプト図イメージプロンプト**（ワークフロー / メカニズム / 比較）。任意で Google の **Nano Banana**（Gemini 画像 API）による直接描画にも対応。 |
| 🛠️ [bioinfo-tool-builder](https://github.com/chanikyu/SciCo-Skills/wiki/bioinfo-tool-builder) | 研究目標から新しいバイオインフォマティクスツールを自律的に構築 — 論文・ツールの深い調査 → アルゴリズム設計 → 実現可能性 → 実際の競合ツールとの正直なベンチマーク(真の値により近く)、conda隔離、2レンズレビュー、低摩擦CLI。4つのゲートでのみ報告。 |

## 🚀 Quick start

```
/plugin marketplace add chanikyu/SciCo-Skills
/plugin install scico-skills
```

詳しいセットアップは [Installation](https://github.com/chanikyu/SciCo-Skills/wiki/Installation) ページをご覧ください。

## 🔬 Design philosophy

- **近似ではなく正確に** — データ図はコードで描画され、値が捏造されることはありません。
- **誠実な統計** — 使用した検定を正式名称で明記し、補正を適用し、何も創作しません。
- **再現可能** — 実行するたびにスクリプトと編集可能なベクター出力を生成します。
- **組み合わせ可能** — スキルは互いを再利用します（amplicon-analysis は scientific-data-viz を通じて描画します）。
- **Effortless** — ツールは低摩擦に構築(ワンコマンドCLI、妥当なデフォルト、標準IO)。

---

<div align="center">

[Documentation](https://github.com/chanikyu/SciCo-Skills/wiki) · [MIT](../LICENSE) · 再現可能な科学のために [Claude Code](https://claude.com/claude-code) で作成

</div>
