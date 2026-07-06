"""annotate.py — metabolite annotation via matchms spectral matching (LC-MS MS2 / GC-MS EI) +
an honest MSI / Schymanski confidence level. Each query spectrum is matched to a user library by
(modified) cosine similarity; most untargeted hits are level 2-3 (putative)."""
import numpy as np
import pandas as pd


def msi_level(cosine, n_matched, has_reference_standard=False, precursor_match=False, ri_match=None):
    """Honest confidence level (Sumner-style MSI 1-4): 1 = reference standard; 2 = probable
    (strong spectral match WITH precursor accurate-mass agreement, + RI for GC-MS); 3 = putative
    (spectral match without precursor confirmation); 4 = unknown."""
    if has_reference_standard:
        return 1
    if cosine >= 0.8 and n_matched >= 6 and precursor_match and (ri_match is None or ri_match):
        return 2
    if cosine >= 0.7 and n_matched >= 3:
        return 3
    return 4


def _precursor_ok(q, lib, tol):
    a, b = q.get("precursor_mz"), lib.get("precursor_mz")
    return a is not None and b is not None and abs(float(a) - float(b)) <= tol


def annotate(query_spectra, library_spectra, tolerance=0.01, modified=False,
             cosine_min=0.7, min_matched=3, precursor_tol=0.01):
    """Match each query spectrum to its best library hit by (modified) cosine. Returns a DataFrame:
    feature, match, cosine, n_matched, precursor_match, msi_level. Level 2 needs precursor agreement."""
    from matchms.similarity import CosineGreedy, ModifiedCosineGreedy
    sim = ModifiedCosineGreedy(tolerance=tolerance) if modified else CosineGreedy(tolerance=tolerance)
    cols = ["feature", "match", "cosine", "n_matched", "precursor_match", "msi_level"]
    rows = []
    for q in query_spectra:
        best_lib, best_score, best_n = None, 0.0, 0
        for lib in library_spectra:
            r = sim.pair(q, lib)
            score, n = float(r["score"]), int(r["matches"])
            if score > best_score:
                best_lib, best_score, best_n = lib, score, n
        fid = q.get("feature_id") or q.get("compound_name") or q.get("id") or q.get("precursor_mz")
        prec = _precursor_ok(q, best_lib, precursor_tol) if best_lib is not None else False
        if best_lib is not None and best_score >= cosine_min and best_n >= min_matched:
            rows.append({"feature": fid, "match": best_lib.get("compound_name") or best_lib.get("id"),
                         "cosine": round(best_score, 3), "n_matched": best_n, "precursor_match": prec,
                         "msi_level": msi_level(best_score, best_n, precursor_match=prec)})
        else:
            rows.append({"feature": fid, "match": None,
                         "cosine": round(best_score, 3) if best_lib is not None else np.nan,
                         "n_matched": best_n, "precursor_match": False, "msi_level": 4})
    return pd.DataFrame(rows, columns=cols)


def annotation_summary(ann):
    """How many features at each MSI level (honest: most are putative 2-3, many unknown 4)."""
    return ann["msi_level"].value_counts().sort_index().rename("n_features").to_frame()
