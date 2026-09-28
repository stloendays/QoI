# Composite figures — QSQ manuscript (main Figs. 1–8, Supplementary Figs. S1–S8, Tables S1–S17)

Built 2026-09-28 in the AI4S house visual system (`style.py`, a per-project copy of the
Catalyst-Essay canon). Every panel reads the frozen repository tables through `figdata.py`;
each script asserts the manuscript's frozen anchors (20.34×, 50.83×, 14,986, 143/254, 0.557,
0.0776221, 63/63, …) before drawing, so a drift in the data fails the build instead of
silently changing a number.

```
figures/composite/
    style.py        183 mm page in millimetres, Arial 5.3–9 pt, ticks in, one red per panel
    layout.py       house legend + overlap audit (run before every save)
    figdata.py      data layer: every CSV/JSON the figures use, by function
    figN/make_figN.py   -> FigN.{svg,pdf,png}     600 dpi, live text
    figSN/make_figSN.py -> FigSN.{svg,pdf,png}
    make_sheet.py   -> Sheet_main_figures.{svg,pdf,png}, Sheet_supplementary_figures.{svg,pdf,png}
    tables/build_si_tables.py -> SI_tables.{html,pdf,docx}   from paper/SUPPLEMENTARY_TABLES_FINAL.md
```

Interpreters: figures `D:\Tools\pur_bridge_env\Scripts\python.exe`; tables (needs python-docx)
`D:\Research\CatalystForge\.venv\Scripts\python.exe`. Sheets and the table PDF rasterize
through headless Chrome.

## Palette (semantic)

| role | colour |
|---|---|
| ZFP / SZ3 / SPERR | blue `#7789B7` (dark `#5A6480`) / green `#89AA7B` (dark `#5E7A52`) / pale blue `#9DACCB` |
| eligible, certified | navy `#5A6480` |
| screen-rejected, non-evaluable, the threshold under discussion | red `#EB6969` — at most one red object per panel |
| Hartree / Bader / electron count | green / navy / pale blue |
| null, inactive, identity lines | `#B3B8C0`, ink dashed |

## What changed relative to the R renders (`figures/R/rendered/`)

- No in-figure titles, subtitles or footnotes: the caption carries them (`paper/FIGURE_CAPTIONS.md`).
- Panel letters lowercase bold, outside the axes; 183 mm double-column pages, heights by content.
- Fig. 2b plots absolute realized L∞, which is the regressor behind the frozen pooled slope 1.02 /
  r 0.89; the R render plotted L∞/range under the same annotation (slope there is 1.08 / 0.93).
- Fig. 3: the "Primary result" banner is gone; the numbers sit in the panel a flow boxes.
- Fig. 5c: the three ladders are the R script's own selection rule (ZFP pairs with ≥ 5 rungs, min /
  median / max consecutive jump) and are named in the panel titles.
- Fig. 8 (external confirmation) is the former Figure 7; Fig. 7 is the Fourier mechanism figure, as
  on branch `paper/fourier-mechanism-integration-20260927`.
- SI tables: hairline top/bottom rules and header rule only, no vertical rules, no banded rows,
  tabular numerals right-aligned, TeX fragments converted to Unicode.

## Cautions

- `paper/SUPPLEMENTARY_TABLES_FINAL.md` is read, never written. Fix a number upstream and rebuild.
- The overlap audit does not see data marks; look at the PNG after any change.
- `Sheet_*` scale figures to 0.70; per-figure PDF/SVG are the submission artefacts.
