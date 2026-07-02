"""
journal_style.py — reusable matplotlib house style for publication data figures.

Encodes the Nature/Cell/eLife journal convention: white background, no decorative
chrome (no colored cards/headers/tints), left+bottom spines only, no gridlines,
bold black panel letters, plain black titles, filled black data points, editable
vector PDF output.

Usage:
    import journal_style as J
    J.set_style()
    fig, axes = J.figure_grid(1, 3, width="2col", panel_h=2.6)
    ax = axes[0]
    ...plot with EXACT data...
    J.finalize(ax); J.panel_letter(ax, "A"); ax.set_title("...")
    J.save(fig, "myfigure")   # -> myfigure.png (300dpi) + myfigure.pdf (editable text)

Design rules baked in — do NOT override casually:
- Bars start at 0 (bar y-axis must include zero). Line/scatter y-axis may be non-zero.
- Show individual points when n is small (<~15/group).
- Colors are colorblind-safe by default.
- Error type (SD / SEM / 95% CI) must be stated by the caller in the axis label
  or caption — this module never invents error bars.
"""
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import findfont, FontProperties
from cycler import cycler

# ---- palettes ---------------------------------------------------------------
# Named QUALITATIVE palettes for nominal groups. okabe_ito / tol_vibrant are
# colorblind-safe; the journal sets (npg, aaas, lancet, nejm, jama) reproduce the
# house colors of those journals (ggsci) and read as "real paper" figures.
PALETTES = {
    # --- colorblind-safe (safest for any audience) ---
    "okabe_ito":   ["#E69F00", "#56B4E9", "#009E73", "#F0E442",
                    "#0072B2", "#D55E00", "#CC79A7", "#000000"],   # colorblind-safe
    "tol_bright":  ["#4477AA", "#EE6677", "#228833", "#CCBB44",
                    "#66CCEE", "#AA3377", "#BBBBBB"],
    "tol_muted":   ["#88CCEE", "#44AA99", "#117733", "#332288", "#DDCC77",
                    "#999933", "#CC6677", "#882255", "#AA4499", "#DDDDDD"],
    "tol_vibrant": ["#EE7733", "#0077BB", "#33BBEE", "#EE3377",
                    "#CC3311", "#009988", "#BBBBBB"],
    # --- journal house colors (ggsci) — match to the target venue ---
    "npg":         ["#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F",
                    "#8491B4", "#91D1C2", "#DC0000", "#7E6148", "#B09C85"],  # Nature
    "aaas":        ["#3B4992", "#EE0000", "#008B45", "#631879", "#008280",
                    "#BB0021", "#5F559B", "#A20056", "#808180", "#1B1919"],  # Science
    "nejm":        ["#BC3C29", "#0072B5", "#E18727", "#20854E",
                    "#7876B1", "#6F99AD", "#FFDC91", "#EE4C97"],   # NEJM
    "lancet":      ["#00468B", "#ED0000", "#42B540", "#0099B4", "#925E9F",
                    "#FDAF91", "#AD002A", "#ADB6B6", "#1B1919"],   # Lancet
    "jama":        ["#374E55", "#DF8F44", "#00A1D5", "#B24745",
                    "#79AF97", "#6A6599", "#80796B"],              # JAMA
    "jco":         ["#0073C2", "#EFC000", "#868686", "#CD534C", "#7AA6DC",
                    "#003C67", "#8F7700", "#3B3B3B", "#A73030", "#4A6990"],  # J Clin Oncol
    "d3":          ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
                    "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF"],  # D3 category10
    # --- ColorBrewer qualitative ---
    "set1":        ["#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00",
                    "#FFDD33", "#A65628", "#F781BF", "#999999"],
    "set2":        ["#66C2A5", "#FC8D62", "#8DA0CB", "#E78AC3",
                    "#A6D854", "#FFD92F", "#E5C494", "#B3B3B3"],
    "dark2":       ["#1B9E77", "#D95F02", "#7570B3", "#E7298A",
                    "#66A61E", "#E6AB02", "#A6761D", "#666666"],
    "accent":      ["#7FC97F", "#BEAED4", "#FDC086", "#FBD75B",
                    "#386CB0", "#F0027F", "#BF5B17", "#666666"],
    # --- MANY categories (12–20 colors) — use for lots of taxa / clusters ---
    "tab20":       ["#1F77B4", "#AEC7E8", "#FF7F0E", "#FFBB78", "#2CA02C",  # DEFAULT
                    "#98DF8A", "#D62728", "#FF9896", "#9467BD", "#C5B0D5",
                    "#8C564B", "#C49C94", "#E377C2", "#F7B6D2", "#7F7F7F",
                    "#C7C7C7", "#BCBD22", "#DBDB8D", "#17BECF", "#9EDAE5"],
    "set3":        ["#8DD3C7", "#FFED6F", "#BEBADA", "#FB8072", "#80B1D3",
                    "#FDB462", "#B3DE69", "#FCCDE5", "#D9D9D9", "#BC80BD",
                    "#CCEBC5", "#FFFFB3"],
    "paired":      ["#A6CEE3", "#1F78B4", "#B2DF8A", "#33A02C", "#FB9A99",
                    "#E31A1C", "#FDBF6F", "#FF7F00", "#CAB2D6", "#6A3D9A",
                    "#FFFF99", "#B15928"],
    "igv":         ["#5050FF", "#CE3D32", "#749B58", "#F0E685", "#466983",
                    "#BA6338", "#5DB1DD", "#802268", "#6BD76B", "#D595A7",
                    "#924822", "#837B8D", "#C75127", "#D58F5C", "#7A65A5",
                    "#E4AF69", "#3B1B53", "#CDDEB7", "#612A79", "#AE1F63"],
    "kelly":       ["#F3C300", "#875692", "#F38400", "#A1CAF1", "#BE0032",
                    "#C2B280", "#848482", "#008856", "#E68FAC", "#0067A5",
                    "#F99379", "#604E97", "#F6A600", "#B3446C", "#DCD300",
                    "#882D17", "#8DB600", "#654522", "#E25822", "#2B3D26"],
}
# Sequential colormaps offered for ORDINAL groups (light->dark = low->high).
# All matplotlib built-ins (no seaborn dependency).
SEQ_CMAPS = ["Blues", "viridis", "cividis", "magma", "Greens", "Purples", "YlGnBu", "YlOrRd"]

