"""persist.py — longitudinal strain persistence within a subject across timepoints. Pure Python —
testable. Uses the raw distance/identity matrix so 'undetermined' (below coverage) is kept distinct
from a genuine strain 'replacement'."""
import pandas as pd

from share import is_same


def persistence(species_mat, meta, subject_col, time_col, threshold, metric="distance"):
    """For each subject with >=2 timepoints, per species: is the SAME strain retained across the subject's
    consecutive timepoints? species_mat: {species: samples×samples distance/identity matrix}.
    Returns a DataFrame: subject, species, n_timepoints, outcome
    ('persisted' = same at every consecutive step, 'replaced' = a different strain appears,
     'undetermined' = any step below coverage/breadth)."""
    rows = []
    for sp, mat in species_mat.items():
        for subj, grp in meta.groupby(subject_col):
            order = pd.to_numeric(grp[time_col], errors="coerce")          # numeric time sorts correctly
            if order.isna().any():                                          # "T1"/"T10"/"day3" → embedded int
                emb = pd.to_numeric(grp[time_col].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
                order = emb if emb.notna().all() else grp[time_col]         # else keep given (metadata) order
            samples = [s for s in grp.assign(_o=order).sort_values("_o", kind="stable").index
                       if s in mat.index]
            if len(samples) < 2:
                continue
            calls = [is_same(mat.loc[a, b], threshold, metric) for a, b in zip(samples[:-1], samples[1:])]
            if any(c is None for c in calls):
                outcome = "undetermined"
            elif all(calls):
                outcome = "persisted"
            else:
                outcome = "replaced"
            rows.append({"subject": str(subj), "species": str(sp), "n_timepoints": len(samples),
                         "outcome": outcome})
    return pd.DataFrame(rows, columns=["subject", "species", "n_timepoints", "outcome"])
