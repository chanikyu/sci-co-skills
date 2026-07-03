# 🛡️ amr-profiling

<sub>[← SciCo-Skills](../../README.md) · a skill in the SciCo-Skills suite</sub>

Screen one or more **assembled bacterial genomes** for **AMR genes, virulence factors, and
plasmid replicons** — via **AMRFinderPlus** and **abricate**. Input is a contigs FASTA or a
folder of them (batch). Same design as the other SciCo skills: conda-managed tools, structured
output + logs, honest calls.

## What it runs

| Target | Tool | Database |
|---|---|---|
| **AMR** (primary) | AMRFinderPlus | NCBI AMR (`amrfinder -u` / `--amrfinder-db`) |
| **AMR** (secondary) | abricate | CARD / ResFinder (bundled) |
| **Virulence** | abricate | VFDB (bundled) |
| **Plasmid replicons** | abricate | PlasmidFinder (bundled) |

Batch runs get an abricate **presence/absence summary** across genomes per database.

## 🤖 Use it in Claude

> *"Screen these assemblies for AMR, virulence, and plasmids."*
>
> *"amr-profiling on this genome — AMRFinderPlus with --organism Escherichia"*

Input is an **assembly** — only have reads? Assemble first with
[`genome-analysis`](../genome-analysis).

## ⚠️ Notes

- A gene hit predicts **genotype, not clinical phenotype** — the report says so.
- Database + version and identity/coverage thresholds are always reported.
- AMRFinderPlus needs its DB (`amrfinder -u`, or `--amrfinder-db`); missing → skipped with a note.

## Environment

One conda env, **`scico-amr`** (`ncbi-amrfinderplus`, `abricate`) — created on first use (asks
first). Full rules: **[`SKILL.md`](SKILL.md)**.
