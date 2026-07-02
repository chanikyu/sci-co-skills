"""
stats.py — OPTIONAL statistical testing for scientific-data-viz.

Compute the standard test for a comparison and return an honest result dict
(FULL test name, statistic + symbol, exact p, df where defined, parametric flag).
The viz layer (journal_style) only annotates p-values you supply; this module is
where the p-values are actually COMPUTED — keep it explicit and opt-in.

Annotate figures with report() so the FULL test name is written out
(e.g. "Mann–Whitney U test, U = 41.0, P = 0.003") — never a bare "U, p" / "t, p".

Honesty rules baked in:
- Auto-selection picks parametric vs non-parametric from a normality check
  (Shapiro–Wilk); the choice is reported so you can override it.
- Multiple pairwise comparisons are corrected (Holm by default).
- Returns the EXACT p-value; the caller decides stars via journal_style.stars().
- Never fabricates a result: too-small samples raise or return a clear note.
"""
import numpy as np
from itertools import combinations
from scipy import stats


def _stars(p):
    return "***" if p < 1e-3 else "**" if p < 1e-2 else "*" if p < 5e-2 else "n.s."


def _all_normal(*arrays, alpha=0.05):
    """True if every group passes Shapiro–Wilk (n>=3). Basis for parametric choice."""
    for a in arrays:
        a = np.asarray(a, float)
        if len(a) < 3 or stats.shapiro(a).pvalue <= alpha:
            return False
    return True


def compare(groups, paired=False, parametric="auto"):
    """Compare 2+ groups; auto-picks the appropriate test.

    2 groups:  paired  → paired t-test / Wilcoxon signed-rank test
               unpaired→ Welch's t-test / Mann–Whitney U test
    3+ groups: one-way ANOVA / Kruskal–Wallis test
    Returns {test (full name), stat, stat_symbol, df, p, parametric, k, note}.
    """
    groups = [np.asarray(g, float) for g in groups]
    k = len(groups)
    if parametric == "auto":
        parametric = _all_normal(*groups)
    note = "parametric choice: Shapiro–Wilk normality test"
    df = None
    if k == 2:
        a, b = groups
        if paired:
            if parametric:
                stat, p = stats.ttest_rel(a, b); name, sym, df = "paired t-test", "t", (len(a) - 1,)
            else:
                stat, p = stats.wilcoxon(a, b); name, sym = "Wilcoxon signed-rank test", "W"
        else:
            if parametric:
                stat, p = stats.ttest_ind(a, b, equal_var=False); name, sym = "Welch's t-test", "t"
            else:
                stat, p = stats.mannwhitneyu(a, b, alternative="two-sided"); name, sym = "Mann–Whitney U test", "U"
    else:
        N = sum(len(g) for g in groups)
        if parametric:
            stat, p = stats.f_oneway(*groups); name, sym, df = "one-way ANOVA", "F", (k - 1, N - k)
        else:
            stat, p = stats.kruskal(*groups); name, sym, df = "Kruskal–Wallis test", "H", (k - 1,)
    return {"test": name, "stat": float(stat), "stat_symbol": sym, "df": df,
            "p": float(p), "parametric": bool(parametric), "k": k, "note": note}


def posthoc(groups, labels=None, paired=False, parametric="auto", correction="holm"):
    """Pairwise comparisons across 3+ groups with multiple-testing correction.
    Returns [{i, j, label_i, label_j, test, p_raw, p_adj, stars}]. correction: 'holm'|'bonferroni'.
    """
    groups = [np.asarray(g, float) for g in groups]
    labels = labels or [f"g{i}" for i in range(len(groups))]
    if parametric == "auto":
        parametric = _all_normal(*groups)
    pairs = list(combinations(range(len(groups)), 2))
    res = [compare([groups[i], groups[j]], paired=paired, parametric=parametric) for i, j in pairs]
    p_adj = _correct([r["p"] for r in res], correction)
    return [{"i": i, "j": j, "label_i": labels[i], "label_j": labels[j], "test": r["test"],
             "p_raw": r["p"], "p_adj": float(pa), "stars": _stars(pa)}
            for (i, j), r, pa in zip(pairs, res, p_adj)]


def _correct(pvals, method="holm"):
    p = np.asarray(pvals, float)
    n = len(p)
    if method == "bonferroni":
        return np.minimum(p * n, 1.0)
    order = np.argsort(p)                 # Holm–Bonferroni (step-down)
    adj = np.empty(n)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (n - rank) * p[idx])
        adj[idx] = min(running, 1.0)
    return adj


