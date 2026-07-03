---
name: amr-profiling
description: 'Use when the user has one or more assembled bacterial genomes (a contigs FASTA, or a folder of them) and wants to screen for antimicrobial resistance (AMR) genes, virulence factors, and plasmid replicons — via AMRFinderPlus and abricate (CARD / ResFinder for AMR, VFDB for virulence, PlasmidFinder for plasmids). Triggers — "AMR / 항생제 내성 유전자", "resistance genes", "virulence / VFDB", "plasmid / PlasmidFinder", "abricate / AMRFinderPlus". Input is an ASSEMBLY; only have reads? assemble first with genome-analysis. NOT for MLST/serotyping (use strain-typing) or metagenomes.'
---

# AMR Profiling

Screen one or more **assembled bacterial genomes** for **AMR genes, virulence factors, and
plasmid replicons**. Input is a contigs FASTA or a folder of them (batch). Same design as the
other SciCo skills: conda-managed tools, structured output + logs, honest reporting.

## When to use

- Input is one or more **assembled** bacterial genomes (contigs FASTA / a folder of them).
- User wants resistance genes, and/or virulence factors, and/or plasmid replicons.
- Only have reads? Assemble first with **`genome-analysis`**, then run this.
- **Not** for: MLST / serotyping (→ `strain-typing`), metagenomes (→ `shotgun-analysis`).

## Iron rule — honest calls

Report the database + version and the identity / coverage thresholds for every hit. A gene hit
is a *prediction of genotype*, not a phenotype — say so; don't claim clinical resistance from a
sequence alone. Report partial hits. A missing DB → that screen is skipped with a note.

## What it runs

| Target | Tool | Database |
|---|---|---|
| **AMR** (primary) | AMRFinderPlus | NCBI AMR (auto-downloaded / `--amrfinder-db`) |
| **AMR** (secondary) | abricate | CARD / ResFinder (bundled) |
| **Virulence** | abricate | VFDB (bundled) |
| **Plasmid replicons** | abricate | PlasmidFinder (bundled) |

Batch runs get an abricate **presence/absence summary** across genomes per database.

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/amr-profiling")
import pipeline
pipeline.run(
    input_path="genomes/",       # a contigs FASTA, or a folder of FASTAs (batch)
    out_dir="/path/to/results",  # -> tables/ logs/ report.md
    organism=None,               # e.g. "Escherichia" -> AMRFinderPlus point-mutation screen
    amrfinder_db=None,           # optional AMRFinderPlus DB path (else its default)
)
```

## Operating procedure

0. **Environment** — ensure the `scico-amr` conda env (below); create if missing (ask first).
   AMRFinderPlus needs its DB — `amrfinder -u` downloads it, or pass `--amrfinder-db`.
1. **Collect genomes** — a single FASTA or every FASTA in the folder.
2. **AMR** — AMRFinderPlus per genome (`--plus`; `--organism` for point mutations if known).
3. **AMR / virulence / plasmid** — abricate vs CARD, VFDB, PlasmidFinder; per-genome tabs +
   a presence/absence `--summary` across the batch.
4. **Run + log** — each tool via `conda run -n scico-amr`, teeing to `logs/<tool>.log`.
5. **Validate + report** — outputs exist; write `report.md` (genotype ≠ phenotype caveat stated).

## Environment (conda — auto-created if missing)

One conda env, **`scico-amr`** (`environment.yml`): Python 3.12 + ncbi-amrfinderplus, abricate.
Create if missing (ask first), then run via `conda run -n scico-amr`.

```bash
conda env list | grep -q scico-amr \
  || conda env create -f skills/amr-profiling/environment.yml
```

## Common mistakes

| Mistake | Fix |
|---|---|
| Claiming resistance phenotype from a gene hit | Report genotype; note it predicts, not proves, resistance |
| Not stating identity/coverage thresholds | Always report the DB + %ID / %cov cutoffs |
| AMRFinderPlus with no DB | Run `amrfinder -u` or pass `--amrfinder-db`; else skip with a note |
| Running on reads | Input is an assembly — assemble first with `genome-analysis` |
