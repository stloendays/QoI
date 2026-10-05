# Composite figures — QSQ/QOAC-H manuscript (main Figs. 1–9, Supplementary figures, TOC and SI tables)

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
- Fig. 2 rebuilt 2026-09-30 with `advanced.py` (copied from the figure-studio skill): every row drawn
  and KDE-density coloured (a, b); per-codec x material-class slopes with material-cluster bootstrap CIs
  beside b; c as a raincloud of 1 - R^2 on a log axis with paired Wilcoxon tests; d as a bubble matrix
  over matched Hartree bins, colour centred on P90/P10 = 10. The new statistics are asserted in
  `fig2/make_fig2.py`.
- Fig. 3: the "Primary result" banner is gone; the numbers sit in the panel a flow boxes.
- Fig. 5c: the three ladders are the R script's own selection rule (ZFP pairs with ≥ 5 rungs, min /
  median / max consecutive jump) and are named in the panel titles.
- Fig. 7 is the Fourier mechanism figure. The 2026-10-05 QOAC-H integration adds reader-facing Fig. 8 from `figures/R/rendered/figure8_qoac_h_R.*`; the existing external-confirmation render is now reader-facing Fig. 9 while retaining its historical `figure8_external_confirmation` filename for provenance.
- SI tables: hairline top/bottom rules and header rule only, no vertical rules, no banded rows,
  tabular numerals right-aligned, TeX fragments converted to Unicode.

## 3D structure renders (added 2026-09-30)

Fig. 1a, Fig. 5e, Fig. 7e, Supplementary Fig. S9 and the TOC graphic carry OVITO renders of real fields.
They follow the two-stage pattern: the renders are slow and deterministic, the composition is fast.

```
render3d/prep_fields.py    frozen venv   D:\Research\QoI-final4-local\venv\Scripts\python.exe
                           -> D:\Research\QoI-ext-cache\figure3d\*.npz (outside the repo, regenerable)
render3d/build_kcn.py      render-venv   D:\Tools\render-venv\Scripts\python.exe   -> renders/kcn_*.png
render3d/build_gallery.py  render-venv                                             -> renders/gallery_*.png
render3d/scene.py          shared OVITO helpers (Tachyon + ambient occlusion, transparent PNG)
figS9/make_figS9.py, toc/make_toc.py                                               -> FigS9, TOC
```

- **Material.** KCN (mp-676693): the Fig. 5c jump case and Fig. 7 matched pair 266, so all three main
  figures show the same cell under one orthographic camera.
- **Gates in `prep_fields.py`.** Source SHA-256; value range equal to the frozen `value_ptp`; realized L∞
  within 0.95–1.05 of the frozen row; Bader re-solve identical to WP-B's pinned-stack re-solve of the same
  row (`cp_rows.csv`: error to 1e-9 relative, reassigned-voxel count exact). The re-solve differs from the
  frozen Ubuntu rows by the cross-platform amount WP-B documents, so the in-figure numbers are the frozen
  rows while the drawn voxels are the re-solve.
- **Hartree.** `build_kcn.py` imports `run_shard.safe_hartree` from the spectral audit and asserts that
  the ZFP/SZ3 RMS ratio of pair 266 reproduces its frozen value (0.1532). V (eV) = 14.40 × safe_hartree.
- **Isolevels.** ρ 0.60 e Å⁻³; Δρ ±0.5 × the smaller realized L∞ of pair 266; ΔV_H ±0.5 × the SZ3 max,
  shared by both codecs. Both codecs put ~99 % of their Hartree-weighted error at low G, so a per-codec
  level would invent a shape contrast that the data do not have. Gallery: each isosurface encloses the
  densest 15 % of non-vacuum voxels. Values are written to `renders/*_params.json`, and the figures read them.
- **Structure.** The MP KCN file has its C/N atoms in a periodic C–N–N–C–C–N–N–C chain (1.36–1.47 Å). It is
  drawn as the file gives it, with periodic-image bonds.
- Sheets: the main sheet now contains nine reader-facing figures; the right column includes the QOAC-H Fig. 8 and external-confirmation Fig. 9 through provenance-preserving paths.

## Cautions

- `paper/SUPPLEMENTARY_TABLES_FINAL.md` is read, never written. Fix a number upstream and rebuild.
- The overlap audit does not see data marks; look at the PNG after any change.
- `Sheet_*` scale figures to 0.70 (main right column 0.60); per-figure PDF/SVG are the submission artefacts.
- `render3d/prep_fields.py` gates against WP-B's `cp_rows.csv`, which currently lives in the WP-B agent
  worktree (path in the script); repoint `WPB_ROWS` if that branch is merged or moved.
