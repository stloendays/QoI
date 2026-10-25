# Study 3 — structure-factor prediction in the water-filling writer (W2): results

92/92 materials analyzable; failed: none.

## Criteria

- **G1 prediction gain** cr(W2S)/cr(W1S) at 1e-6: median 1.95 (95% CI 1.79–2.07), W2S smaller in 89/92 — **met**.
- **G2 closed form at the optimum with prediction** cr(O2S)/cr(W2S): 1e-06: median 0.995 (CI 0.993–0.998); 0.0001: median 0.947 (CI 0.926–0.962) — **met**.
- **Validity:** 92 analyzable; all arms certified: True; W1S reproduces revision 11: True (W1S_equals_rev11_1e-06: 92/92, W1S_equals_rev11_0.0001: 92/92) — **met**.

## Ratios (cr = raw bytes / stream bytes; median, 95% bootstrap CI, wins, range)

| ratio | median (CI) | wins | range |
|---|---|---|---|
| W2S/W1S 1e-06 all | 1.95 (1.79–2.07) | 89/92 | 0.99–3.60 |
| W2S/W1S 1e-06 P1 | 2.05 (1.84–2.24) | 57/60 | 0.99–3.60 |
| W2S/W1S 1e-06 P3B | 1.79 (1.56–1.99) | 32/32 | 1.01–3.03 |
| O2S/W2S 1e-06 all | 0.99 (0.99–1.00) | 28/92 | 0.71–1.09 |
| O2S/W2S 1e-06 P1 | 1.00 (0.99–1.00) | 20/60 | 0.71–1.06 |
| O2S/W2S 1e-06 P3B | 0.99 (0.99–1.00) | 8/32 | 0.95–1.09 |
| W2S/A3 1e-06 all | 4.47 (3.70–4.86) | 92/92 | 1.94–20.31 |
| W2S/A3 1e-06 P1 | 5.02 (4.67–6.29) | 60/60 | 2.17–20.31 |
| W2S/A3 1e-06 P3B | 3.04 (2.61–3.74) | 32/32 | 1.94–6.74 |
| W2S/A1 1e-06 all | 5.28 (4.35–5.97) | 92/92 | 2.14–21.36 |
| W2S/A1 1e-06 P1 | 6.17 (5.54–7.25) | 60/60 | 2.32–21.36 |
| W2S/A1 1e-06 P3B | 4.13 (3.90–4.40) | 32/32 | 2.14–8.49 |
| W2S/A2 1e-06 all | 6.84 (6.12–7.96) | 92/92 | 3.33–30.09 |
| W2S/A2 1e-06 P1 | 7.70 (6.47–8.59) | 60/60 | 3.33–30.09 |
| W2S/A2 1e-06 P3B | 5.45 (4.34–6.97) | 32/32 | 3.77–11.26 |
| W2S/A6 1e-06 all | 69.35 (54.21–92.47) | 92/92 | 12.16–311.66 |
| W2S/A6 1e-06 P1 | 66.24 (50.53–96.52) | 60/60 | 12.16–274.13 |
| W2S/A6 1e-06 P3B | 77.71 (55.30–123.94) | 32/32 | 23.71–311.66 |
| W2/W1S 1e-06 all | 1.00 (0.82–1.29) | 46/92 | 0.22–3.60 |
| W2/W1S 1e-06 P1 | 0.93 (0.73–1.31) | 27/60 | 0.22–3.60 |
| W2/W1S 1e-06 P3B | 1.15 (0.85–1.48) | 19/32 | 0.57–3.03 |
| W2S/W2 1e-06 all | 1.76 (1.60–1.85) | 68/92 | 1.00–7.84 |
| W2S/W2 1e-06 P1 | 1.95 (1.76–2.76) | 45/60 | 1.00–7.84 |
| W2S/W2 1e-06 P3B | 1.57 (1.33–1.68) | 23/32 | 1.00–2.37 |
| W2S/W1S 1e-06 symmetry operations 1 | 2.40 (2.02–2.91) | 18/18 | 1.67–3.60 |
| W2S/W1S 1e-06 symmetry operations 2-8 | 2.09 (1.85–2.34) | 49/49 | 1.16–3.16 |
| W2S/W1S 1e-06 symmetry operations 9-24 | 1.34 (1.09–1.68) | 12/14 | 1.00–1.99 |
| W2S/W1S 1e-06 symmetry operations >24 | 1.06 (1.01–1.09) | 10/11 | 0.99–1.47 |
| W2S/W1S 0.0001 all | 1.28 (1.12–1.34) | 68/92 | 0.98–4.32 |
| W2S/W1S 0.0001 P1 | 1.24 (1.08–1.33) | 45/60 | 0.98–3.00 |
| W2S/W1S 0.0001 P3B | 1.36 (1.12–1.79) | 23/32 | 0.99–4.32 |
| O2S/W2S 0.0001 all | 0.95 (0.93–0.96) | 8/92 | 0.44–1.04 |
| O2S/W2S 0.0001 P1 | 0.96 (0.91–0.97) | 5/60 | 0.45–1.01 |
| O2S/W2S 0.0001 P3B | 0.94 (0.89–0.96) | 3/32 | 0.44–1.04 |
| W2S/A3 0.0001 all | 3.36 (3.13–3.69) | 92/92 | 1.87–10.30 |
| W2S/A3 0.0001 P1 | 3.68 (3.17–4.26) | 60/60 | 1.87–10.30 |
| W2S/A3 0.0001 P3B | 3.15 (2.99–3.49) | 32/32 | 2.01–5.66 |
| W2S/A1 0.0001 all | 7.03 (5.98–7.49) | 92/92 | 2.23–14.04 |
| W2S/A1 0.0001 P1 | 5.81 (4.87–7.22) | 60/60 | 2.23–14.04 |
| W2S/A1 0.0001 P3B | 7.54 (7.10–8.42) | 32/32 | 4.19–11.32 |
| W2S/A2 0.0001 all | 4.61 (4.20–5.10) | 92/92 | 2.54–12.83 |
| W2S/A2 0.0001 P1 | 4.67 (4.21–5.11) | 60/60 | 2.54–12.83 |
| W2S/A2 0.0001 P3B | 4.52 (3.97–5.64) | 32/32 | 2.97–12.05 |
| W2S/A6 0.0001 all | 67.18 (57.54–81.07) | 92/92 | 9.17–319.59 |
| W2S/A6 0.0001 P1 | 50.91 (43.11–59.64) | 60/60 | 9.17–161.51 |
| W2S/A6 0.0001 P3B | 116.51 (88.61–131.54) | 32/32 | 47.96–319.59 |
| W2/W1S 0.0001 all | 0.89 (0.68–1.07) | 41/92 | 0.18–4.32 |
| W2/W1S 0.0001 P1 | 0.69 (0.57–0.91) | 20/60 | 0.18–3.00 |
| W2/W1S 0.0001 P3B | 1.19 (0.95–1.79) | 21/32 | 0.57–4.32 |
| W2S/W2 0.0001 all | 1.50 (1.23–1.61) | 64/92 | 0.99–6.35 |
| W2S/W2 0.0001 P1 | 1.69 (1.51–1.95) | 45/60 | 0.99–6.35 |
| W2S/W2 0.0001 P3B | 1.06 (1.00–1.28) | 19/32 | 0.99–1.73 |
| W2S/W1S 0.0001 symmetry operations 1 | 2.12 (1.79–2.89) | 18/18 | 1.34–4.32 |
| W2S/W1S 0.0001 symmetry operations 2-8 | 1.30 (1.22–1.37) | 47/49 | 0.99–2.12 |
| W2S/W1S 0.0001 symmetry operations 9-24 | 0.99 (0.99–1.00) | 3/14 | 0.98–1.12 |
| W2S/W1S 0.0001 symmetry operations >24 | 0.99 (0.98–0.99) | 0/11 | 0.98–0.99 |