CURRENT = list(PALETTES["okabe_ito"])  # active qualitative palette
BLUE_RAMP = ["#9AA0A6", "#AECDE1", "#4E86C6", "#25517F"]  # legacy ordinal blue ramp
GREY = "#9AA0A6"
INK = "#000000"


def use_palette(name):
    """Set the active qualitative palette (also sets the axes color cycle so
    bars/lines pick these colors automatically). name in PALETTES."""
    global CURRENT
    if name not in PALETTES:
        raise ValueError(f"unknown palette '{name}'. Options: {list(PALETTES)}")
    CURRENT = list(PALETTES[name])
    plt.rcParams["axes.prop_cycle"] = cycler(color=CURRENT)
    return CURRENT


def palette(n=None, name=None):
    """Return the active (or named) qualitative palette; n colors if given
    (cycled/repeated when n exceeds the palette length)."""
    cols = PALETTES[name] if name else CURRENT
    if n is None:
        return list(cols)
    return [cols[i % len(cols)] for i in range(n)]


# Back-compat constant (stable colorblind-safe set). For the ACTIVE palette after
# use_palette(), call J.palette() instead of reading this.
CATEGORICAL = list(PALETTES["okabe_ito"])


def sequential(n, cmap="Blues", lo=0.30, hi=0.92):
    """n ordered colors from a matplotlib colormap (for ORDINAL groups: dose,
    stage, time). Use this — not a rainbow — when categories have an order."""
    cm = matplotlib.colormaps[cmap]
    return [cm(x) for x in np.linspace(lo, hi, n)]