def correlation(x, y, method="pearson"):
    """Pearson (linear) or Spearman (rank/monotonic) correlation with p-value."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if method == "spearman":
        r, p = stats.spearmanr(x, y); name, sym = "Spearman rank correlation", "rs"
    else:
        r, p = stats.pearsonr(x, y); name, sym = "Pearson correlation", "r"
    return {"test": name, "r": float(r), "stat_symbol": sym, "p": float(p), "n": len(x)}


def chi_square(table):
    """Chi-squared test of independence on a contingency table (rows × cols)."""
    chi2, p, dof, _ = stats.chi2_contingency(np.asarray(table))
    return {"test": "chi-squared test", "stat": float(chi2), "stat_symbol": "chi2",
            "df": (int(dof),), "p": float(p)}


def logrank(t1, e1, t2, e2):
    """Two-group log-rank test for survival. t = times, e = event(1)/censored(0)."""
    t = np.r_[np.asarray(t1, float), np.asarray(t2, float)]
    e = np.r_[np.asarray(e1, float), np.asarray(e2, float)]
    g = np.r_[np.zeros(len(t1)), np.ones(len(t2))]
    O1 = E1 = V = 0.0
    for tt in np.unique(t[e == 1]):
        at = t >= tt
        n = at.sum(); n1 = (at & (g == 0)).sum()
        d = ((t == tt) & (e == 1)).sum(); d1 = ((t == tt) & (e == 1) & (g == 0)).sum()
        if n <= 1:
            continue
        E1 += d * n1 / n; O1 += d1
        V += d * (n1 / n) * (1 - n1 / n) * (n - d) / (n - 1)
    chi2 = (O1 - E1) ** 2 / V if V > 0 else 0.0
    return {"test": "log-rank test", "stat": float(chi2), "stat_symbol": "chi2",
            "df": (1,), "p": float(stats.chi2.sf(chi2, 1))}


# ---- beta diversity / ordination (distance-matrix based) --------------------
def bray_curtis(table):
    """Bray–Curtis dissimilarity matrix (n×n) from a samples × features table."""
    X = np.asarray(table, float)
    n = X.shape[0]
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = np.abs(X[i] - X[j]).sum() / (X[i] + X[j]).sum()
            D[i, j] = D[j, i] = d
    return D


def pcoa(dist):
    """Classical PCoA (principal coordinates analysis) of a distance matrix.
    Returns {coords: n×k array, var_explained: % per axis}. Label plot axes with
    var_explained (e.g. 'PCoA1 (56.7%)') — journal_style.var_label() does this."""
    D = np.asarray(dist, float)
    n = D.shape[0]
    B = -0.5 * (np.eye(n) - np.ones((n, n)) / n) @ (D ** 2) @ (np.eye(n) - np.ones((n, n)) / n)
    vals, vecs = np.linalg.eigh(B)
    idx = np.argsort(vals)[::-1]
    vals, vecs = vals[idx], vecs[:, idx]
    pos = vals[vals > 0].sum()
    coords = vecs * np.sqrt(np.clip(vals, 0, None))
    return {"coords": coords, "var_explained": np.clip(vals, 0, None) / pos * 100}


def permanova(dist, groups, permutations=999, seed=0):
    """PERMANOVA (Anderson 2001): do groups differ in multivariate (beta-diversity)
    space? Distance-matrix based, tested by permutation. Returns pseudo-F, R², and
    a permutation p-value. This is the standard test to accompany a PCoA plot."""
    D = np.asarray(dist, float)
    n = D.shape[0]
    groups = np.asarray(groups)
    labs = np.unique(groups)
    a = len(labs)
    D2 = D ** 2
    tri = np.triu_indices(n, 1)
    SS_T = D2[tri].sum() / n

    def ss_within(g):
        s = 0.0
        for lab in labs:
            idx = np.where(g == lab)[0]
            ng = len(idx)
            if ng > 1:
                s += D2[np.ix_(idx, idx)][np.triu_indices(ng, 1)].sum() / ng
        return s

    SS_W = ss_within(groups)
    F = ((SS_T - SS_W) / (a - 1)) / (SS_W / (n - a))
    rng = np.random.default_rng(seed)
    count = 1
    for _ in range(permutations):
        SSw = ss_within(rng.permutation(groups))
        Fp = ((SS_T - SSw) / (a - 1)) / (SSw / (n - a))
        if Fp >= F:
            count += 1
    return {"test": "PERMANOVA", "stat": float(F), "stat_symbol": "pseudo-F",
            "R2": float((SS_T - SS_W) / SS_T), "p": count / (permutations + 1),
            "permutations": permutations, "df": (a - 1, n - a)}


def report(res, italic_p=False):
    """Format a full annotation string with the FULL test name written out, e.g.
    'Mann–Whitney U test, U = 41.0, P = 0.003' or 'one-way ANOVA, F(3, 28) = 12.4, P < 0.001'.
    Use this for figure annotations instead of a bare statistic symbol."""
    p = res["p"]
    ps = "P < 0.001" if p < 1e-3 else f"P = {p:.3f}"
    if res["test"] == "PERMANOVA":
        return f"PERMANOVA, pseudo-F = {res['stat']:.2f}, R² = {res['R2']:.2f}, {ps}"
    if "r" in res:  # correlation
        return f"{res['test']}, {res['stat_symbol']} = {res['r']:.2f}, {ps} (n = {res['n']})"
    sym, val, df, name = res.get("stat_symbol", ""), res.get("stat"), res.get("df"), res["test"]
    if name == "one-way ANOVA" and df:
        stat_str = f"F({df[0]}, {df[1]}) = {val:.2f}"
    elif df and len(df) == 1 and sym in ("H", "t", "chi2"):
        stat_str = f"{sym}({df[0]}) = {val:.2f}"
    else:
        stat_str = f"{sym} = {val:.1f}" if sym == "U" else f"{sym} = {val:.2f}"
    return f"{name}, {stat_str}, {ps}"
