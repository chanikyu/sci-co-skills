"""multivariate.py — PCA + PLS-DA with VIP scores, cross-validated accuracy, and a permutation test.
PLS-DA overfits easily, so the honest metric is CV accuracy validated by label permutation."""
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import StratifiedKFold


def pca_scores(X, n=2):
    p = PCA(n_components=n).fit(X.values)
    return p.transform(X.values), p.explained_variance_ratio_ * 100


def _onehot(y):
    levels = list(pd.unique(y))
    Y = np.array([[1.0 if v == lv else 0.0 for lv in levels] for v in y])
    return Y, levels


def vip_scores(pls):
    """Standard VIP from a fitted PLSRegression (mean VIP^2 = 1; conventional cutoff VIP > 1)."""
    t, w, q = pls.x_scores_, pls.x_weights_, pls.y_loadings_
    ss = (q ** 2).sum(axis=0) * (t ** 2).sum(axis=0)         # y-variance per component (n_comp,)
    wn = w / np.linalg.norm(w, axis=0)
    return np.sqrt(w.shape[0] * ((wn ** 2) @ ss) / ss.sum())


def plsda(X, y, n_components=2):
    yv = pd.Series(list(y)).astype(str).values
    Y, levels = _onehot(yv)
    nc = min(n_components, X.shape[1], X.shape[0] - 1)
    pls = PLSRegression(n_components=nc).fit(X.values, Y)
    vip = pd.Series(vip_scores(pls), index=X.columns)
    return pls, pls.x_scores_, vip, levels


def _fold_pareto(Xtr, Xte):
    """Pareto-scale using TRAIN statistics only (fit on train, apply to test) — no fold leakage."""
    mu = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0); sd[sd == 0] = 1.0
    d = np.sqrt(sd)
    return (Xtr - mu) / d, (Xte - mu) / d


def _cv_accuracy(Xv, yv, n_components, seed=0, n_splits=5):
    """Xv = transformed (log, UNSCALED); Pareto scaling is fit inside each fold to avoid leakage,
    so the accuracy is an honest cross-validated estimate (not optimistically biased)."""
    levels = list(pd.unique(yv))
    y_idx = np.array([levels.index(v) for v in yv])
    n_splits = min(n_splits, int(np.bincount(y_idx).min()))
    if n_splits < 2:
        return np.nan
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    correct = 0
    for tr, te in skf.split(Xv, y_idx):
        Xtr, Xte = _fold_pareto(Xv[tr], Xv[te])
        Ytr, lv = _onehot(yv[tr])
        nc = min(n_components, Xtr.shape[1], len(tr) - 1)
        pls = PLSRegression(n_components=nc).fit(Xtr, Ytr)
        pred = pls.predict(Xte).argmax(1)
        te_true = np.array([lv.index(v) if v in lv else -1 for v in yv[te]])
        correct += int((pred == te_true).sum())
    return correct / len(yv)


def permutation_test(X, y, n_perm=200, n_components=2, seed=0):
    """Return (cv_accuracy, permuted_accuracies, p_value). p = fraction of label-shuffles that
    match/beat the observed CV accuracy (a real class effect gives small p)."""
    rng = np.random.default_rng(seed)
    yv = pd.Series(list(y)).astype(str).values
    Xv = X.values
    obs = _cv_accuracy(Xv, yv, n_components, seed)
    perm = np.array([_cv_accuracy(Xv, rng.permutation(yv), n_components, seed + i + 1)
                     for i in range(n_perm)])
    perm = perm[~np.isnan(perm)]
    p = (np.sum(perm >= obs) + 1) / (len(perm) + 1) if perm.size else np.nan
    return obs, perm, p
