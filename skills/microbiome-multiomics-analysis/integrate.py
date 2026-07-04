"""integrate.py — the reliable multi-omics integration core:
cross-omic Spearman correlation (+BH-FDR), per-omic PERMANOVA (Aitchison), Procrustes + Mantel."""
import warnings
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from scipy.spatial import procrustes
from scipy.spatial.distance import pdist, squareform
from statsmodels.stats.multitest import multipletests
from skbio.stats.distance import DistanceMatrix, mantel, permanova, permdisp
from skbio.stats.ordination import pcoa


def cross_correlation(A, B, qthr=0.05, rho_thr=0.3):
    """All feature-pairs Spearman between two aligned omics (samples × features), vectorized.
    Returns (full_table, significant_table); BH-FDR is over the n_A × n_B pairs of THIS omic pair."""
    nA, nB = A.shape[1], B.shape[1]
    rho, pval = spearmanr(A.values, B.values)
    rho, pval = np.asarray(rho), np.asarray(pval)
    if rho.ndim < 2:                                 # only two variables total -> scalars
        rb, pb = np.array([[float(rho)]]), np.array([[float(pval)]])
    else:
        rb, pb = rho[:nA, nA:], pval[:nA, nA:]
    df = pd.DataFrame({
        "feature_A": np.repeat(A.columns.values, nB),
        "feature_B": np.tile(B.columns.values, nA),
        "rho": rb.ravel(), "pvalue": pb.ravel(),
    }).dropna(subset=["pvalue"])
    df["padj"] = multipletests(df["pvalue"], method="fdr_bh")[1]
    sig = df[(df["padj"] < qthr) & (df["rho"].abs() >= rho_thr)].sort_values("padj").reset_index(drop=True)
    return df, sig


def _euclidean_dm(transformed_df):
    """Euclidean distance on transformed values (= Aitchison distance when the input is CLR)."""
    d = squareform(pdist(transformed_df.values, metric="euclidean"))
    return DistanceMatrix(d, ids=[str(i) for i in transformed_df.index])


def permanova_test(transformed_df, groups, permutations=999):
    """PERMANOVA on Euclidean/Aitchison distance + a dispersion (permdisp) check. {R2, F, p, disp_p}."""
    dm = _euclidean_dm(transformed_df)
    g = [str(v) for v in groups]
    res = permanova(dm, g, permutations=permutations)
    F = float(res["test statistic"]); p = float(res["p-value"])
    a = len(set(g)); n = len(g)
    r2 = (F * (a - 1)) / (F * (a - 1) + (n - a)) if (n - a) > 0 else np.nan
    try:
        disp_p = float(permdisp(dm, g, permutations=permutations)["p-value"])
    except Exception as e:
        disp_p = np.nan
        warnings.warn(f"permdisp failed: {e}")
    return {"R2": r2, "F": F, "p": p, "disp_p": disp_p}


def concordance(A_t, B_t, permutations=999):
    """Procrustes disparity (2-axis PCoA overlay) + Mantel test (full distance matrix) between two
    omics. Lower disparity / higher Mantel r = the layers arrange samples more congruently."""
    dmA, dmB = _euclidean_dm(A_t), _euclidean_dm(B_t)
    cA = pcoa(dmA).samples.values
    cB = pcoa(dmB).samples.values
    if cA.shape[1] < 2 or cB.shape[1] < 2:
        raise ValueError("PCoA returned <2 axes — too few samples/variance for a 2-D concordance overlay.")
    mtx1, mtx2, disparity = procrustes(cA[:, :2], cB[:, :2])
    r, p, _ = mantel(dmA, dmB, method="spearman", permutations=permutations)
    return float(disparity), float(r), float(p), mtx1, mtx2


def concat_plsda(transformed, groups, n_perm=200, seed=0):
    """DIABLO substitute (DIABLO itself is R-only): per-block z-scale the transformed omics, concatenate,
    PLS-DA (sklearn) -> CV accuracy + label-permutation p + |loading| feature panel. NOT block-sparse."""
    from sklearn.cross_decomposition import PLSRegression
    from sklearn.model_selection import StratifiedKFold
    blocks, feat = [], []
    for name, t in transformed.items():
        z = (t - t.mean(axis=0)) / t.std(axis=0).replace(0, 1.0)
        blocks.append(z.values); feat += [f"{name}:{c}" for c in t.columns]
    X = np.hstack(blocks)
    yv = np.array([str(g) for g in groups])
    levels = list(pd.unique(yv))
    onehot = lambda yl: np.array([[1.0 if v == lv else 0.0 for lv in levels] for v in yl])
    nc = min(2, X.shape[1], X.shape[0] - 1)
    pls = PLSRegression(n_components=nc).fit(X, onehot(yv))
    loadings = pd.Series(np.abs(pls.x_loadings_[:, 0]), index=feat).sort_values(ascending=False)

    def cv(Xv, yl):
        idx = np.array([levels.index(v) for v in yl])
        ns = min(5, int(np.bincount(idx).min()))
        if ns < 2:
            return np.nan
        skf = StratifiedKFold(n_splits=ns, shuffle=True, random_state=seed)
        ok = 0
        for tr, te in skf.split(Xv, idx):
            m = PLSRegression(n_components=min(nc, len(tr) - 1)).fit(Xv[tr], onehot(yl[tr]))
            ok += int((m.predict(Xv[te]).argmax(1) == idx[te]).sum())
        return ok / len(yl)

    rng = np.random.default_rng(seed)
    obs = cv(X, yv)
    perm = np.array([cv(X, rng.permutation(yv)) for _ in range(n_perm)])
    perm = perm[~np.isnan(perm)]
    p = (np.sum(perm >= obs) + 1) / (len(perm) + 1) if perm.size else np.nan
    return obs, p, loadings
