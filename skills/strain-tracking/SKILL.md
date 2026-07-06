---
name: strain-tracking
description: 'Use when the user has a MULTI-SAMPLE shotgun metagenome cohort and wants STRAIN-TRACKING — following the SAME bacterial strain across samples / individuals / timepoints (transmission, sharing, persistence, turnover), NOT typing a single isolate: per-sample strain profiling (StrainPhlAn 4 marker-based [default], or inStrain popANI reference/MAG-based; MIDAS2 planned), per-species cross-sample strain distance matrices, "same-strain" calls at community thresholds (inStrain popANI >= 99.999%, StrainPhlAn nucleotide/phylogenetic distance), a strain-sharing network, and longitudinal persistence. Part of the microbiome suite (Metagenome / DNA). Triggers — "strain tracking / sharing / transmission", "균주 추적 / 전파 / 공유", "StrainPhlAn / inStrain / popANI / MIDAS2". NOT for a single assembled isolate (use strain-typing) or 16S (amplicon-analysis).'
---

# Strain Tracking (same-strain sharing across a metagenome cohort)

Follow the **same bacterial strain across samples** — between individuals (sharing / transmission) or
within an individual over time (persistence / replacement / turnover) — from a **multi-sample**
shotgun metagenome cohort. Distinct from `strain-typing` (one isolate genome, MLST/cgMLST): here the
input is a **cohort of metagenomes**, and the question is *"is it the same strain in two places?"*. Same
design as the other SciCo skills: enter at any stage, conda-managed tools, user DBs. Reuses
`shotgun-analysis` QC; a strain distance matrix can be handed to `amplicon-analysis` for PCoA/PERMANOVA
(convert identity→distance first; **not auto-run**); figures reuse `scientific-data-viz`.

## When to use

- A **multi-sample** metagenome cohort, asking about **strain sharing / transmission / persistence**.
- **Not** a single assembled isolate (→ `strain-typing`) or 16S/ITS (→ `amplicon-analysis`).

## Iron rule — honest strain-tracking

**Sharing ≠ transmission** — two hosts carrying the same strain may share an environment/diet, not a
direct transmission event; call it *strain sharing* and require epidemiological / temporal context before
saying "transmission". **Species-by-species** — every call is within one species; there is no single
genome-wide answer. **Coverage gates the call** — a strain needs enough coverage/breadth (StrainPhlAn
breadth ~80%; inStrain ≥50% breadth, ~5× coverage) or it is *undetermined*, not "different". State the
**tool + threshold** (inStrain **popANI ≥ 99.999%**; StrainPhlAn normalized nucleotide/phylogenetic
distance) and the **DB/reference** — reference-based tools miss unknown species.

## Pipeline (stages)

```
QC'd reads (host-removed; reuse shotgun QC), many samples
   ─(profile per sample: StrainPhlAn 4 [marker, default] · inStrain [popANI, ref/MAG] · MIDAS2)→
   per-species SNV / marker consensus  ─(cross-sample compare)→  per-species strain DISTANCE / identity matrix
distance matrix ─(threshold "same strain")→ shared-strain pairs
   ┬─ across individuals → strain-SHARING network (networkx: who shares which species)
   └─ within individual over time → PERSISTENCE (retained vs replaced vs undetermined, among detected timepoints)
   (export a species' distance matrix to amplicon-analysis for PCoA/PERMANOVA — NOT auto-run)
→ tables/ (shared_strains.csv, sharing_edges.csv, persistence.csv) images/ (sharing network, persistence) logs/ report.md
```

Enter at any stage: **reads → full; a per-species strain distance matrix → same-strain calls + network + persistence.**

## Databases (user-provided)

- **StrainPhlAn / MetaPhlAn 4** marker DB (~15 GB; downloaded once — the reference-free default) **or**
  **inStrain** (user genome/MAG set + a Bowtie2 index; popANI, highest resolution). **MIDAS2**
  (UHGG ~93 GB) is *planned — not yet wired*. A missing DB → that engine is skipped with a note.

## Reliable core vs external

- **External CLI (conda, needs DBs — scaffolded):** StrainPhlAn/MetaPhlAn, inStrain, MIDAS2, Bowtie2.
- **Python-native (testable):** **same-strain calls** (threshold a distance/identity matrix), the
  **strain-sharing network** (networkx), and **longitudinal persistence**.

## Operating procedure

`pipeline.run(input_path, metadata, out_dir, engine="strainphlan", metric="distance",
threshold=..., subject_col=None, time_col=None, ...)` — ensure the `scico-straintrack` conda env
(create if missing, ask first); detect the stage; pick the threshold from the tool (popANI 99.999% for
inStrain; a normalized distance for StrainPhlAn); run + log; validate; report with the sharing≠transmission
+ species-by-species + coverage caveats. Before a heavy install / DB download, report the estimate and confirm.

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/strain-tracking")
import pipeline
pipeline.run(
    input_path="strain_distance.csv",  # reads dir / per-species strain distance matrix (auto-detected)
    metadata="metadata.csv",           # sample_id + subject / timepoint / group columns
    out_dir="/path/to/results",
    engine="strainphlan",              # "strainphlan" (marker, default) | "instrain" (popANI) — midas2 planned
    metric="distance",                 # "distance" (same if <= threshold) | "identity" (same if >= threshold)
    subject_col="subject",             # host/individual id → cross-subject sharing + within-subject persistence
    time_col="timepoint",              # enables longitudinal persistence
)
```

## Environment (conda — auto-created if missing)

One conda env, **`scico-straintrack`** (`environment.yml`): Python 3.10 + metaphlan (StrainPhlAn),
bowtie2, networkx, scikit-bio, scipy, pandas, numpy, matplotlib (+ optional `instrain`, `midas2`,
`dendropy`). Create if missing (ask first), run via `conda run -n scico-straintrack`. Reuses
`amplicon-analysis` (PCoA/PERMANOVA) + `scientific-data-viz` (figures).

## Common mistakes

| Mistake | Fix |
|---|---|
| Calling strain sharing "transmission" | Sharing ≠ transmission — needs epi/temporal context |
| One genome-wide "same strain?" answer | It's **per species**; report each species separately |
| Treating low-coverage as "different strain" | Below breadth/coverage gate → **undetermined**, not different |
| Using strain-typing for a cohort | That's for one isolate genome; use this for many metagenomes |
| Reading persistence as full turnover | It calls persisted / replaced / undetermined among **detected** timepoints; new acquisition / loss are not yet modeled |
| Not stating the threshold / DB | Always report tool + popANI/distance threshold + reference DB |
