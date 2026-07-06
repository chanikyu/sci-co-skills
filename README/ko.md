<div align="center">

<img src="../assets/logo.png" width="150" alt="SciCo-Skills logo"/>

# SciCo-Skills

### 과학 연구와 논문 출판을 위한 **Claude Code 스킬** 모음.

[English](../README.md) · **한국어** · [日本語](ja.md) · [中文](zh.md) · [Español](es.md)

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skills-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skills">
  <img src="https://img.shields.io/badge/version-1.10.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-2ca02c?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
  <a href="https://github.com/chanikyu/SciCo-Skills/wiki"><img src="https://img.shields.io/badge/docs-Wiki-4DBBD5?style=for-the-badge&logo=github&logoColor=white" alt="Wiki"></a>
</p>

데이터를 자연어로 설명하면 Claude가 알맞은 스킬을 실행합니다 —
**코드로 렌더링되고, 정확하며, 정직한** 과학 결과물(다양성, 통계, 그림)을 만들어 냅니다.

📖 **[Wiki에서 문서 읽기 »](https://github.com/chanikyu/SciCo-Skills/wiki)**

</div>

---

## 📦 Skills

| Skill | 기능 |
|---|---|
| 🧬 [amplicon-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/amplicon-analysis) | 16S/ITS 마이크로바이옴 파이프라인 — FASTQ(DADA2) 또는 feature table → 전처리 → 알파·베타 다양성(거리, PCoA, PERMANOVA) → 차등 존재비 — 저널 그림까지. 어느 단계로도 진입 가능; scikit-bio 기반; scientific-data-viz 재사용. |
| 🦠 [shotgun-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/shotgun-analysis) | 샷건 메타지노믹스 — QC + 호스트 제거 → 리드 기반 프로파일링(MetaPhlAn / Kraken2+Bracken, HUMAnN) 또는 어셈블리 기반 MAG(MEGAHIT → MetaBAT2 + CONCOCT + SemiBin2 → DAS_Tool, CheckM2, GTDB-Tk) → 다양성 & 차등 존재비. amplicon-analysis 코어 재사용. |
| 👾 [virome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/virome-analysis) | 메타지놈에서 바이롬 / 파지 분석 — geNomad 바이러스 동정 → CheckV QC → vOTU(95% ANI / 85% AF) → CoverM 존재비(breadth ≥75%) → 다양성 & 차등. amplicon-analysis 코어를 재사용하고, shotgun 어셈블리 위에서 동작. |
| 💊 [resistome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/resistome-analysis) | 메타지놈의 리드로부터 얻는 레지스톰 / 군집 수준 AMR — ARG 검출(RGI/CARD, DeepARG, AMR++/MEGARes) → hAMRonization → 정규화(RPKM + 세포당) → 약물 계열별 집계 → ARG × 샘플 → 다양성 & 차등 분석. amplicon-analysis 코어를 재사용합니다(단일 분리균주 대상 amr-profiling과 대비). |
| 🔬 [genome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/genome-analysis) | 세균 분리균주 유전체 백본 — FASTQ 또는 contigs → QC → 조립(SPAdes/Unicycler/Shovill/SKESA/Flye/Canu/Raven) → 조립 QC(QUAST, CheckM2) → 주석(Bakta/Prokka) → 종 동정(GTDB-Tk/ANI). 어느 단계로도 진입. |
| 🏷️ [strain-typing](https://github.com/chanikyu/SciCo-Skills/wiki/strain-typing) | 조립 유전체 균주 타이핑 — MLST sequence type(mlst), 선택적 serotyping(SISTR/ECTyper) 및 cgMLST(chewBBACA). |
| 🛡️ [amr-profiling](https://github.com/chanikyu/SciCo-Skills/wiki/amr-profiling) | 조립 유전체에서 AMR 유전자·병원성 인자·플라스미드 replicon 스크리닝 — AMRFinderPlus + abricate(CARD/ResFinder, VFDB, PlasmidFinder). |
| 📈 [transcriptome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/transcriptome-analysis) | Bulk RNA-seq — FASTQ 또는 count matrix → QC → 정량(Salmon/kallisto/STAR, --aligner) → 차등발현(pydeseq2) → enrichment, PCA/volcano/heatmap. 어느 단계로도 진입. |
| ⚛️ [metabolomics-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/metabolomics-analysis) | 메타볼로믹스 업스트림 — 원시 LC-MS/GC-MS(mzML/.CDF) → 피처 검출(asari/XCMS · eRah/MS-DIAL) → 정렬 → QC(RSD, QC-RLSC 드리프트) → 주석(matchms, MSI 레벨) → 주석된 피처 테이블. microbiome-metabolome-analysis로 이어짐. |
| 🧪 [metatranscriptome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/metatranscriptome-analysis) | 군집 RNA-seq — QC + host 제거 → rRNA 제거(SortMeRNA) → 기능(HUMAnN)·분류(MetaPhlAn) 프로파일링(활성 군집) → 다양성 & 차등존재비. shotgun+amplicon 코어 재사용. |
| ⚗️ [microbiome-metabolome-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/microbiome-metabolome-analysis) | 주석된 피처 테이블에서 시작하는 메타볼로믹스 — 필터링/대치 → PQN → log+Pareto → 단변량(BH-FDR, 볼케이노) → PCA / PLS-DA + VIP + 순열검정 → 히트맵; 선택적 경로 ORA. |
| 🔗 [microbiome-multiomics-analysis](https://github.com/chanikyu/SciCo-Skills/wiki/microbiome-multiomics-analysis) | 짝지어진 메타지놈 + 메타전사체 + 메타볼롬 통합 — 오믹스별 CLR/log → PERMANOVA → 오믹스 간 Spearman 네트워크(BH-FDR) → Procrustes/Mantel 일치도; 선택적 MOFA+. |
| 📊 [scientific-data-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-data-viz) | 실제 데이터로 만드는 논문 품질의 저널 그림 — 코드로 렌더링되어 모든 값이 정확합니다. 20종 팔레트, 범례 바깥 배치, 선택적 통계(t / ANOVA / Mann–Whitney / Kruskal / 상관 / log-rank / **PERMANOVA**), 체계적인 `images/` + `script/` 출력. |
| 🧫 [scientific-workflow-viz](https://github.com/chanikyu/SciCo-Skills/wiki/scientific-workflow-viz) | BioRender 스타일의 **개념도 이미지 프롬프트**(워크플로우 / 메커니즘 / 비교), 선택적으로 Google **Nano Banana**(Gemini 이미지 API)를 통한 직접 렌더링 지원. |
| 🛠️ [bioinfo-tool-builder](https://github.com/chanikyu/SciCo-Skills/wiki/bioinfo-tool-builder) | 연구 목표로부터 새 생물정보 도구를 자동으로 개발 — 논문·도구 심층 조사 → 알고리즘 설계 → 타당성 → 실제 경쟁툴 대비 정직한 벤치마크(정답에 더 가깝게), conda 격리, 2렌즈 리뷰, 저마찰 CLI. 4개 게이트에서만 보고. |

## 🚀 Quick start

```
/plugin marketplace add chanikyu/SciCo-Skills
/plugin install scico-skills
```

전체 설정은 [Installation](https://github.com/chanikyu/SciCo-Skills/wiki/Installation) 페이지를 참고하세요.

## 🔬 Design philosophy

- **근사가 아닌 정확** — 데이터 그림은 코드로 렌더링되며, 값을 지어내지 않습니다.
- **정직한 통계** — 사용한 검정을 전체 이름으로 명시하고, 보정을 적용하며, 없는 것을 만들어 내지 않습니다.
- **재현 가능** — 실행할 때마다 스크립트와 편집 가능한 벡터 출력을 함께 내보냅니다.
- **조합 가능** — 스킬끼리 서로 재사용합니다(amplicon-analysis는 scientific-data-viz를 통해 렌더링).
- **Effortless** — 도구는 저마찰로 만든다(원커맨드 CLI, 합리적 기본값, 표준 IO).

---

<div align="center">

[Documentation](https://github.com/chanikyu/SciCo-Skills/wiki) · [MIT](../LICENSE) · [Claude Code](https://claude.com/claude-code)로 재현 가능한 과학을 위해 제작

</div>
