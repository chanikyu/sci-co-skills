"""figures.py — strain-tracking plots: the strain-sharing network + longitudinal persistence outcomes."""
import os
import sys

_SDV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scientific-data-viz")
if _SDV not in sys.path:
    sys.path.insert(0, _SDV)

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import journal_style as J

_OUTCOME_ORDER = ["persisted", "replaced", "undetermined"]


def sharing_network_figure(G, out_path, palette="okabe_ito", title="Strain-sharing network"):
    """Nodes = subjects/samples; edges = a shared strain (thicker = more species shared)."""
    J.set_style(palette=palette)
    fig, ax = plt.subplots(figsize=(5.2, 4.4), dpi=200)
    if G.number_of_edges() == 0:
        ax.text(0.5, 0.5, "no shared strains detected", ha="center", va="center", fontsize=9, color="#777")
        ax.axis("off"); J.save(fig, out_path); return out_path + ".png"
    pos = nx.spring_layout(G, seed=42, weight="weight")
    w = [G[u][v]["weight"] for u, v in G.edges()]
    node_c = J.palette(1)[0]
    nx.draw_networkx_edges(G, pos, ax=ax, width=[0.8 + 1.6 * x for x in w], edge_color="#8aa0b0", alpha=0.75)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_c, edgecolors="#333", linewidths=0.6,
                           node_size=[110 + 45 * G.degree(n) for n in G.nodes()])
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=6.5)
    ax.set_title(f"{title}  ({G.number_of_edges()} sharing links)", fontsize=9)
    ax.axis("off")
    J.save(fig, out_path)
    return out_path + ".png"


def persistence_figure(persist_df, out_path, palette="okabe_ito", title="Strain persistence"):
    """Stacked/colored bar of persistence outcomes across subject×species observations."""
    J.set_style(palette=palette)
    counts = persist_df["outcome"].value_counts().reindex(_OUTCOME_ORDER).fillna(0)
    cols = {"persisted": J.palette(3)[0], "replaced": J.palette(3)[1], "undetermined": "#c9c9c9"}
    fig, ax = plt.subplots(figsize=(4.4, 3.6), dpi=200)
    ax.bar(range(len(_OUTCOME_ORDER)), counts.values, color=[cols[o] for o in _OUTCOME_ORDER],
           edgecolor="#333", lw=0.5)
    for i, v in enumerate(counts.values):
        ax.text(i, v, str(int(v)), ha="center", va="bottom", fontsize=7)
    ax.set_xticks(range(len(_OUTCOME_ORDER))); ax.set_xticklabels(_OUTCOME_ORDER)
    ax.set_ylabel("subject × species observations"); ax.set_ylim(0, max(counts.values) * 1.2 + 1)
    J.finalize(ax); ax.set_title(title, fontsize=9)
    J.save(fig, out_path)
    return out_path + ".png"
