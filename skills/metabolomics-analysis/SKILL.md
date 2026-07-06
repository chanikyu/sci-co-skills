---
name: metabolomics-analysis
description: 'Use when the user has RAW untargeted metabolomics spectra (LC-MS or GC-MS: mzML / .CDF, or a not-yet-annotated feature table) and wants the UPSTREAM processing → an annotated feature table: peak/feature detection (LC-MS via asari / XCMS), GC-MS deconvolution + retention index (eRah / MS-DIAL + RIAssigner), RT alignment, gap-filling, isotope/adduct grouping, QC (pooled-QC RSD filter, QC-RLSC drift correction), and metabolite annotation (matchms spectral matching, precursor-gated MSI confidence levels), output as an annotated feature table (CSV) that hands off to microbiome-metabolome-analysis for stats. Triggers — "metabolomics / 메타볼로믹스 원시처리", "LC-MS / GC-MS 처리", "peak picking / 피크 검출", "mzML → feature table", "metabolite annotation". NOT for downstream statistics from an already-annotated table (use microbiome-metabolome-analysis).'
---

# Metabolomics Analysis (raw spectra → annotated feature table)

The **upstream** untargeted-metabolomics pipeline — raw LC-MS / GC-MS spectra → **annotated feature
table** — the half that `microbiome-metabolome-analysis` (downstream statistics) assumes is already
done. Detection → alignment → grouping → QC → **annotation**, for **both LC-MS and GC-MS**. Same
design as the other SciCo skills: enter at any stage, conda-managed tools, structured output + logs,
honesty. Hands off the annotated table to **`microbiome-metabolome-analysis`** for stats.

## When to use

- Input is **raw** metabolomics: an mzML / .CDF directory, or a **not-yet-annotated** feature table
  (m/z · RT × samples), + sample metadata (with a QC/blank flag if available).
- **Not** for statistics from an already-annotated table (→ `microbiome-metabolome-analysis`), or
  targeted quantification.

## Iron rule — honest annotation (MSI levels)

Every reported identity carries a **Metabolomics Standards Initiative (MSI) / Schymanski confidence
level (1–4)** — **most untargeted features are level 2–3 (putative)**; level 1 needs a reference
standard. State the tool + version + parameters (they are starting points, **not** universal), the
library used, and the scoring/RI thresholds. Report QC RSD + how many features were dropped. Never
present a putative match as a confirmed identity.

## Pipeline (two platform tracks)

```
raw (mzML / .CDF) ┬─ LC-MS TRACK ── feature detection (asari [Python] / XCMS) → RT alignment (obiwarp)
                  │                  → correspondence + gap-fill → isotope/adduct grouping (CAMERA)
                  └─ GC-MS TRACK ── deconvolution (eRah / MS-DIAL) → retention index (RIAssigner)
                                    → alignment → EI matching (NIST / Golm / FiehnLib)
feature table ─(QC: pooled-QC RSD filter + blank filter + QC-RLSC drift correction)→ clean table
clean table + per-feature spectra ─(annotate: matchms MS2/EI spectral match, precursor-gated → MSI level)→ annotations
→ tables/ (feature_table_clean.csv, annotations.csv) images/ (QC RSD, annotation MSI) logs/ report.md
→ hand off to microbiome-metabolome-analysis for diversity / differential stats
```

Enter at any stage: **mzML → full; a feature table → QC + annotation; an annotated table → done / stats.**

## Tracks & tools (confirmed from the literature)

- **LC-MS (Python-native default):** **asari** (pure-Python feature detection + alignment + grouping,
  fast); `--engine xcms` wraps XCMS/CAMERA (r-xcms) for publication-grade. `msconvert` for vendor raw.
- **GC-MS (must wrap — no production Python deconvolution):** **eRah** (R) or **MS-DIAL** (Java) for
  deconvolution; **RIAssigner** (Python) for retention index; EI libraries (NIST / Golm / FiehnLib / MoNA).
