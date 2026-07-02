---
name: scientific-data-viz
description: Use when the user has REAL data (numbers, a table, CSV, experiment results, stats) and wants a publication-quality journal figure (Nature/Cell/eLife style) plotted from it — a bar/line/box/scatter/heatmap/forest/survival/etc. chart where the exact data values must be rendered faithfully. Triggers — "논문 그림/figure 그려줘", "이 데이터로 그래프", "publication figure", "저널 스타일 plot", "막대/박스/산점도/히트맵 그려줘", "figure for my paper". NOT for conceptual diagrams/workflows/mechanisms (use scientific-workflow-viz instead).
---

# Scientific Data Viz

Turn **real data** into a **publication-quality journal figure** by writing plotting
code (matplotlib) that renders the exact values — never an AI image prompt.

**Core principle:** The figure is CODE-RENDERED so the data is exact. An AI image
generator fabricates bar heights, axes, and error bars; it must never touch real data.
Sibling skill `scientific-workflow-viz` handles the opposite case (conceptual
diagrams), and uses image prompts. This skill is for data.

## When to use

- User provides data (table/CSV/numbers/stats) and wants it plotted for a paper, thesis, poster, or grant.
- Output must look like a real journal figure: minimal, white background, clean.
- Use when the message is "show these numbers," not "explain this concept."

**When NOT to use:** conceptual workflow / pipeline / mechanism / comparison *diagrams*
with no data behind them → use `scientific-workflow-viz` (image prompt) instead.

## The iron rule — data values are exact

**Render the numbers the user gave, unchanged.**

- No eyeballing, no rounding for looks, no smoothing, no interpolation the data lacks.
- Never route real data through an image generator ("make me a figure that looks like…").
- Never invent statistics, significance stars, or error bars the data doesn't support.
- If a value is missing, ask or mark it — don't fill it in.
- Bars start at zero (a truncated bar axis misrepresents the data).

## Workflow

1. **Ingest & inspect.** Read the data exactly. Note: # variables, each variable's type
   (categorical / ordinal / continuous / temporal / count), sample size per group,
   independent vs paired vs longitudinal, and what uncertainty exists (raw / SD / SEM / CI).
   If the format is a file, load it; if it's pasted numbers, transcribe them verbatim.
   **Separate table + metadata is supported (and normal for omics):** accept a data/feature
   table (samples × features) and a separate metadata/mapping file (sample × covariates like
   group, sex, timepoint) and JOIN them on the shared key (`sample_id`). Use pandas:
   `df = table.merge(meta, on="sample_id", how="inner")`. VALIDATE the join — report any IDs
   present in one file but not the other; never silently drop samples. One metadata file can
   drive coloring/faceting for many data tables (abundance, alpha, beta) that share the key.
2. **Pick the plot.** Choose the chart a naive reader understands fastest for the message.
   **REQUIRED:** consult `plot-selection.md` (intent → plot table + golden rules). One
   message per panel; multiple messages → multi-panel with letters A, B, C…. State which
   plot you chose and *why* it fits the data.
3. **Ask the color set.** Before rendering, let the user choose a palette:
   a. **Show all options first** — render/open the swatch of all 20 palettes so they see
      the actual colors: run `palette_reference.py` (saves `palette_reference.png`) and
      display it. Don't rely on the picker alone.
   b. **Then ask (AskUserQuestion).** The picker is capped at 4 options by the harness, so
      make the 4 options the 4 palette CATEGORIES (Many-categories / Journal / Colorblind-safe /
      ColorBrewer), and state in the question that the user can type ANY of the 20 names
      (listed below) into "Other". **Default & first option: `tab20`** (20 distinct colors,
      handles few or many groups); fall back to it when the user has no preference.
   c. Use a sequential ramp (`J.sequential`), not a qualitative palette, for ORDINAL groups.
4. **(Optional) Run the statistics.** Only if the user asks to test / provides raw
   replicate data: compute the test with `stats.py` and annotate with the computed p.
   Otherwise skip — never invent a test. See "Optional statistics" below.
5. **Render in house style.** Use `journal_style.py`. Plot the exact data. Overlay
   individual points when n is small. Label the error type. **Put legends OUTSIDE the
   plot** with `J.legend_outside(ax)` so they never overlap data.
