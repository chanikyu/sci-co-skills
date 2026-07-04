"""pipeline.py — microbiome multi-omics integration orchestrator (reliable core + optional modules).

Align paired omics -> per-omic CLR/log -> PERMANOVA per omic -> cross-omic Spearman network (BH-FDR)
-> Procrustes + Mantel concordance. Optional: MOFA+ factors, concatenated-CLR PLS-DA.
"""
import os
import sys
import datetime
import itertools

_HERE = os.path.dirname(os.path.abspath(__file__))
_SDV = os.path.join(_HERE, "..", "scientific-data-viz")
for p in (_HERE, _SDV):
    if p not in sys.path:
        sys.path.insert(0, p)

import pandas as pd
import journal_style as J
import prep
import integrate
import figures as F


def _log(logf, msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(logf, "a") as fh:
        fh.write(line + "\n")


def _read(path):
    return pd.read_csv(path, sep="\t" if path.endswith((".tsv", ".txt")) else ",", index_col=0)


def run(omics, metadata, group_col, out_dir, min_prevalence=0.1, top_n=200, min_overlap=8,
        compositional=None, qthr=0.05, rho_thr=0.3, permutations=999,
        do_mofa=False, do_plsda=False, palette="okabe_ito"):
    img, scr = J.prepare_output(out_dir)
    tables = os.path.join(out_dir, "tables"); logs = os.path.join(out_dir, "logs")
    os.makedirs(tables, exist_ok=True); os.makedirs(logs, exist_ok=True)
    logf = os.path.join(logs, "pipeline.log")

    omic_dfs = {k: _read(v) for k, v in omics.items()}
    meta = _read(metadata)
    _log(logf, f"omics: {[(k, tuple(v.shape)) for k, v in omic_dfs.items()]}")

    aligned, meta, ids, dropped = prep.align(omic_dfs, meta, min_overlap=min_overlap)
    _log(logf, f"aligned on {len(ids)} shared samples; dropped per omic: "
               f"{ {k: len(v) for k, v in dropped.items()} }")
    groups = meta[group_col].astype(str).values
    if len(set(groups)) < 2:
        raise ValueError(f"group_col={group_col!r} has <2 groups after alignment; PERMANOVA needs >=2.")
    if len(ids) < 20:
        _log(logf, f"  WARNING: only {len(ids)} paired samples (<20) — treat all p-values as exploratory.")

    transformed = {}
    for name, df in aligned.items():
        filt = prep.filter_features(df, min_prevalence=min_prevalence, top_n=top_n)
        zero = filt.index[filt.sum(axis=1) == 0].tolist()
        if zero:
            raise ValueError(f"{name}: samples with all-zero features after filtering: {zero} — "
                             f"loosen min_prevalence or drop these samples.")
        comp = None if compositional is None else compositional.get(name)
        used_clr = comp if comp is not None else ("metabol" not in name.lower())
        transformed[name] = prep.transform_omic(name, filt, comp)
        note = "CLR" if used_clr else "log+scale"
        if comp is None:
            note += " (inferred from name — verify)"
        _log(logf, f"  {name}: {filt.shape[1]} features kept ({note})")

    # per-omic condition footprint
    perm = {name: integrate.permanova_test(t, groups, permutations) for name, t in transformed.items()}
    pd.DataFrame(perm).T.to_csv(os.path.join(tables, "permanova_per_omic.csv"))
    for name, r in perm.items():
        _log(logf, f"  PERMANOVA {name}: R2={r['R2']:.3f}, p={r['p']:.3f} (dispersion p={r['disp_p']:.3f})")
    F.permanova_figure(perm, os.path.join(img, "permanova"), palette=palette)

    # cross-omic correlation + concordance per omic pair
    result = {"n_samples": len(ids), "permanova": perm, "pairs": {}}
    for a, b in itertools.combinations(list(transformed), 2):
        full, sig = integrate.cross_correlation(transformed[a], transformed[b], qthr, rho_thr)
        grid = transformed[a].shape[1] * transformed[b].shape[1]
        n_tested = len(full)                         # constant-column pairs are dropped before FDR
        sig.to_csv(os.path.join(tables, f"crosscorr_{a}_{b}.csv"), index=False)
        _log(logf, f"  {a}×{b}: {n_tested} of {grid} pairs tested (BH-FDR per pair), "
                   f"{len(sig)} significant (q<{qthr}, |rho|>={rho_thr})")
        F.correlation_heatmap(full, sig, os.path.join(img, f"corr_{a}_{b}"), a, b, palette=palette)
        disp, mr, mp, m1, m2 = integrate.concordance(transformed[a], transformed[b], permutations)
        _log(logf, f"  {a}~{b} concordance: Procrustes m2={disp:.3f}, Mantel r={mr:.3f}, p={mp:.3f}")
        F.procrustes_figure(m1, m2, groups, os.path.join(img, f"procrustes_{a}_{b}"), a, b,
                            disp, mr, mp, palette=palette)
        result["pairs"][f"{a}~{b}"] = {"n_tested": n_tested, "grid": grid, "n_sig": len(sig),
                                       "procrustes_m2": disp, "mantel_r": mr, "mantel_p": mp}

    if do_plsda:
        obs, pp, load = integrate.concat_plsda(transformed, groups)
        load.to_csv(os.path.join(tables, "plsda_loadings.csv"), header=["abs_loading"])
        _log(logf, f"  concat-CLR PLS-DA (DIABLO substitute): CV accuracy={obs:.3f}, permutation P={pp:.3f}")
        result["plsda"] = {"cv_accuracy": round(float(obs), 3), "perm_p": round(float(pp), 3)}

    if do_mofa:
        try:
            _run_mofa(transformed, tables, logf)
        except Exception as e:                       # optional dep / stochastic — never break the core
            _log(logf, f"  MOFA+ skipped: {e}")

    pngs = [f for f in os.listdir(img) if f.endswith(".png")]
    ok = len(pngs) > 0
    _log(logf, f"validation: {'PASS' if ok else 'FAIL'} — {len(pngs)} figures, "
               f"{len([f for f in os.listdir(tables) if f.endswith('.csv')])} tables")
    result["ok"] = ok; result["log"] = logf
    return result


def _run_mofa(transformed, tables, logf):
    """Optional MOFA+ shared latent factors (needs mofapy2). Saves the trained HDF5 model — the
    factor scores (Z), loadings (W), and per-omic variance-explained (R²) are stored inside it."""
    from mofapy2.run.entry_point import entry_point
    ent = entry_point()
    data = [[t.values for t in transformed.values()]]
    ent.set_data_options(scale_views=True)
    ent.set_data_matrix(data, views_names=list(transformed),
                        samples_names=[list(next(iter(transformed.values())).index)])
    ent.set_model_options(factors=min(5, len(next(iter(transformed.values()))) - 1))
    ent.set_train_options(iter=100, convergence_mode="fast", verbose=False)
    ent.build(); ent.run()
    out = os.path.join(tables, "mofa_model.hdf5")
    ent.save(out)
    _log(logf, f"  MOFA+: model trained; factors + variance-explained saved in {out}")
