"""Render a visual swatch of every palette in journal_style.PALETTES so a user
can eyeball them and choose. Run:  python palette_reference.py [output_path_stem]
Default output: ./palette_reference.(png|pdf)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import journal_style as J

# group headings -> palette names (order shown top to bottom)
GROUPS = [
    ("Colorblind-safe", ["okabe_ito", "tol_bright", "tol_muted", "tol_vibrant"]),
    ("Journal house colors", ["npg", "aaas", "nejm", "lancet", "jama", "jco", "d3"]),
    ("ColorBrewer qualitative", ["set1", "set2", "dark2", "accent"]),
    ("Many categories (12-20)", ["tab20", "set3", "paired", "igv", "kelly"]),
]

J.set_style()
rows = sum(len(names) for _, names in GROUPS) + len(GROUPS)   # palettes + headers
fig, ax = plt.subplots(figsize=(11, 0.34 * rows + 0.6), dpi=300)
ax.set_xlim(0, 22); ax.set_ylim(0, rows); ax.axis("off")
fig.suptitle("scientific-data-viz — color palettes", fontsize=14, fontweight="bold", y=0.995)

y = rows
for heading, names in GROUPS:
    y -= 1
    ax.text(0, y + 0.30, heading, fontsize=11, fontweight="bold", va="center")
    for name in names:
        y -= 1
        cols = J.PALETTES[name]
        ax.text(0, y + 0.45, f"{name}  ({len(cols)})", fontsize=8.5, va="center")
        for k, c in enumerate(cols):
            ax.add_patch(Rectangle((6 + k * 0.75, y + 0.1), 0.7, 0.8,
                                   facecolor=c, edgecolor="white", lw=0.6))

stem = sys.argv[1] if len(sys.argv) > 1 else "palette_reference"
fig.savefig(f"{stem}.png", dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(f"{stem}.pdf", bbox_inches="tight", facecolor="white")
print(f"saved {stem}.png / .pdf  ({len(J.PALETTES)} palettes)")
