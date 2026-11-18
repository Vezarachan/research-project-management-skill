"""House figure style (research-project-management skill). Lives at code/src/paperfigs/plotstyle.py.

Every number here is at FINAL PRINT SIZE: figures are created at the width they will be
printed (84 mm single column, 180 mm full width; AAG Annals), so a 7 pt label stays 7 pt.
Never draw on a large canvas and let the journal shrink it - text falls below 6 pt.

    from paperfigs.plotstyle import use, figure, panel_label, save, PALETTE
    from paperfigs.paths import fig_dir
    use()
    fig, axes = figure("full", height_mm=90, ncols=2)
    panel_label(axes[0], "a", "Standard CRC fails regionally")
    save(fig, fig_dir() / "fig_flood-results")  # -> .pdf (vector) + .png (600 dpi preview)

File names follow figure-standard.md section 2: fig_<topic> / figS_<topic>, never versions or dates.

Affinity Designer figures follow the same numbers: document width 84 or 180 mm, Aptos,
panel label/title 9 pt, body 7 pt, nothing below 6.5 pt. Check with scripts/check_figures.py.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt

FONT = "Aptos"               # house font; change here only if a venue mandates another
SIZE_PANEL = 9               # panel label (bold letter) and panel title (regular), same line
SIZE_BODY = 7                # axis labels, legends, box text
SIZE_SMALL = 6.5             # tick labels, map annotations - the floor (AAG: > 6 pt)
LINE_AXIS = 0.6              # pt; AAG minimum for any line is 0.3 pt
LINE_DATA = 1.2
WIDTH_MM = {"single": 84, "full": 180}
MAX_HEIGHT_MM = 240          # incl. caption
DPI = 600

# Define the project's colours ONCE here; Affinity figures use the same hex values.
# Keep meanings fixed across all figures (e.g. red = fails / above tolerance).
# Colours must stay distinguishable in greyscale, or be paired with line style / marker.
PALETTE = {
    "fail": "#B2373D",       # above tolerance, missed, worse
    "pass": "#3E6FA8",       # below tolerance, better
    "neutral": "#9A9A9A",    # at tolerance, baseline, context
    "method": "#7C6BC4",     # the proposed method
    "baseline": "#C9C9C9",   # comparison methods
}

MM = 1 / 25.4


def use():
    mpl.rcParams.update({
        "font.family": FONT,
        "font.size": SIZE_BODY,
        "axes.labelsize": SIZE_BODY,
        "axes.titlesize": SIZE_BODY,
        "legend.fontsize": SIZE_BODY,
        "xtick.labelsize": SIZE_SMALL,
        "ytick.labelsize": SIZE_SMALL,
        "mathtext.fontset": "custom",       # math in the house font, not DejaVu
        "mathtext.rm": FONT,
        "mathtext.it": f"{FONT}:italic",
        "mathtext.bf": f"{FONT}:bold",
        "axes.unicode_minus": True,
        "axes.linewidth": LINE_AXIS,
        "xtick.major.width": LINE_AXIS,
        "ytick.major.width": LINE_AXIS,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "lines.linewidth": LINE_DATA,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "pdf.fonttype": 42,                 # embed TrueType, text stays editable
        "svg.fonttype": "none",
        "savefig.dpi": DPI,
    })


def figure(width="full", height_mm=None, **subplots_kw):
    """Figure at final print width ('single' | 'full' | mm as number)."""
    w = WIDTH_MM.get(width, width)
    h = height_mm or w * 0.6
    if h > MAX_HEIGHT_MM - 40:
        print(f"plotstyle: {h:.0f} mm tall leaves little room for the caption (page {MAX_HEIGHT_MM} mm)")
    return plt.subplots(figsize=(w * MM, h * MM), layout="constrained", **subplots_kw)


def panel_label(ax, letter, title="", x=0.0, y=1.02):
    """House panel heading: bold lowercase letter + regular sentence-case title, e.g. '**a** Pecos River basin'.

    Result panels state the finding ('GeoCRC keeps every region within alpha');
    context panels name the subject ('Pecos River basin'). No final period.
    """
    text = rf"$\mathbf{{{letter}}}$" + (f" {title}" if title else "")
    ax.text(x, y, text, transform=ax.transAxes, ha="left", va="bottom", fontsize=SIZE_PANEL)


def save(fig, stem, png=True):
    """Vector PDF for LaTeX + 600 dpi PNG preview. Submission TIFFs: scripts/export_submission_figures.sh."""
    fig.savefig(f"{stem}.pdf")
    if png:
        fig.savefig(f"{stem}.png", dpi=DPI)
