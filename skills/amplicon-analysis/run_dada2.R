#!/usr/bin/env Rscript
# Stage 0 (amplicon): paired FASTQ -> ASV feature table via DADA2 (+ optional taxonomy).
# Run inside the conda env: conda run -n scico-amplicon Rscript run_dada2.R --input_dir ...
# Verified on a simulated 16S set (recovered 6/6 injected ASVs). Standard DADA2; tune truncLen/maxEE to your reads.
suppressMessages({library(dada2); library(optparse)})

opt <- parse_args(OptionParser(option_list = list(
  make_option("--input_dir"), make_option("--out_dir"),
  make_option("--pat_f", default = "_R1"), make_option("--pat_r", default = "_R2"),
  make_option("--trunc_f", type = "integer", default = 0),   # 0 = no truncation (use for ITS)
  make_option("--trunc_r", type = "integer", default = 0),
  make_option("--maxee_f", type = "double", default = 2),
  make_option("--maxee_r", type = "double", default = 2),
  make_option("--tax_db", default = ""),                     # DADA2 assignTaxonomy training set
  make_option("--threads", type = "integer", default = 1))))

dir.create(file.path(opt$out_dir, "filtered"), showWarnings = FALSE, recursive = TRUE)
fnFs <- sort(list.files(opt$input_dir, pattern = opt$pat_f, full.names = TRUE))
fnRs <- sort(list.files(opt$input_dir, pattern = opt$pat_r, full.names = TRUE))
sample.names <- sapply(strsplit(basename(fnFs), opt$pat_f), `[`, 1)
filtFs <- file.path(opt$out_dir, "filtered", paste0(sample.names, "_F.fastq.gz"))
filtRs <- file.path(opt$out_dir, "filtered", paste0(sample.names, "_R.fastq.gz"))
names(filtFs) <- sample.names; names(filtRs) <- sample.names

filterAndTrim(fnFs, filtFs, fnRs, filtRs,
              truncLen = c(opt$trunc_f, opt$trunc_r), maxEE = c(opt$maxee_f, opt$maxee_r),
              truncQ = 2, rm.phix = TRUE, compress = TRUE, multithread = opt$threads)
errF <- learnErrors(filtFs, multithread = opt$threads)
errR <- learnErrors(filtRs, multithread = opt$threads)
mergers <- mergePairs(dada(filtFs, err = errF, multithread = opt$threads), filtFs,
                      dada(filtRs, err = errR, multithread = opt$threads), filtRs)
seqtab <- removeBimeraDenovo(makeSequenceTable(mergers), method = "consensus",
                             multithread = opt$threads)

asv.seqs <- colnames(seqtab); asv.ids <- paste0("ASV", seq_along(asv.seqs))
ft <- seqtab; colnames(ft) <- asv.ids
write.csv(data.frame(sample_id = rownames(ft), ft, check.names = FALSE),
          file.path(opt$out_dir, "feature_table.csv"), row.names = FALSE)
writeLines(paste0(">", asv.ids, "\n", asv.seqs), file.path(opt$out_dir, "asv_sequences.fasta"))

if (nchar(opt$tax_db) > 0) {
  tax <- assignTaxonomy(asv.seqs, opt$tax_db, multithread = opt$threads)
  rownames(tax) <- asv.ids
  write.csv(data.frame(ASV = asv.ids, tax), file.path(opt$out_dir, "taxonomy.csv"), row.names = FALSE)
}
cat("DADA2 done:", nrow(ft), "samples x", ncol(ft), "ASVs\n")
