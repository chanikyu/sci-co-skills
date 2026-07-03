---
name: strain-typing
description: 'Use when the user has one or more assembled bacterial genomes (a contigs FASTA, or a folder of them) and wants strain typing — MLST sequence type (mlst), optional species-specific serotyping (SISTR / ECTyper / …), and optional core-genome MLST (chewBBACA). Triggers — "MLST", "sequence type / ST", "serotyping / 혈청형", "균주 타이핑", "cgMLST". Input is an ASSEMBLY; if you only have reads, assemble first with genome-analysis. NOT for AMR/virulence/plasmid (use amr-profiling) or metagenomes.'
---

# Strain Typing

Type one or more **assembled bacterial genomes** — MLST sequence type, and (optionally)
serotype and core-genome MLST. Input is a contigs FASTA or a folder of them (batch). Same
design as the other SciCo skills: conda-managed tools, user-selected level, structured output
+ logs, honest reporting. Figures (if any) reuse `scientific-data-viz`.

## When to use

- Input is one or more **assembled** bacterial genomes (contigs FASTA / a folder of them).
- User wants MLST ST, and optionally serotype / cgMLST.
- Only have reads? Assemble first with **`genome-analysis`**, then run this.
- **Not** for: AMR / virulence / plasmid genes (→ `amr-profiling`), metagenomes (→ `shotgun-analysis`).

## Iron rule — honest typing

Report the scheme used and any partial / novel / missing alleles; never force a call the data
does not support. Serotyping is **organism-specific** — only run the matching tool (SISTR for
Salmonella, ECTyper for E. coli, …) and say which. cgMLST needs a defined scheme; state it.

## What it runs (user picks the level)

1. **MLST** (default, always) — `mlst` auto-detects the scheme and reports the ST + allele
   profile. No DB download needed (bundled).
2. **Serotyping** (optional, `serotyper=`) — organism-specific: `sistr` (Salmonella),
   `ectyper` (E. coli); add others as needed.
3. **cgMLST** (optional, `cgmlst_scheme=PATH`) — `chewBBACA` allele calling against a
   user-provided scheme (precise outbreak/epi typing).

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/strain-typing")
import pipeline
pipeline.run(
    input_path="genomes/",       # a contigs FASTA, or a folder of FASTAs (batch)
    out_dir="/path/to/results",  # -> tables/ logs/ report.md
    serotyper=None,              # or "sistr", "ectyper" (organism-specific)
    cgmlst_scheme=None,          # or a path to a chewBBACA scheme (enables cgMLST)
)
```

## Operating procedure

0. **Environment** — ensure the `scico-typing` conda env (below); create if missing (ask first).
1. **Collect genomes** — a single FASTA or every FASTA in the folder.
2. **MLST** — run on all; write `tables/mlst.tsv`.
3. **Ask what else** — if the user wants serotype/cgMLST, confirm the organism (→ serotyper) and,
   for cgMLST, the scheme path (`AskUserQuestion`).
4. **Run + log** — each tool via `conda run -n scico-typing`, teeing to `logs/<tool>.log`.
5. **Validate + report** — outputs exist, ST resolved (flag partial/novel); write `report.md`.

## Environment (conda — auto-created if missing)

One conda env, **`scico-typing`** (`environment.yml`): Python 3.12 + mlst, sistr_cmd, ectyper,
chewbbaca. Create if missing (ask first), then run via `conda run -n scico-typing`.

```bash
conda env list | grep -q scico-typing \
  || conda env create -f skills/strain-typing/environment.yml
```

## Common mistakes

| Mistake | Fix |
|---|---|
| Serotyping with the wrong organism's tool | Only run the tool for the actual species (confirm first) |
| Reporting an ST despite missing alleles | Flag partial/novel alleles; don't force a clean ST |
| Running on reads | Input is an assembly — assemble first with `genome-analysis` |
| cgMLST without a scheme | Requires a defined scheme path; state which scheme |