6. **Output into a structured folder.** Create an output directory and, inside it,
   `images/` and `script/` (use `J.prepare_output(base)`). Save the figure as
   `images/<name>.png` (300 dpi preview) + `images/<name>.pdf` (vector, editable — the
   submission file), and write/copy the generating `script/<name>.py` (reproducible).
   Tell the user the folder layout.

   ```
   <base>/
     images/   <name>.png, <name>.pdf
     script/   <name>.py
   ```
7. **Report honestly.** Say which plot and why, which palette, restate the error type,
   and flag any limitation (small n, no stats provided, assumed SEM vs SD, which test
   and correction were used, etc.).

## Color palettes (offer these in step 3)

20 qualitative sets in `J.PALETTES`, grouped by purpose. Show the user the relevant
group and let them pick (default `okabe_ito`). **Match the palette size to the number
of groups** — for many categories (e.g. a taxonomy barplot with 9+ taxa) offer a
many-color set, not a 7-color one.

- **Colorblind-safe:** `okabe_ito` (default), `tol_bright`, `tol_muted`, `tol_vibrant`
- **Journal house colors (match the venue):** `npg` (Nature), `aaas` (Science), `nejm`,
  `lancet`, `jama`, `jco`, `d3`
- **ColorBrewer qualitative:** `set1`, `set2`, `dark2`, `accent`
- **Many categories (12–20 colors):** `tab20`, `set3`, `paired`, `igv`, `kelly`
- **Ordinal** (dose/stage/time): single-hue ramp `J.sequential(n, cmap)`, `cmap` in
  `J.SEQ_CMAPS` (Blues, viridis, cividis, magma, …) — NOT a qualitative palette.
- **Signed values / correlation matrices:** `J.diverging(n)` centered at 0.

Apply with `J.set_style(palette="igv")` or `J.use_palette("lancet")`; fetch colors with
`J.palette(n)`. A visual swatch of all palettes: run `palette_reference.py` in this skill dir.

## Using journal_style.py

The house style (the Nature/Cell/eLife minimal look) is encoded in `journal_style.py`
in this skill directory. Import it — do not re-derive the style by hand.

```python
import numpy as np
import journal_style as J          # copy the file next to your script, or add its dir to sys.path

J.set_style()                       # journal rcParams (Arial/Helvetica, thin spines, no grid)
fig, axes = J.figure_grid(1, 3, width="2col", panel_h=2.6)   # sized to a journal column
axA, axB, axC = axes

# --- Panel A: bar + individual points + error bars (small-n comparison) ---
means = np.array([4.2, 3.8, 2.6, 1.8]); sds = np.array([0.55, 0.48, 0.40, 0.35])
x = np.arange(4)
axA.bar(x, means, color=J.BLUE_RAMP, edgecolor="#3a3a3a", linewidth=0.7)
axA.errorbar(x, means, yerr=sds, fmt="none", ecolor="black", capsize=3, elinewidth=1)
# ...overlay real replicate points with J.jitter(...) when you have them...
axA.set_ylim(0, 5.3); axA.set_xticks(x); axA.set_xticklabels(["Vehicle","Low","Mid","High"])
axA.set_ylabel("FITC-dextran (µg/mL)  (mean ± SD)")   # <- state the error type
J.sig_bracket(axA, 0, 3, 4.85, "**")                  # only if the user gave the test result
J.finalize(axA); J.panel_letter(axA, "A"); axA.set_title("Intestinal permeability")

# ...axB, axC similarly...
J.save(fig, "/Users/.../Desktop/myfigure")            # -> .png + editable .pdf
```

Helpers: `J.set_style(palette=...)`, `J.use_palette()`, `J.palette(n)`, `J.figure_grid()`,
`J.finalize()`, `J.panel_letter()`, `J.legend_outside(ax)` (legend outside the panel),
`J.sig_bracket()`, `J.add_sig_brackets()` (stacked brackets from posthoc pairs),
`J.stats_text()`, `J.stars(p)`, `J.slope()` (paired before/after), `J.jitter()`, `J.save()`;
palettes `J.PALETTES`, `J.sequential(n, cmap)`, `J.diverging(n)`.
Any matplotlib plot type works — the module only sets the *look*, not the chart.

**Notes (from usability testing):**
- To import the module, add its directory to `sys.path`:
  `import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/scientific-data-viz")`.