def diverging(n, cmap="RdBu_r"):
    """n colors from a diverging map (for signed values / correlations, centered 0)."""
    cm = matplotlib.colormaps[cmap]
    return [cm(x) for x in np.linspace(0.05, 0.95, n)]


# ---- global style -----------------------------------------------------------
def _pick_font():
    for f in ("Arial", "Helvetica", "Helvetica Neue"):
        try:
            if f.lower() in findfont(FontProperties(family=f)).lower():
                return f
        except Exception:
            pass
    return "DejaVu Sans"


def set_style(base_fontsize=9, palette="tab20"):
    """Apply the journal house style globally. Call once before plotting.
    palette: name of the qualitative color set (default 'tab20'; see PALETTES / use_palette)."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [_pick_font(), "DejaVu Sans"],
        "font.size": base_fontsize,
        "axes.titlesize": base_fontsize + 2,
        "axes.labelsize": base_fontsize + 1,
        "xtick.labelsize": base_fontsize,
        "ytick.labelsize": base_fontsize,
        "legend.fontsize": base_fontsize,
        "text.color": INK,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.linewidth": 0.9,
        "axes.grid": False,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "pdf.fonttype": 42,   # editable / embeddable text in PDF
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })
    use_palette(palette)


# ---- layout -----------------------------------------------------------------
# Journal column widths (inches). Match figure width to the target column.
WIDTHS = {"1col": 3.5, "1.5col": 5.0, "2col": 7.2}  # Nature: 89 / 120 / 183 mm


def figure_grid(nrows, ncols, width="2col", panel_h=2.4, wspace=0.45, hspace=0.55):
    """Create a fig + flat list of axes sized to a journal column width."""
    w = WIDTHS.get(width, width if isinstance(width, (int, float)) else 7.2)
    fig, axes = plt.subplots(nrows, ncols, figsize=(w, panel_h * nrows), dpi=300,
                             squeeze=False)
    fig.subplots_adjust(wspace=wspace, hspace=hspace)
    return fig, [ax for row in axes for ax in row]


# ---- per-axes helpers -------------------------------------------------------
def finalize(ax):
    """Journal-clean an axes: drop top/right spines, outward ticks, no grid."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(direction="out", length=3.0, width=0.9)
    ax.set_axisbelow(True)
    return ax


def panel_letter(ax, label, dx=-0.22, dy=1.12, size=13):
    """Bold black panel letter (A, B, C...) at the top-left of a panel."""
    ax.text(dx, dy, label, transform=ax.transAxes, fontsize=size,
            fontweight="bold", va="top", ha="left")


def sig_bracket(ax, x1, x2, y, text="*", h=None, lw=0.9, fontsize=11):
    """Significance bracket spanning x1..x2 at height y with a label (e.g. '**')."""
    if h is None:
        lo, hi = ax.get_ylim()
        h = (hi - lo) * 0.02
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=lw, color=INK,
            clip_on=False)
    ax.text((x1 + x2) / 2, y + h, text, ha="center", va="bottom",
            fontsize=fontsize, clip_on=False)


def legend_outside(ax, where="right", **kw):
    """Place the legend OUTSIDE the axes so it never overlaps the data.

    where="right" (default) → to the right of the panel; "bottom" → below it.
    bbox_inches='tight' at save time keeps it in the exported file (J.save does this).
    """
    if where == "right":
        return ax.legend(bbox_to_anchor=(1.02, 1.0), loc="upper left",
                         frameon=False, borderaxespad=0.0, **kw)
    if where == "bottom":
        ncol = kw.pop("ncol", 3)
        return ax.legend(bbox_to_anchor=(0.5, -0.22), loc="upper center",
                         frameon=False, ncol=ncol, borderaxespad=0.0, **kw)
    raise ValueError("where must be 'right' or 'bottom'")


