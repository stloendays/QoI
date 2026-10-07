# NC main-figure plan (7 display items; NC allows 10)

| NC fig | message | built from | file |
|---|---|---|---|
| 1 | A scientific tolerance is scored only under a qualified measurement contract (renders + contract track) | frozen Fig. 1, unchanged | `figures/composite/fig1/Fig1.*` |
| 2 | The QSQ screen prospectively stratifies numerical risk (1.600% vs 81.325% at 1e-3 e) | frozen Fig. 3, unchanged | `figures/composite/fig3/Fig3.*` |
| 3 | The Hartree operator's spectral weight explains the codec effect (frequency allocation controls Hartree fidelity) | frozen Fig. 7, unchanged | `figures/composite/fig7/Fig7.*` |
| 4 | Under equal search the closed-form law beats pointwise codecs (10.2x / 18.5x) and spectral truncation (1.32x / 1.41x), bulk and slabs | new | `figures/nc/fig3/Fig3.*` (`make_fig3.py`) |
| 5 | The operator metric carries the gain (2.12x / 3.43x); the optimizer's share is set by the system class (1.105 / 1.222) | new | `figures/nc/fig4/Fig4.*` |
| 6 | One stream certifies the Hartree potential and Bader charges together (48/48, overhead 1.000, 1.32x) | new | `figures/nc/fig5/Fig5.*` |
| 7 | The gain is predicted before compression (6 operators, 92 materials, |ln err| 0.026, Spearman 0.977) | new | `figures/nc/fig6/Fig6.*` |

New figures: QoI house style (`figures/composite/style.py`), 183 mm, svg + pdf + png at 600 dpi, overlap audit clean, every plotted
median asserted against the committed SUMMARY/RESULTS files. P1 per-material Part A tables are filtered to the 60 confirmatory
materials (the file also holds the 12 shakedown materials).

Frozen Figs. 2, 4, 5, 6 and 8 move to the Supplementary Information.

Open figure item: Fig. 1b (contract track) shows qualification → certification → diagnosis. A design/prediction station
for the operator law could be added later; the current figure is kept unchanged.
