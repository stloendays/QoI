# NC main-figure plan (9 display items: 8 figures + Table 1; NC allows 10)

Revision 2 (2026-10-07, author: "figure可以再多一点点…你想办法让layout比肩nature"): one new mechanism figure (Fig. 4),
the new data figures re-laid out as asymmetric multi-panel figures, Fig. 1b extended to the operator's three roles, and
one colour code for all data figures.

| NC fig | message | panels | built from | file |
|---|---|---|---|---|
| 1 | The downstream operator acts at qualification, allocation and prediction, and certification | a renders (frozen 1a); b track with four bands | new track, frozen renders | `figures/nc/fig1/make_fig1.py` |
| 2 | The QSQ screen prospectively stratifies numerical risk (1.600% vs 81.325% at 1e-3 e) | a–d | frozen Fig. 3, unchanged | `figures/composite/fig3/Fig3.*` |
| 3 | The Hartree operator's spectral weight explains the codec effect at matched distortion | a–e | frozen Fig. 7, unchanged | `figures/composite/fig7/Fig7.*` |
| 4 | The operator symbol fixes where the step, the error and the bytes go (KCN) | a step maps; b rate–distortion; c amplitude vs step; d Hartree error per mode; e bytes per shell | new; data `compute_kcn_law.py` (frozen venv), stats `kcn_stats.py` | `figures/nc/fig4/` |
| 5 | Under equal search the law beats pointwise codecs (10.2x / 18.5x) and truncation (1.32x / 1.41x) | a, b pair scatter; c median ratios vs tau; d certified CR vs tau | new | `figures/nc/fig5/` |
| 6 | The gain ladder: transform coding (5.6x / 7.3x), operator weight (1.89x / 2.66x), optimizer (1.105x / 1.222x) | a ladder; b A3/A5; c A3/A1 | new; stats `ladder_stats.py` (aggregator bootstrap, asserted equal to SUMMARY.json) | `figures/nc/fig6/` |
| 7 | One stream certifies the Hartree potential and Bader charges together (48/48, overhead 1.000, 1.317x) | a R3 vs best other; b CR per base; c Bader error; d overhead + projections; e best post-processor | new; `POST_COUNTS.json` | `figures/nc/fig7/` |
| 8 | The gain is predicted before compression (460 pairs, Spearman 0.977; within-operator 0.79–0.89) | a tau 1e-6; b tau 1e-4; c per-operator medians; d–f within-operator ranking | new | `figures/nc/fig8/` |

Colour code (Figs. 4–8, `figures/nc/common.py` ARM): green = operator-aware (closed-form law light, operational optimum
dark), blue = operator-blind transform coding, navy = spectral truncation, grey = pointwise codecs; cohort is the marker
(filled circle = bulk, open triangle = slab). Operators in Fig. 8 keep their own palette.

All figures: QoI house style (`figures/composite/style.py`), 183 mm, svg + pdf + png at 600 dpi, overlap audit clean,
PNG inspected. Every plotted statistic is asserted against the committed SUMMARY/RESULTS files or written to a committed
stats JSON by the figure's own script. P1 per-material Part A tables are filtered to the 60 confirmatory materials.

Supplementary Fig. 1 (Bader storage contracts): `figures/nc/si/figS1/make_figS1.py`.

Frozen Figs. 2, 4, 5, 6 and 8 of the frozen manuscript move to the Supplementary Information.
