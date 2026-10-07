"""One vector sheet of the eight NC main figures (svg + pdf + png), built with figures/composite/make_sheet.py.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_nc_sheet.py   -> Sheet_NC_main_figures.{svg,pdf,png}
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMP = os.path.join(os.path.dirname(HERE), "composite")
sys.path.insert(0, COMP)
import make_sheet as M  # noqa: E402

M.HERE = HERE                                   # outputs land next to this script


def read_svg(path):
    """As make_sheet.read_svg, with the <svg> opening tag matched on a word boundary."""
    s = open(path, encoding="utf-8").read()
    m = re.search(r"<svg\b[^>]*>", s)
    head = m.group(0)
    w = float(re.search(r"""width=['"]([0-9.]+)pt['"]""", head).group(1))
    h = float(re.search(r"""height=['"]([0-9.]+)pt['"]""", head).group(1))
    vb = re.search(r"""viewBox=['"]([^'"]+)['"]""", head).group(1)
    return w * M.PT_MM, h * M.PT_MM, vb, s[m.end():s.rindex("</svg>")]


M.read_svg = read_svg
F = lambda *p: os.path.join(HERE, *p)           # noqa: E731
C = lambda *p: os.path.join(COMP, *p)           # noqa: E731
COLUMNS = [
    [(F("fig1", "Fig1.svg"), "Figure 1   The downstream operator at each stage of certified compression", 0.72),
     (C("fig3", "Fig3.svg"), "Figure 2   The frozen QSQ screen prospectively stratifies numerical risk", 0.72),
     (C("fig7", "Fig7.svg"), "Figure 3   The Hartree operator's spectral weight explains the codec effect", 0.62),
     (F("fig4", "Fig4.svg"), "Figure 4   The operator symbol fixes where the step, the error and the bytes go", 0.72)],
    [(F("fig5", "Fig5.svg"), "Figure 5   Under equal search the law beats pointwise codecs and truncation", 0.72),
     (F("fig6", "Fig6.svg"), "Figure 6   The gain ladder: transform coding, operator weight, optimizer", 0.72),
     (F("fig7", "Fig7.svg"), "Figure 7   One stream certifies the Hartree potential and Bader charges", 0.72),
     (F("fig8", "Fig8.svg"), "Figure 8   The gain is predicted before compression", 0.72)],
]

if __name__ == "__main__":
    svg, w, h, n = M.compose("Nature Communications main figures 1–8", COLUMNS)
    open(F("Sheet_NC_main_figures.svg"), "w", encoding="utf-8").write(svg)
    print("wrote Sheet_NC_main_figures.svg  %.1f x %.1f mm, %d figures" % (w, h, n))
    M.render("Sheet_NC_main_figures", svg, w, h)
