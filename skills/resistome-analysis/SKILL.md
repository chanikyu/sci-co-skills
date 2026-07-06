---
name: resistome-analysis
description: 'Use when the user has a microbial COMMUNITY metagenome and wants the RESISTOME — antibiotic-resistance genes (ARGs) profiled directly from reads (not a single isolate): ARG detection (RGI/CARD, DeepARG, or AMR++/MEGARes), normalization (RPKM + per-single-copy-gene / per-16S "ARGs per cell"), aggregation to drug classes / mechanisms (ARO), and an ARG × samples abundance table → diversity + differential abundance (reusing the amplicon-analysis core) + a drug-class summary. Part of the microbiome suite (Metagenome / DNA). Triggers — "resistome / 리지스톰", "metagenomic AMR / 군집 항생제 내성", "ARG profiling", "CARD / RGI / DeepARG / MEGARes". NOT for a single assembled genome (use amr-profiling) or 16S (amplicon-analysis).'
---

# Resistome Analysis (community AMR from metagenomes)

Profile the **resistome** — the antibiotic-resistance genes (ARGs) of a whole microbial community —
directly from a shotgun metagenome's **reads**: detect ARGs → normalize → aggregate to drug classes →
**ARG × samples abundance** → diversity + differential. Distinct from `amr-profiling` (single isolate
genome): here the input is a **community**, quantified from reads. Same design as the other SciCo
skills: enter at any stage, conda-managed tools, user DBs. Downstream **reuses the `amplicon-analysis`
core**; figures reuse **`scientific-data-viz`**; reuses `shotgun-analysis` QC.

## When to use

- Input is a **community metagenome** for AMR: QC'd reads (or hAMRonization ARG reports), or an
  ARG × samples abundance table + metadata.
- **Not** for a single assembled genome (→ `amr-profiling`) or 16S/ITS (→ `amplicon-analysis`).

## Iron rule — honest resistome

**Genotype ≠ clinical phenotype** — a detected ARG predicts *hazard*, not treatment outcome; say so on
every report. **The database dominates the result** — different DBs/pipelines give **16–45× different**
ARG abundances; state the DB + version + tool + identity/coverage cutoffs. Raw counts are not
comparable — **normalize** (RPKM, and per-single-copy-gene / per-16S for "ARGs per cell"). Short-read
gene assignment is ambiguous; report % reads mapped. **ARG richness is depth-confounded** — deeper
samples detect more rare ARGs, so compute **alpha diversity on rarefied counts, not RPKM**, and say so.
Prefer **single-copy marker genes** for per-cell (16S copy number varies 1–15× per genome). Note: CLR
differential abundance is **invariant to the per-sample per-cell scaling** — so per-marker changes
Bray–Curtis + the drug-class summary, not the CLR test. `marker_rpkm` is **user-provided** (the
pipeline does not quantify markers itself).

## Pipeline (stages)

```
QC'd reads (host-removed; reuse shotgun QC) ─(ARG detection: RGI bwt/CARD · DeepARG · AMR++/MEGARes)→ ARG hits
   ─(hAMRonization: harmonize tool outputs)→ ─(normalize: RPKM + per-single-copy-gene / per-16S)→ ARG × samples
ARG table ┬─(aggregate to drug classes / mechanisms via ARO)→ drug-class × samples summary
          └─ CORE (reused from amplicon-analysis): preprocess → alpha → beta (PCoA, PERMANOVA)
             → differential abundance (which ARGs differ by group)
→ tables/ (arg_abundance.csv, drug_class.csv) images/ (drug-class composition, PCoA, differential) logs/ report.md
```

Enter at any stage: **reads → full; hAMRonization reports → normalize + downstream; an ARG table → diversity + differential.**

## Databases (user-provided)

- **CARD** (RGI, ~200 MB; academic/non-commercial) or **DeepARG** DB (models baked in — no external DB,
  simplest) or **MEGARes** (AMR++, ~30 MB, redistributable). A missing DB → that engine is skipped with a note.

## Reliable core vs external

- **External CLI (conda, needs DBs — scaffolded):** RGI (rgi), DeepARG, AMR++, hAMRonization.
- **Python-native (testable):** **RPKM + per-marker normalization**, **drug-class aggregation**, ARG
  table assembly, and the whole **downstream** (reuses amplicon-analysis core).

## Operating procedure

`pipeline.run(input_path, metadata, group_col, out_dir, from_stage=None, engine="deeparg",
gene_lengths=None, marker_rpkm=None, ...)` — ensure the `scico-resistome` conda env (create if missing,
ask first); detect the stage; pick cutoffs from the data; run + log each stage; validate; report with
the genotype≠phenotype + DB caveats. Before a heavy install/DB download, report the estimate and confirm.

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/resistome-analysis")
import pipeline
pipeline.run(
    input_path="arg_abundance.csv",  # reads dir / hAMRonization reports / ARG abundance table
    metadata="metadata.csv",         # sample_id + group column
    group_col="group",
    out_dir="/path/to/results",
    engine="deeparg",                # "deeparg" (models bundled) | "rgi" (needs CARD) — amrplusplus not yet wired
)
```

## Environment (conda — auto-created if missing)

One conda env, **`scico-resistome`** (`environment.yml`): Python 3.10 + deeparg, hamronization,
scikit-bio, pandas, numpy, scipy, matplotlib (+ optional `rgi` for the CARD engine, `amrplusplus`).
Create if missing (ask first), run via `conda run -n scico-resistome`. Reuses `amplicon-analysis`
(core) + `scientific-data-viz` (figures).

## Common mistakes

| Mistake | Fix |
|---|---|
| Reading an ARG hit as clinical resistance | Genotype ≠ phenotype — report hazard, not outcome |
| Comparing raw ARG counts across samples | Normalize: RPKM + per-single-copy-gene / per-16S |
| Trusting one DB's numbers | DBs disagree 16–45× — state DB + version + cutoffs |
| Using amr-profiling for a community | That's for one isolate genome; use this for reads |
| Ignoring % reads mapped | Report mapping rate + coverage cutoffs (short-read ambiguity) |