- **Annotation (both, Python):** **matchms** — MS2 (LC-MS) / EI (GC-MS) spectral matching against a
  user library (MoNA / GNPS / MassBank / NIST) with cosine / modified-cosine; MS1 adduct + formula;
  optional **SIRIUS** (Java CLI) for in-silico. MSI level assigned from the evidence.
- **QC:** pooled-QC **RSD** filter, blank filter, **QC-RLSC** (LOESS drift correction) — pure Python.

## Databases / references (user-provided)

- **Spectral library** for annotation (`--library PATH`: MoNA / GNPS / MassBank `.msp`/`.mgf`; NIST for GC-MS).
- **GC-MS:** RI reference (alkane / FAME) + an EI library.
- **XCMS / MS-DIAL / SIRIUS:** installed on demand (conda) when that engine is chosen.
A missing library → annotation is skipped (features stay unannotated) with a clear note.

## Operating procedure — enter at ANY stage

`pipeline.run(input_path, metadata, out_dir, platform="lc", from_stage=None, engine="asari",
library=None, ...)` detects the input and runs downstream. Every run: ensure the `scico-metabolomics`
conda env (create if missing, ask first); detect the stage; pick QC options from the data (QC/blank
presence, RSD cutoff) — ppm / peak-width are per-instrument defaults you set; run + log each stage; report with MSI
levels. Before a heavy install (XCMS / MS-DIAL / SIRIUS) or a large run, report the estimate and confirm.

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/metabolomics-analysis")
import pipeline
pipeline.run(
    input_path="mzml_dir/",        # mzML/.CDF dir, OR a feature table, OR an annotated table
    metadata="metadata.csv",       # sample_id + (optional) sample_type (sample/qc/blank)
    out_dir="/path/to/results",
    platform="lc",                 # "lc" or "gc"
    engine="asari",                # LC: "asari" | "xcms"; GC: "erah" | "msdial"
    library="mona.msp",            # spectral library for annotation (optional)
)
```

## Environment (conda — auto-created if missing)

One conda env, **`scico-metabolomics`** (`environment.yml`): Python 3.11 + asari, matchms, pymzml,
pyteomics, RIAssigner, statsmodels, pandas, numpy, matplotlib (+ optional, on demand: `r-xcms` for the
XCMS engine, MS-DIAL / eRah for GC-MS deconvolution, SIRIUS for in-silico, ProteoWizard `msconvert`).
Create if missing (ask first), run via `conda run -n scico-metabolomics`. Reuses **`scientific-data-viz`**.

## Honesty / caveats

- **Parameters are starting points** — ppm / peak-width must be checked against internal standards.
- **GC-MS deconvolution is wrapped** (R/Java) — pure Python cannot do it; stated per run.
- **Most annotations are MSI level 2–3 (putative)** — only reference-standard matches are level 1.
- **Annotation needs per-feature MS2/EI spectra** (the detector's spectra export, or a user `.mgf`/`.msp`)
  + a library; **level 2 requires precursor accurate-mass agreement** — spectral-only matches are level 3.
- **GC-MS retention index (RIAssigner)** is applied only when an alkane/FAME RI reference is provided;
  MS1 isotope/adduct grouping is done by the detector (asari khipu / XCMS+CAMERA), not re-derived here.
- QC drift correction (QC-RLSC) needs pooled QCs; it can over-correct in small, well-controlled runs.
- The output annotated table is the handoff to `microbiome-metabolome-analysis` (stats).

## Common mistakes

| Mistake | Fix |
|---|---|
| Trying GC-MS in pure Python | Deconvolution wraps eRah / MS-DIAL; only RI + annotation are Python |
| Reporting putative IDs as confirmed | Tag every identity with its MSI level (most are 2–3) |
| Default ppm / peak-width blindly | Validate on internal standards; defaults are starting points |
| No QC / blank samples | RSD filter + QC-RLSC need pooled QC; say when they're skipped |
| Reinventing peak-picking | Reuse asari / XCMS / MS-DIAL — don't hand-roll detection |