- **Single-panel figure → no letter.** Panel letters (A, B, C…) are only for multi-panel
  figures. `J.figure_grid(1, 1)` still returns a list, so use `ax = axes[0]`.
- **Significance stars:** p<0.001 → \*\*\*, p<0.01 → \*\*, p<0.05 → \*, else n.s. (use `J.stars(p)`).
- `J.sig_bracket()` sits at the top; `J.stats_text()` now defaults to the lower-left so the
  two don't collide. Keep them apart if you move either.

## Optional statistics (`stats.py`)

Opt-in only — run when the user asks to test, or supplies raw replicate data. The
viz layer annotates p-values; `stats.py` is where they are COMPUTED.

```python
import stats as S
res = S.compare([ctrl, low, mid, high])            # auto-picks ANOVA vs Kruskal by normality
ph  = S.posthoc([ctrl, low, mid, high],            # pairwise + Holm correction
                labels=["Ctrl","Low","Mid","High"])
J.add_sig_brackets(ax, ph, x=[0,1,2,3], y0=5.0, dy=0.4)   # brackets for significant pairs
J.stats_text(ax, S.report(res))    # -> "one-way ANOVA, F(3, 28) = 12.40, P < 0.001"
```

Functions: `S.compare(groups, paired=, parametric=)` (Welch's t-test / Mann–Whitney U /
paired t-test / Wilcoxon signed-rank / one-way ANOVA / Kruskal–Wallis), `S.posthoc(...)`
(pairwise + Holm/Bonferroni), `S.correlation(x, y, method=)`, `S.chi_square(table)`,
`S.logrank(t1,e1,t2,e2)`, and **`S.report(res)`** which formats the annotation.

**Ordination / beta diversity (distance-matrix based):** `S.bray_curtis(table)` →
distance matrix; `S.pcoa(dist)` → `{coords, var_explained}`; `S.permanova(dist, groups)`
→ pseudo-F, R², permutation p (the standard test for group separation on a PCoA).
For a PCoA/PCA plot: **label axes with % variance explained** via
`ax.set_xlabel(J.var_label("PCoA1", var[0]))`, and annotate group separation with
`J.stats_text(ax, S.report(S.permanova(dist, groups)))`
(→ "PERMANOVA, pseudo-F = 8.30, R² = 0.27, P = 0.001"). Accept a distance matrix directly
as input, or build one from a feature table with `S.bray_curtis`.

**Always annotate with `S.report(res)`** — it writes the FULL test name plus statistic
and P (e.g. "Mann–Whitney U test, U = 41.0, P = 0.003"). Never label a figure with a bare
symbol like "U, p" or "t, p"; the reader must see which test was run.

**Honesty rules:** report WHICH test and why (parametric choice is auto-decided by a
Shapiro–Wilk normality test and returned in the result); report the EXACT p; for 3+
groups always use `posthoc` with a correction (never a grid of raw p-values); state
n; if a sample is too small to test, say so — don't fabricate a result.

## Environment

If matplotlib isn't installed (common on system Python), create a venv:
`python3 -m venv venv && ./venv/bin/pip install -q matplotlib numpy`, then run with
`./venv/bin/python`. (Add pandas if loading CSV/Excel, scipy/lifelines for fits/survival.)

## Common mistakes

| Mistake | Fix |
|---|---|
| Feeding real data to an AI image tool | Always code-render. Image tools fabricate values. |
| Bar y-axis not starting at 0 | Bars must include zero; only line/scatter may be non-zero. |
| Not showing points when n is small | Overlay individual replicates (n < ~15). |
| Error bars unlabeled | State SD / SEM / 95% CI in the axis label or caption. |
| Inventing significance stars | Add stats only from the user's actual test result. |
| Colored cards / header bars / background tints | That's slide/BioRender style — journals want minimal white. |
| Rainbow categorical colors | Use a named palette (`J.use_palette`); light→dark ramp for ordinal groups. |
| Legend covering the data | Put it outside with `J.legend_outside(ax)`. |
| Reporting raw pairwise p-values for 3+ groups | Correct for multiple comparisons (`S.posthoc`, Holm). |
| PNG only | Also emit vector PDF (fonttype 42) — the real submission file. |

## Real-world impact

Produces figures visually indistinguishable from Nature/Cell/eLife figures, with
exact data and an editable vector PDF, plus a reproducible script — in one pass.
