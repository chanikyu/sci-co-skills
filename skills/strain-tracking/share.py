"""share.py — same-strain calls + strain-sharing network from a per-species strain distance/identity
matrix. Pure Python — testable. Sharing != transmission (always reported as *sharing*)."""
import itertools
import numpy as np
import pandas as pd
import networkx as nx


def is_same(value, threshold, metric):
    """One pairwise call. NaN (below coverage/breadth) → None (undetermined), NOT 'different'.
    metric='distance' → same if value <= threshold; 'identity' → same if value >= threshold."""
    if pd.isna(value):
        return None
    if metric == "identity":
        return bool(value >= threshold)
    if metric == "distance":
        return bool(value <= threshold)
    raise ValueError("metric must be 'distance' or 'identity'")


def same_strain_adjacency(mat, threshold, metric="distance"):
    """mat: samples×samples strain distance/identity DataFrame for ONE species. Returns a boolean
    adjacency DataFrame (True where two samples carry the same strain). NaN → False; diagonal False."""
    if metric == "identity":
        adj = mat.ge(threshold)
    elif metric == "distance":
        adj = mat.le(threshold)
    else:
        raise ValueError("metric must be 'distance' or 'identity'")
    arr = (adj & mat.notna()).to_numpy(copy=True)
    np.fill_diagonal(arr, False)
    return pd.DataFrame(arr, index=mat.index, columns=mat.columns)


def shared_pairs(adj, meta=None, subject_col=None, cross_subject_only=False):
    """Same-strain sharing pairs for one species. cross_subject_only=True keeps only pairs from DIFFERENT
    subjects (candidate cross-host sharing, excluding one subject's own timepoints)."""
    if cross_subject_only and (meta is None or not subject_col):
        raise ValueError("cross_subject_only=True requires meta and subject_col.")
    ids = list(adj.index)
    out = []
    for a, b in itertools.combinations(ids, 2):
        if not bool(adj.loc[a, b]):
            continue
        if cross_subject_only and meta is not None and subject_col:
            if meta.loc[a, subject_col] == meta.loc[b, subject_col]:
                continue
        out.append((a, b))
    return out


def sharing_network(species_adj, meta=None, subject_col=None):
    """Aggregate per-species same-strain adjacencies into ONE cross-host sharing graph.
    Node = subject (if subject_col) else sample; edge weight = # species the two share a strain in.
    Same-subject pairs are dropped (self over time is persistence, not sharing). Returns (nx.Graph, edges DF)."""
    weight, species_of, seen = {}, {}, set()
    for sp, adj in species_adj.items():
        for a, b in shared_pairs(adj):
            na = meta.loc[a, subject_col] if (meta is not None and subject_col) else a
            nb = meta.loc[b, subject_col] if (meta is not None and subject_col) else b
            if na == nb:
                continue
            key = tuple(sorted((str(na), str(nb))))
            if (key, str(sp)) in seen:                 # count each SPECIES once per subject-pair
                continue
            seen.add((key, str(sp)))
            weight[key] = weight.get(key, 0) + 1
            species_of.setdefault(key, []).append(str(sp))
    G = nx.Graph()
    nodes = set()                                   # only subjects/samples actually profiled in some species
    for adj in species_adj.values():
        if meta is not None and subject_col:
            idx = [s for s in adj.index if s in meta.index]
            nodes.update(meta.loc[idx, subject_col].astype(str))
        else:
            nodes.update(str(x) for x in adj.index)
    G.add_nodes_from(sorted(nodes))
    for (na, nb), w in weight.items():
        G.add_edge(na, nb, weight=w, species=species_of[(na, nb)])
    edges = pd.DataFrame([{"node_a": a, "node_b": b, "n_species_shared": w,
                           "species": ";".join(species_of[(a, b)])}
                          for (a, b), w in weight.items()],
                         columns=["node_a", "node_b", "n_species_shared", "species"])
    return G, edges.sort_values("n_species_shared", ascending=False).reset_index(drop=True)