def add_sig_brackets(ax, pairs, x, y0, dy, only_sig=True, ns_thresh=0.05):
    """Draw stacked significance brackets from posthoc pairs.

    pairs: list of dicts each with 'i','j' (group indices) and a p-value under
    'p_adj' or 'p' (use stats.posthoc() output). x: list of x-positions per group.
    Shorter spans are drawn lower so brackets nest cleanly.
    """
    level = 0
    for pr in sorted(pairs, key=lambda d: abs(d["j"] - d["i"])):
        p = pr.get("p_adj", pr.get("p"))
        if only_sig and (p is None or p >= ns_thresh):
            continue
        sig_bracket(ax, x[pr["i"]], x[pr["j"]], y0 + level * dy, stars(p))
        level += 1
    return ax


def stats_text(ax, text, x=0.03, y=0.05, va="bottom", **kw):
    """Italic stats annotation (e.g. 'ANOVA p<0.001') inside the panel.

    Defaults to the LOWER-left so it never collides with a top sig_bracket or
    the panel letter/title. Move it (x, y in axes fraction) if it overlaps data.
    """
    ax.text(x, y, text, transform=ax.transAxes, ha="left", va=va,
            fontsize=plt.rcParams["font.size"] - 0.5, style="italic", **kw)


def stars(p):
    """Standard significance stars from a p-value (n.s. / * / ** / ***)."""
    return "***" if p < 1e-3 else "**" if p < 1e-2 else "*" if p < 5e-2 else "n.s."


def slope(ax, before, after, x=(0, 1), labels=("Before", "After"),
          line_color=GREY, point_color=INK, mean=True):
    """Paired/slope plot: one line per unit linking its two paired values.

    First choice for before/after on the SAME units (see plot-selection.md).
    before/after are equal-length arrays of paired measurements.
    """
    before, after = np.asarray(before), np.asarray(after)
    for b, a_ in zip(before, after):
        ax.plot(x, [b, a_], "-", color=line_color, lw=0.8, alpha=0.7, zorder=1)
    ax.scatter([x[0]] * len(before), before, s=16, color=point_color, zorder=3)
    ax.scatter([x[1]] * len(after), after, s=16, color=point_color, zorder=3)
    if mean:
        ax.plot(x, [before.mean(), after.mean()], "-o", color=CATEGORICAL[5],
                lw=2.2, ms=5, zorder=4)
    ax.set_xticks(list(x))
    ax.set_xticklabels(list(labels))
    ax.set_xlim(x[0] - 0.4, x[1] + 0.4)
    return ax


def var_label(name, pct):
    """Axis label with % variance explained, e.g. var_label('PCoA1', 56.7) ->
    'PCoA1 (56.7%)'. Use for PCoA / PCA / ordination axes."""
    return f"{name} ({pct:.1f}%)"


def jitter(x_center, n, width=0.11, rng=None):
    """Horizontal jitter positions for overlaying individual points on a bar/box."""
    rng = rng or np.random.default_rng(0)
    return x_center + rng.uniform(-width, width, n)


# ---- output -----------------------------------------------------------------
def prepare_output(base):
    """Create the standard output layout <base>/images and <base>/script and
    return (images_dir, script_dir). Save figures into images/, the .py into script/."""
    img = os.path.join(base, "images")
    scr = os.path.join(base, "script")
    os.makedirs(img, exist_ok=True)
    os.makedirs(scr, exist_ok=True)
    return img, scr


def save(fig, stem, dpi=300):
    """Save PNG (raster preview) + PDF (vector, editable text) for submission.
    Pass a stem inside an images/ dir, e.g. J.save(fig, f"{images_dir}/figure1")."""
    fig.savefig(f"{stem}.png", dpi=dpi, bbox_inches="tight", facecolor="white")
    fig.savefig(f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    return f"{stem}.png", f"{stem}.pdf"
