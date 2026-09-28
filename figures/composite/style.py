"""Visual system for the QoI / QSQ manuscript figures (main Figs. 1-8, SI S1-S8).

A copy of the AI4S (Catalyst-Essay) house style: 183 mm pages laid out in
millimetres, Arial 5.3-9 pt, ticks in, live text in the SVG and TrueType in the
PDF. The palette block is this project's own:

    ZFP    blue        SZ3   green       SPERR  pale blue
    eligible / certified  navy ; screen-rejected / non-evaluable  RED
    Hartree  green ; Bader  navy ; electron count  pale blue

One red per panel: red marks the thing the panel is about (the rejected cohort,
the non-evaluable branch, the threshold that matters). Everything else stays in
the blue/green family or in OTHER grey.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

INK, MID, GRID = "#1B1B1B", "#6B6F76", "#E4E4E4"
GREEN, BLUE, PALE = "#89AA7B", "#7789B7", "#9DACCB"
OTHER, RED = "#B3B8C0", "#EB6969"
TINT_G, TINT_B, PAPER = "#E4ECDE", "#E3E7F0", "#F0EEEF"
PALE_B, PALE_G, MID_G, LINE = "#C6CCDC", "#CBD7C3", "#ACBF9F", "#D6D6D6"
DARK_G, DARK_B = "#5E7A52", "#5A6480"
TINT_R = "#FBE3E3"

# semantic aliases used by the figure scripts
CODEC = {"ZFP": BLUE, "SZ3": GREEN, "SPERR": PALE}
CODEC_DARK = {"ZFP": DARK_B, "SZ3": DARK_G, "SPERR": "#6F7F9E"}
ELIGIBLE, REJECTED = DARK_B, RED
HARTREE, BADER, ELECTRON = GREEN, DARK_B, PALE
CODECS = ("ZFP", "SZ3", "SPERR")

RC = {
    "font.family": "Arial", "font.size": 7, "axes.linewidth": 0.6,
    "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK, "ytick.color": INK, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.major.size": 2.4, "ytick.major.size": 2.4, "xtick.minor.size": 1.3, "ytick.minor.size": 1.3,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.minor.width": 0.5, "ytick.minor.width": 0.5,
    "axes.labelsize": 7, "axes.labelpad": 2.0,
    "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic",
    "mathtext.bf": "Arial:bold", "mathtext.default": "regular",
    "svg.fonttype": "none", "pdf.fonttype": 42, "legend.frameon": False,
    "hatch.linewidth": 0.5,
}


class Page:
    """A figure laid out in millimetres from its bottom-left corner."""

    def __init__(self, w_mm, h_mm):
        plt.rcParams.update(RC)
        self.W, self.H = w_mm, h_mm
        self.fig = plt.figure(figsize=(w_mm / 25.4, h_mm / 25.4))

    def ax(self, x, y, w, h, **kw):
        return self.fig.add_axes([x / self.W, y / self.H, w / self.W, h / self.H], **kw)

    def canvas(self, x, y, w, h):
        """Axes with data units equal to millimetres, for schematics."""
        a = self.ax(x, y, w, h)
        a.set_xlim(0, w)
        a.set_ylim(0, h)
        a.set_aspect("equal")
        a.axis("off")
        return a

    def letter(self, ch, x, y):
        self.fig.text(x / self.W, y / self.H, ch, fontsize=9, fontweight="bold", va="top", ha="left")

    def title(self, text, x, y):
        self.fig.text(x / self.W, y / self.H, text, fontsize=7, fontweight="bold", va="top", ha="left")

    def save(self, here, stem):
        for ext in ("svg", "pdf", "png"):
            self.fig.savefig(os.path.join(here, "%s.%s" % (stem, ext)), dpi=600,
                             facecolor="white")
        print("wrote %s.{svg,pdf,png}  %.0f x %.0f mm" % (stem, self.W, self.H))


def crop_rgba(path, pad=6):
    img = mpimg.imread(path)
    a = img[:, :, 3] if img.shape[2] == 4 else (img[:, :, :3].min(axis=2) < 0.98).astype(float)
    ys, xs = np.where(a > 0.02)
    return img[max(ys.min() - pad, 0):ys.max() + pad, max(xs.min() - pad, 0):xs.max() + pad]


def boxed(ax):
    for s in ax.spines.values():
        s.set_linewidth(0.6)
    ax.tick_params(which="both", top=False, right=False)


def open_frame(ax):
    """Left and bottom spines only, the default for data panels here."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(which="both", top=False, right=False)


def grid(ax, axis="both"):
    ax.grid(True, axis=axis, color=GRID, linewidth=0.4, zorder=0)
    ax.set_axisbelow(True)


def fmt_minus(s):
    return s.replace("-", "−")


def log_ticks(ax, axis="both", subs=(2, 5)):
    """Decade ticks labelled as 10^k, minor ticks unlabelled."""
    from matplotlib.ticker import LogLocator, NullFormatter
    for a in ((ax.xaxis, ax.yaxis) if axis == "both" else
              ((ax.xaxis,) if axis == "x" else (ax.yaxis,))):
        a.set_major_locator(LogLocator(base=10, numticks=12))
        a.set_minor_locator(LogLocator(base=10, subs=subs, numticks=12))
        a.set_minor_formatter(NullFormatter())


def pow_label(k):
    return r"$10^{%d}$" % k


def thr_label(tau):
    """'10^-3 e' style threshold label from a float."""
    return r"$10^{%d}$ e" % int(round(np.log10(tau)))


def note(ax, x, y, text, ha="left", va="top", size=5.6, color=INK, box=True, **kw):
    """Small in-panel annotation, optionally with a white hairline box."""
    bbox = dict(boxstyle="square,pad=0.3", facecolor="white", edgecolor=LINE,
                linewidth=0.5) if box else None
    return ax.text(x, y, text, ha=ha, va=va, fontsize=size, color=color,
                   transform=ax.transAxes, bbox=bbox, zorder=7, **kw)