## Writer

- Variants chosen by W2S: {"1e-06": {"all": 84, "none": 3, "written": 5}, "0.0001": {"all": 47, "none": 23, "written": 22}}
- Materials with a kept prediction: 92; median predicted shells 23.0; median SFP block 651.0 bytes.
- Certified per arm: {"W1S_1e-06": 92, "W1S_0.0001": 92, "W2S_1e-06": 92, "W2S_0.0001": 92, "W2_1e-06": 92, "W2_0.0001": 92, "O2S_1e-06": 92, "O2S_0.0001": 92}

## Attribution and comparison with the strongest baseline

- **Density prediction (SFP) is the gain.** Same water-filling writer and symmetry, prediction added: W2S/W1S median
  1.95 at 1e-6 (89/92 smaller) and 1.28 at 1e-4 (68/92). The gain is largest where symmetry gives least: 2.40 on the
  18 cells with one symmetry operation, 2.09 on 2–8 operations, 1.34 on 9–24, 1.06 above 24 (1e-6).
- **Prediction against symmetry:** W2 (prediction, no symmetry) against W1S (symmetry, no prediction) median 1.00 at
  1e-6 (46/92) and 0.89 at 1e-4 (41/92): each alone is worth about the same; together (W2S/W2) 1.76 and 1.50.
- **Strongest baseline (operational optimum O2S on the same residual curves):** cr(O2S)/cr(W2S) median 0.995 at 1e-6
  and 0.947 at 1e-4 — the closed-form allocation is at or above the Lagrangian selection with prediction (W2S at least
  as small in 64/92 and 84/92 materials). Against the law protocol's A3: 4.47-fold (1e-6) and 3.36-fold (1e-4), 92/92 each.
- **Per cohort:** P1 bulk 2.05 / 1.24, P3b slabs 1.79 / 1.36 (W2S/W1S at 1e-6 / 1e-4).

## Review

- Both aggregators re-run on `analysis/server_runs_20261025c/collected/checkpoints/sfp`: SUMMARY.json, rows.csv and
  materials.csv byte-identical to the monitor's.
- `review_recompute.py` (independent of `aggregate_sfp.py`; cr recomputed from bytes): every ratio's median, wins and N
  equal SUMMARY.json; 736/736 certified rows have historical and Nyquist-safe Hartree RMS < tau; W1S equals revision
  11's W1S bytes on 92/92 materials at both tolerances (`results/REVIEW_RECOMPUTE.json`).
