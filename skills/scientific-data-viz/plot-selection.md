# Plot Selection Reference

Pick the plot the reader understands **fastest** for the message. Start from the
reader's *question* (the intent), confirm the *data shape*, then choose. The point
is intuitiveness: a naive reader should grasp the message without a manual.

## Step 1 — Read the data's nature

Classify before choosing:

- **# of variables** to show together: 1, 2, or 3+.
- **Type of each**: categorical (nominal), ordinal (ordered categories: dose, stage),
  continuous, temporal (time), count/proportion.
- **Sample size per group**: small (n < ~15 → show individual points) vs large.
- **Structure**: independent groups vs paired/repeated (same unit measured twice)
  vs longitudinal (many timepoints).
- **Uncertainty available?**: raw replicates, SD, SEM, or CI (decides error bars).

## Step 2 — Intent → plot (the decision table)

| Reader's question (intent) | Data shape | First choice | Alternatives | Avoid / notes |
|---|---|---|---|---|
| How does a value differ across a few groups? | 1 categorical × 1 continuous, small n | **bar + individual points + error bars** | dot plot | bar without points when n small hides the data |
| …across groups, showing the full spread? | 1 categorical × 1 continuous, larger n | **box + jittered points** | violin, raincloud, strip/swarm | violin needs n≥~20 to be honest |
| How does one continuous variable distribute? | 1 continuous | **histogram** or KDE density | rug, ECDF | over-smoothed KDE hides gaps/bimodality |
| Do two continuous variables relate? | 2 continuous | **scatter (+ fit line + CI)** | bubble (3rd var by size), hexbin/2D-density if dense | connecting scatter points with lines |
| How does a value change over time / an ordered axis? | temporal/ordinal × continuous | **line (+ CI/SEM band)** | multi-line, area (cumulative) | bars for a continuous x |
| Two grouping factors at once? | 2 categorical × 1 continuous | **grouped bar / grouped box** | faceted (small multiples) | >3 levels each → use a heatmap |
| A value over a full matrix of two categories? | 2 categorical × 1 value (many×many) | **heatmap** | clustermap (+ dendrogram) | center a *diverging* map at 0 for signed values |
| Rank many categories? | 1 categorical (many) × 1 value | **horizontal ordered bar / lollipop** | dot plot | vertical bars with rotated labels |
| Before vs after on the same units? | paired continuous | **paired/slope lines (connected dots)** | paired scatter, difference plot | independent-group bars (loses pairing) |
| Effect sizes / model coefficients / OR·HR? | estimate + CI per item | **forest plot** (point + CI, reference line 0 or 1) | coefficient plot | bar charts for effect sizes |
| Composition / part-of-whole? | categorical proportions | **stacked / 100%-stacked bar** | treemap | pie (except ≤3 slices, lay audience) |
| Time-to-event / survival? | time + event/censor | **Kaplan–Meier step curve** (+ risk table, censor ticks) | cumulative incidence | smoothing the step curve |
| Counts of two categoricals? | 2 categorical (counts) | **grouped/stacked bar** | mosaic, contingency heatmap | 3D bars |
| Sample structure in high dimensions? | many continuous | **PCA / UMAP scatter** colored by group | — | over-interpreting axes units |
| Group separation in multivariate/community space? | distance matrix + groups | **PCoA scatter** colored by group | NMDS | label axes with % variance (`J.var_label`); test with **PERMANOVA** (`S.permanova`) |
| Agreement between two methods? | 2 continuous, same quantity | **Bland–Altman** (difference vs mean) | — | plain scatter alone (misses bias) |
| Flows / transitions between states? | source→target + weight | **Sankey / alluvial** | chord | — |

## Step 3 — Golden rules (apply to whatever you pick)

- **Bars start at zero.** Truncating a bar y-axis exaggerates differences. Line/scatter
  y-axes may be non-zero.
- **Show the data when n is small.** Overlay individual points on bars/boxes for n < ~15.
- **State the error type.** Always say SD vs SEM vs 95% CI (axis label or caption).
  Never draw error bars the data doesn't support.
- **Colorblind-safe.** Use `journal_style.CATEGORICAL` (Okabe-Ito) or a single-hue ramp.
- **Direct-label beats a legend** when there are ≤3 series.
- **One message per panel.** Multiple messages → multi-panel with bold letters (A, B, C…).
- **No** dual y-axes, 3D, drop shadows, or gratuitous gridlines (chartjunk).
- **Encode order.** For ordinal groups use a sequential ramp (light→dark), not random hues.

## Multi-panel assembly

- Order panels by the argument's logic (overview → mechanism → outcome), not by plot type.
- Keep shared quantities on identical scales/colors across panels so the reader compares directly.
- Reuse one color meaning across the whole figure (e.g. "High dose" is always the same navy).
