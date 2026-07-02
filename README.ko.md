<div align="center">

# 📊 scientific-data-viz

### 실제 데이터 → 논문에 바로 쓰는 저널 그림. **AI의 추측이 아닌, 정확한 값.**

[English](README.md) · **한국어** · [日本語](README.ja.md) · [中文](README.zh.md) · [Español](README.es.md)

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-Skill-8A2BE2?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/version-1.0.0-1f77b4?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/badge/license-Apache%202.0-2ca02c?style=for-the-badge" alt="Apache 2.0">
  <img src="https://img.shields.io/badge/python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python">
  <img src="https://img.shields.io/badge/matplotlib-journal%20style-11557C?style=for-the-badge" alt="matplotlib">
</p>

여러분의 데이터를 **Nature / Cell / eLife 스타일** 그림으로 바꿔 주는 **Claude Code Skill** —
`matplotlib`으로 **코드 렌더링**하여 모든 막대, 점, 오차 막대가 여러분의 수치와 정확히 일치합니다.

<img src="assets/hero_gallery.png" width="90%" alt="Multi-panel journal figure"/>

</div>

---

> [!IMPORTANT]
> **이것은 AI 이미지 생성기가 아닙니다.** 이미지 모델은 막대 높이, 축, 오차 막대를
> 지어냅니다. 이 스킬은 여러분의 **정확한** 값을 깔끔한 저널 스타일로 렌더링하는
> *플로팅 코드를 작성*하고, 편집 가능한 벡터 **PDF**와 재현 가능한 **스크립트**까지 내보냅니다.

---

## ✨ 기능

|  |  |
|---|---|
| 🎯 **자동으로 알맞은 그림 선택** | 의도 기반 가이드가 데이터의 형태를 가장 명확한 차트에 매핑합니다 |
| 🧑‍🔬 **저널 하우스 스타일** | 흰 배경, 불필요한 장식 없음, 굵은 패널 문자, 채워진 점, 편집 가능한 PDF |
| 🔢 **정확한 값** | 막대는 0에서 시작하고, 오차 유형(SD/SEM/CI)을 표기하며, 아무것도 매끄럽게 하거나 지어내지 않습니다 |
| 🎨 **20종 컬러 팔레트** | 색각 이상 안전 · 저널(NPG/AAAS/NEJM/Lancet/JAMA) · 다범주(tab20/igv/kelly) |
| 📐 **범례는 바깥에** | 데이터와 절대 겹치지 않습니다 |
| 📈 **선택적 통계** | t / ANOVA / Mann–Whitney / Kruskal / 상관 / log-rank / **PERMANOVA**, 검정명 전체 표기 |
| 🔗 **테이블 + 메타데이터** | 피처 테이블과 메타데이터 파일을 `sample_id`로 결합(오믹스 스타일) |
| 📁 **구조화된 출력** | `images/*.png,*.pdf` + `script/*.py` |

---

## 🖼️ 예시

<div align="center">

**내장 플롯 카탈로그의 한 페이지** &nbsp;·&nbsp; **20종 팔레트 스와치**

<img src="assets/plot_catalogue.png" width="88%" alt="Plot catalogue"/>
<img src="assets/palettes.png" width="70%" alt="Color palettes"/>

</div>

---

## 🤖 이게 뭔가요?

