<div align="center">

# 🧪 sci-co-skills

### 과학 연구와 논문 출판을 위한 **Claude Code 스킬** 모음.

[English](../README.md) · **한국어** · [日本語](ja.md) · [中文](zh.md) · [Español](es.md)

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skills-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skills">
  <img src="https://img.shields.io/badge/version-1.2.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-2ca02c?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
</p>

데이터를 자연어로 설명하면 Claude가 알맞은 스킬을 실행합니다 —
**코드로 렌더링되고, 정확하며, 정직한** 과학 결과물(다양성, 통계, 그림)을 만듭니다.

<img src="../assets/hero_gallery.png" width="90%" alt="Journal-style figures"/>

</div>

---

## 📦 스킬

| 스킬 | 기능 |
|---|---|
| 🧬 **[amplicon-analysis](../skills/amplicon-analysis)** | 16S/ITS 마이크로바이옴 파이프라인 — 전처리 → **알파** & **베타** 다양성(거리, PCoA, PERMANOVA) → **차등 존재비** — 논문용 그림 포함. scikit-bio 기반이며, 그림은 `scientific-data-viz`를 재사용합니다. |
| 📊 **[scientific-data-viz](../skills/scientific-data-viz)** | 실제 데이터로 만드는 논문 품질의 저널 그림 — 코드로 렌더링되어 모든 값이 정확합니다. 20종 팔레트, 범례 외부 배치, 선택적 통계(t / ANOVA / Mann–Whitney / Kruskal / 상관 / log-rank / **PERMANOVA**), 구조화된 `images/` + `script/` 출력. |
| 🧫 **[scientific-workflow-viz](../skills/scientific-workflow-viz)** | BioRender 스타일의 **개념도 이미지 프롬프트**(워크플로우 / 메커니즘 / 비교)이며, Google **Nano Banana**(Gemini 이미지 API)를 통한 직접 렌더링을 선택적으로 지원합니다. |

## 🚀 설치

```bash
/plugin marketplace add chanikyu/sci-co-skills
/plugin install sci-co-skills
```

각 스킬은 Python 의존성을 `skills/<skill>/requirements.txt`에 명시합니다. 가상 환경은 첫 사용 시 생성됩니다. 참고: **`amplicon-analysis`는 Python ≤ 3.12가 필요합니다**(scikit-bio).

---

## 🧬 amplicon-analysis

피처 테이블(카운트 또는 상대 존재비)과 샘플 메타데이터로부터 표준 **16S/ITS 마이크로바이옴** 워크플로우를 처음부터 끝까지 수행합니다:

1. **전처리** — 카운트 vs 상대 존재비 자동 감지, `sample_id` 기준 조인(불일치 보고), 저출현 피처 필터링, 선택적 시드 희석화(rarefaction), CLR.
2. **알파 다양성** — observed / Shannon / Simpson / Pielou / Chao1, 전체 이름 표기 그룹 검정 포함.
3. **베타 다양성** — Bray–Curtis / Jaccard → PCoA(% 분산) → **PERMANOVA**.
4. **차등 존재비** — `clr_test`(기본, 조성적) · `kruskal_lfc` · `pydeseq2`(선택); BH-FDR.
5. **출력** — `tables/`, `images/`(논문용 그림), `script/`, 그리고 쉬운 말로 쓴 `report.md`.

다양성/PCoA/PERMANOVA에는 **scikit-bio**를 사용하며, 그림과 전체 이름 표기 통계 주석은 `scientific-data-viz`를 재사용합니다. 설계 자체가 정직합니다: 방법과 임계값을 명시하고, 다중 검정을 보정하며, 희석화는 선택 사항이자 보고 대상입니다.

→ 전체 가이드: [`skills/amplicon-analysis`](../skills/amplicon-analysis)

---

## 📊 scientific-data-viz

실제 데이터를 **Nature / Cell / eLife 스타일** 그림으로 바꿉니다. AI 이미지 생성기가 아닙니다 — 당신의 정확한 수치를 렌더링하는 `matplotlib` 코드를 작성한 뒤, 편집 가능한 벡터 PDF와 재현 가능한 스크립트를 내보냅니다.

|  |  |
|---|---|
| 🎯 **알맞은 그래프를 자동으로** | 의도 기반 가이드가 데이터 형태 → 가장 명확한 차트로 매핑 |
| 🎨 **20종 팔레트** | 색각 이상 안전 · 저널(NPG/AAAS/NEJM/Lancet/JAMA) · 다범주(tab20/igv/kelly) |
| 📈 **선택적 통계** | 전체 검정 이름, PERMANOVA, Holm 보정 사후검정 |
| 📁 **구조화된 출력** | `images/*.png,*.pdf` + `script/*.py` |

<div align="center">
<img src="../assets/plot_catalogue.png" width="80%" alt="Plot catalogue"/>
<img src="../assets/palettes.png" width="66%" alt="Palettes"/>
</div>

→ 전체 가이드: [`skills/scientific-data-viz`](../skills/scientific-data-viz)

---

## 🧫 scientific-workflow-viz

BioRender 스타일의 **개념도 이미지 프롬프트** — 워크플로우, 파이프라인, 메커니즘, 비교, 타임라인, 다중 패널 인포그래픽 — FigureLabs / BioRender AI에 바로 붙여넣을 수 있습니다. 유연한 레이아웃을 갖춘 5단계 방법(분석 → 설계 → 구성 요소 → 일러스트 → 프롬프트). **선택적으로** Google **Nano Banana**(Gemini 이미지 API)로 프롬프트를 바로 이미지로 렌더링할 수 있습니다 — 키만 제공하면 됩니다.

배경 데이터가 없는 도식/다이어그램에는 이 스킬을, 실제 데이터를 플롯할 때는 `scientific-data-viz`를 사용하세요.

→ 전체 가이드: [`skills/scientific-workflow-viz`](../skills/scientific-workflow-viz)

---

## 🔬 설계 철학

- **근사가 아닌 정확** — 데이터 그림은 코드로 렌더링되며, 값은 결코 조작되지 않습니다.
- **정직한 통계** — 사용한 검정을 전체 이름으로 명시하고, 보정을 적용하며, 아무것도 지어내지 않습니다.
- **재현 가능** — 모든 실행마다 스크립트와 편집 가능한 벡터 출력을 남깁니다.
- **조합 가능** — 스킬들이 서로를 재사용합니다(amplicon-analysis는 scientific-data-viz를 통해 렌더링).

---

<div align="center">

재현 가능한 과학을 위해 [Claude Code](https://claude.com/claude-code)로 제작 · [MIT](../LICENSE) 라이선스

</div>
