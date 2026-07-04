"""enrichment.py — OPTIONAL over-representation analysis (ORA) via the hypergeometric test.
Annotation-gated: needs metabolites mapped to DB IDs (KEGG/HMDB) + pathway->metabolite sets.
NOT part of the default path. Honest: results inherit annotation-confidence (MSI level) uncertainty."""
import pandas as pd
from scipy.stats import hypergeom
from statsmodels.stats.multitest import multipletests


def ora(sig_ids, sets, background):
    """sig_ids: significant metabolite IDs. sets: {pathway: [member IDs]}. background: all tested IDs."""
    sig, bg = set(sig_ids), set(background)
    M, n = len(bg), len(sig & bg)
    rows = []
    for name, members in sets.items():
        members = set(members) & bg
        K = len(members)
        if K == 0:
            continue
        k = len(sig & members)
        rows.append((name, k, K, float(hypergeom.sf(k - 1, M, K, n))))
    df = pd.DataFrame(rows, columns=["set", "hits", "set_size", "pvalue"]).sort_values("pvalue")
    if len(df):
        df["padj"] = multipletests(df["pvalue"], method="fdr_bh")[1]
    return df.reset_index(drop=True)
