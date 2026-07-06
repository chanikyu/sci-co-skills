"""derep.py — cluster viral genomes into vOTUs (MIUViG standard: 95% ANI over 85% alignment fraction),
greedy centroid clustering with the longest genome as the representative. Input = an all-vs-all ANI/AF
table (from CheckV anicalc / megablast). Pure Python — testable without external tools."""
import pandas as pd


def _normalize_ani(df):
    """Accept either query/target/ani/af or CheckV anicalc's qname/tname/ani/qcov/tcov. The MIUViG
    alignment fraction is coverage of the SHORTER genome = max(qcov, tcov)."""
    cols = {c.lower(): c for c in df.columns}
    q, t = cols.get("query") or cols.get("qname"), cols.get("target") or cols.get("tname")
    if q is None or t is None or "ani" not in cols:
        raise ValueError(f"ANI table needs query/target (or qname/tname) + ani columns; got {list(df.columns)}")
    out = pd.DataFrame({"query": df[q].astype(str), "target": df[t].astype(str),
                        "ani": pd.to_numeric(df[cols["ani"]], errors="coerce")})
    if "af" in cols:
        out["af"] = pd.to_numeric(df[cols["af"]], errors="coerce")
    elif "qcov" in cols and "tcov" in cols:
        out["af"] = pd.concat([pd.to_numeric(df[cols["qcov"]], errors="coerce"),
                               pd.to_numeric(df[cols["tcov"]], errors="coerce")], axis=1).max(axis=1)
    else:
        raise ValueError(f"ANI table needs af (or qcov+tcov); got {list(df.columns)}")
    return out


def cluster_votus(ani_df, lengths, min_ani=95.0, min_af=85.0):
    """ani_df: query/target/ani/af (or CheckV anicalc qname/tname/ani/qcov/tcov). lengths: {genome: len}.
    Greedy: longest-first; each unassigned genome becomes a vOTU centroid and claims its still-unassigned
    neighbours within (min_ani, min_af). Returns (rep_of {genome: rep}, clusters {rep: [members]})."""
    df = _normalize_ani(ani_df)
    missing = (set(df["query"]) | set(df["target"])) - set(lengths)
    if missing:
        raise ValueError(f"{len(missing)} genome(s) in the ANI table are missing from `lengths` "
                         f"(e.g. {sorted(missing)[:3]}) — FASTA and ANI IDs must match.")
    neighbours = {}
    for q, t, a, f in df[["query", "target", "ani", "af"]].itertuples(index=False):
        if q == t or pd.isna(a) or pd.isna(f):
            continue
        if a >= min_ani and f >= min_af:
            neighbours.setdefault(q, set()).add(t)
            neighbours.setdefault(t, set()).add(q)
    order = sorted(lengths, key=lambda g: -lengths[g])          # longest first
    rep_of, clusters = {}, {}
    for g in order:
        if g in rep_of:
            continue
        members = [g] + [m for m in neighbours.get(g, ()) if m not in rep_of]
        for m in members:
            rep_of[m] = g
        clusters[g] = members
    return rep_of, clusters


def votu_summary(clusters):
    """One row per vOTU: representative + member count (how many genomes collapsed into it)."""
    df = pd.DataFrame([{"vOTU": r, "n_members": len(m)} for r, m in clusters.items()],
                      columns=["vOTU", "n_members"])
    return df.sort_values("n_members", ascending=False).reset_index(drop=True) if len(df) else df
