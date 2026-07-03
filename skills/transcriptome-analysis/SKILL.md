---
name: transcriptome-analysis
description: 'Use when the user has bulk RNA-seq data — raw FASTQ, or a gene count matrix — and wants the standard transcriptome pipeline: QC, quantification (Salmon / kallisto alignment-free, or STAR + featureCounts alignment-based, via --aligner), differential expression (pydeseq2), and functional enrichment (GSEA / GO / KEGG), with journal figures (PCA, volcano, heatmap). Triggers — "RNA-seq 분석", "transcriptome / 전사체 분석", "differential expression / 차등발현", "DESeq2 / pydeseq2", "이 count matrix 분석". NOT for metatranscriptome / community RNA (use metatranscriptome-analysis), single-cell (scRNA), amplicon, or shotgun.'
---

# Transcriptome Analysis

Run the standard **bulk RNA-seq** pipeline — QC → quantification → **differential expression** →
functional enrichment — from raw FASTQ or a gene count matrix, into a structured results folder.
**Same design as the other SciCo skills**: enter at any stage, conda-managed tools, user-provided
references, structured output + logs. Figures (PCA, volcano, heatmap, enrichment) reuse
**`scientific-data-viz`**; DE uses **pydeseq2** (DESeq2 model, pure Python).

## When to use

- Input is **bulk RNA-seq**: raw FASTQ + a reference, or a gene × samples count matrix, plus
  sample metadata with a condition column.
- **Not** for: metatranscriptome / community RNA (→ `metatranscriptome-analysis`), single-cell
  (scanpy/scRNA), amplicon (→ `amplicon-analysis`), or shotgun DNA (→ `shotgun-analysis`).

## Iron rule — honest DE

State the quantifier, reference + version, the design formula, the DE model, and **the multiple-
testing correction (BH-FDR)**. Report the shrinkage (if any), the contrast direction, and n per
group. Never call a gene "significant" without an adjusted p-value threshold stated. Low-count
genes are filtered (and reported), not silently dropped.

## Pipeline (stages)

```
raw FASTQ ─(fastp QC)→ trimmed ─(quantify, --aligner)→ gene × samples count matrix
   --aligner salmon | kallisto (alignment-free; needs a transcriptome index) → tx → gene counts
   --aligner star   (align to genome + GTF, then featureCounts)              → gene counts
count matrix + metadata ─(pydeseq2: size factors → dispersion → Wald test → BH-FDR)→ DE genes
                        ─(enrichment: GSEA / GO / KEGG via gseapy, optional)→ enriched sets
→ tables/ images/ (PCA, volcano, heatmap, enrichment) script/ logs/ report.md
```

Enter at any stage: **FASTQ → full; a gene count matrix → DE onward; a DE results table → figures.**

## Databases / references (user-provided)

- **Salmon / kallisto:** a transcriptome index (`--index PATH`) + a tx→gene map (`--tx2gene PATH`).
- **STAR:** a genome index (`--star-index PATH`) + annotation `--gtf PATH`.
- **Enrichment:** gene-set collections (MSigDB / GO / KEGG); gseapy can fetch, or `--gene-sets PATH`.
Missing reference → that stage is skipped with a clear note.

## Operating procedure — enter at ANY stage

`pipeline.run(input_path, metadata, condition, out_dir, from_stage=None, aligner="salmon")`
detects the input and runs everything downstream. Every run:

0. **Environment** — ensure the `scico-transcriptome` conda env (below); create if missing (ask first).
1. **Input** — take the data path from the request.
2. **Detect the stage** — `stages.detect_stage(path)` → `fastq` | `count_matrix` | `de_table`.
3. **Confirm downstream + references** — which reference/index the chosen aligner needs.
4. **Ask for reference paths** — `AskUserQuestion` for the user's index / GTF / gene-sets. No ref → skip that stage.
5–6. **Pick options from the data** — fastp thresholds from read quality; the DE **design formula** and
   **contrast** from the metadata; low-count filter from the count distribution — don't hardcode.
7. **Run + log** — each stage via `conda run -n scico-transcriptome`, teeing to `logs/<stage>.log`.
8. **Validate** — outputs exist and are sane (non-empty counts, padj ∈ [0,1], no crash); stop & report.
9. **Next stage** — repeat downstream.

## Usage

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/transcriptome-analysis")
import pipeline
pipeline.run(
    input_path="counts.csv",      # FASTQ dir / gene count matrix (genes × samples) / DE table
    metadata="metadata.csv",      # sample_id + condition column
    condition="condition",
    out_dir="/path/to/results",   # -> tables/ images/ script/ logs/ report.md
    aligner="salmon",             # "salmon" | "kallisto" | "star"
    from_stage=None,
)
```

## Differential expression

**pydeseq2** (DESeq2 negative-binomial model, pure Python) — size-factor normalization → dispersion
estimation → Wald test → **BH-FDR**. Reports log2 fold-change (optionally shrunk), adjusted p-value,
base mean. Contrast direction and reference level are stated. **counts required** (not TPM/FPKM).

## Environment (conda — auto-created if missing)

One conda env, **`scico-transcriptome`** (`environment.yml`): Python 3.12 + fastp, salmon, kallisto,
star, subread (featureCounts), pydeseq2, gseapy, and the core (matplotlib, pandas, numpy, scipy,
scikit-learn). Create if missing (ask first), then run via `conda run -n scico-transcriptome`.

```bash
conda env list | grep -q scico-transcriptome \
  || conda env create -f skills/transcriptome-analysis/environment.yml
```

Reuses **`scientific-data-viz`** for figures — keep them as siblings.

## Common mistakes

| Mistake | Fix |
|---|---|
| Running DE on TPM/FPKM | pydeseq2 needs raw **counts**; quantify to counts first |
| No low-count filter | Filter low-count genes (report the threshold) before DE |
| Uncorrected p-values | Always BH-FDR (built in); state the padj threshold |
| Batch ignored | If a batch covariate exists, include it in the design formula |
| Salmon TPM used as counts | Use `numReads` / tximport counts, not TPM |
