# Option 1 draft — scoping the archive claims to the charge-density content

Status: wording draft for the owner. Not applied to `paper/MANUSCRIPT.md`.

**Budgets.** Main text + Methods is 4,992 / 5,000 words and the abstract 150 / 150, so every addition below
needs an equal cut.

**Numbers.** From `results/s0b_archive_spin_bytes_frozen_seeds/`, recomputed with the frozen bootstrap seeds
(20260930 for Bader, 20261012 for Hartree).

- **Hartree.** The published intervals are reproduced exactly: law at 1e-6, [326.6, 394.6].
- **Bader.** The interval differs slightly from the published one ([3.63, 5.41] here, [3.64, 5.46]
  published); WP-F's resampling order was not replicated.
- **Block share.** The magnetization block accounts for 51.95% of the archive's bytes (expansion estimate).
- **Block-only ratios.** Bader 2.10 [1.74, 2.61] at 1e-3 e; Hartree law 171 [157, 189] at 1e-6.

## A. Methods, "Archive estimate" (+30 words)

Append after "Objects that failed keep their stored size.":

> Every object also stores a magnetization block (52% of its serialized text; 300/300 sampled objects). Stores
> keep the total-density block only, so $R$ is quoted against that block's share of each file.

## B. Abstract (net about +4 words)

Current:

> Certified storage would shrink the 8.50 TB Materials Project archive 4.4-fold for Bader charges at
> $10^{-3}\,e$ and, with the law, 356-fold for the Hartree potential at $10^{-6}$ (pointwise: 35-fold).

Draft:

> Certified storage would shrink the charge-density content of the 8.50 TB Materials Project archive 2.1-fold
> for Bader charges at $10^{-3}\,e$ and, with the law, 171-fold for the Hartree potential at $10^{-6}$
> (pointwise: 17-fold).

## C. Results paragraphs (archive Bader; archive Hartree)

Replace the ratios with the block-only values. The block-only Bader estimates are 1.13×, 2.10× and 4.32× at
1e-4, 1e-3 and 1e-2 e. The Hartree estimates are 841×, 171× and 3.75× for the law and 16.8× for pointwise
codecs at 1e-6. Savings in TB and the "format gain" split must be recomputed on the same basis; they are not
in S0b yet.

The ratio between writers stays 10.2× (L/P, unchanged).

## D. Alternative wording that keeps whole-archive numbers (now measured, S2)

> Certified storage of the whole served objects — density and magnetization — would shrink the 8.50 TB
> Materials Project archive 4.4-fold for Bader charges at $10^{-3}\,e$ and, with the law, 316-fold for the
> Hartree potential at $10^{-6}$ (pointwise: 35-fold).

The Bader figure comes from `results/s2_archive_whole_object/`. The Hartree figure is map-free and measured
with m certified on the decoded partition at 1e-2 mu_B (`results/s2b_archive_hartree_decframe/`). A new SI
note covers the moment contract (`WS_S_SI_note_draft.md`).