`scientific-data-viz`는 [Claude Code](https://docs.anthropic.com/en/docs/claude-code)용 **스킬**입니다 —
CLI를 실행하는 게 아니라, 그저 **데이터나 그림을 설명**하면 Claude가 스킬을 불러옵니다.
이 스킬을 트리거하는 프롬프트 예시:

```text
"make a publication figure from this CSV"
"draw a journal-style taxonomy bar plot / PCoA"
"plot a Kaplan–Meier / forest plot / heatmap for my paper"
```

---

## 🚀 설치

**1. Claude Code에 플러그인 추가**

```bash
/plugin marketplace add chanikyu/scientific-data-viz
/plugin install scientific-data-viz
```

**2. Python 의존성** (첫 사용 시 venv가 생성되며, 수동으로 설정할 수도 있습니다)

```bash
python3 -m venv venv
./venv/bin/pip install -r skills/scientific-data-viz/requirements.txt
```

`matplotlib`, `numpy`, `scipy`, `pandas`, `squarify`가 필요합니다.

---

## 🧬 사용법

원하는 것을 설명하세요. 스킬은 정해진 워크플로우를 실행합니다:

1. **수집 및 검사** — 자료형, 표본 크기, 대응/종단 여부, 불확실성을 파악합니다. 단일
   테이블 **또는** 피처 테이블 **+ 별도의 메타데이터 파일**을 `sample_id`로 결합한 형태를 받습니다.
2. 선택 가이드(`plot-selection.md`)를 통해 **플롯을 고릅니다**.
3. **어떤 팔레트를 쓸지 묻습니다**(20종 팔레트 스와치를 보여주며, 기본값은 `tab20`).
4. **(선택) 통계** — 요청하거나 원시 반복값을 제공할 때만 수행합니다.
5. 범례를 바깥에 두고 저널 스타일로 **렌더링합니다**.
6. **출력** `images/<name>.png` (300 dpi) + `images/<name>.pdf` (벡터) + `script/<name>.py`.
7. 어떤 플롯, 팔레트, 오차 유형, 검정을 사용했는지 **보고합니다**.

### 📈 통계 (선택) — **검정명 전체**로 주석 표기

| 상황 | 검정 | 주석 |
|---|---|---|
| 2개 그룹, 독립 | Welch's t-test / Mann–Whitney U | `Welch's t-test, t = 7.17, P < 0.001` |
| 2개 그룹, 대응 | paired t-test / Wilcoxon signed-rank | `Wilcoxon signed-rank test, W = 3.0, P = 0.002` |
| 3개 이상 그룹 | one-way ANOVA / Kruskal–Wallis (+ Holm 사후검정) | `one-way ANOVA, F(3, 28) = 12.40, P < 0.001` |
| 상관 | Pearson / Spearman | `Pearson correlation, r = 0.99, P < 0.001` |
| 생존 | log-rank | `log-rank test, chi2(1) = 6.1, P = 0.013` |
| 베타 다양성 | **PERMANOVA** | `PERMANOVA, pseudo-F = 27.10, R² = 0.55, P = 0.001` |

모수/비모수 여부는 Shapiro–Wilk 정규성 검정으로 자동 판정하고 함께 보고합니다.
이 스킬은 검정을 지어내거나 유의성을 조작하지 않습니다.

---

## 📚 지원하는 플롯

`비교(Comparison)` bar+points · dot · grouped bar &nbsp;|&nbsp;
`분포(Distribution)` box · violin · raincloud · strip/swarm · histogram · KDE · ECDF &nbsp;|&nbsp;
`관계(Relationship)` scatter+fit+CI · bubble · hexbin &nbsp;|&nbsp;
`추세(Trend)` line+band · multi-line · area &nbsp;|&nbsp;
`구성(Composition)` stacked · 100%-stacked · treemap · pie &nbsp;|&nbsp;
`순위(Ranking)` ordered bar · lollipop &nbsp;|&nbsp;
`대응(Paired)` slope · difference &nbsp;|&nbsp;
`효과크기(Effect size)` forest / coefficient &nbsp;|&nbsp;
`행렬(Matrix)` heatmap · clustermap · mosaic &nbsp;|&nbsp;
`생존(Survival)` Kaplan–Meier · cumulative incidence &nbsp;|&nbsp;
`일치도(Agreement)` Bland–Altman &nbsp;|&nbsp;
`다변량(Multivariate)` PCA · UMAP · PCoA &nbsp;|&nbsp;
`흐름(Flow)` Sankey/alluvial · chord

스타일 모듈은 **모든** matplotlib 플롯과 함께 작동합니다 — 위 목록은 의도별로 매핑해 엄선한 세트일 뿐입니다.

---

<div align="center">

재현 가능한 과학을 위해 [Claude Code](https://claude.com/claude-code)로 제작 · **Apache-2.0** 라이선스

</div>
