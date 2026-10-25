# Study 4 — the archive under the W2 writer: results

Whole-object reduction of the 8.50 TB frame (stratified ratio estimate, 300 objects, paired bootstrap seed 20261012, 2000 resamples). Objects processed: {"V": 300, "VP": 300, "T": 300, "O": 300, "W": 300, "Q": 300}.

| writer | 1e-6 | 1e-4 | magnetization share 1e-6 / 1e-4 |
|---|---|---|---|
| V: W2S density + W2M magnetization | 1,401 (1,245–1,594) | 4,719 (3,585–6,052) | 3.8% / 34.1% |
| VP: W2S density + pointwise magnetization | 966 (862–1,091) | 1,967 (1,641–2,341) | 33.6% / 72.5% |
| W: W1S (revision 11), partition fixed | 555 (492–635) | 1,735 (1,470–2,048) | 19.4% / 65.2% |
| Q: O1S on W1 (revision 11), partition fixed | 558 (494–638) | 1,726 (1,457–2,041) | 19.6% / 65.1% |
| O: operational allocation A3 (revision 10), partition fixed | 347 (317–387) | 1,325 (1,158–1,511) | 12.0% / 49.4% |
| L: closed-form law | 316 (290–350) | 1,036 (927–1,152) | — / — |
| T: truncation (revision 10), partition fixed | 232 (211–260) | 1,115 (992–1,255) | 8.1% / 41.1% |
| P: best pointwise codec | 35 (32–37) | — | — / — |

## Criteria

- **A1 archive** V/W: 1e-6 2.523 (2.383–2.678), 1e-4 2.719 (2.223–3.314) — **met**.
- **M1 magnetization stream** 1e-06: pointwise/W2M median 30.14 (CI 25.49–35.14), W2M smaller in 298/300; moment-eligible 300, W2M certified 300, pointwise certified 300; median bytes W2M 63.0 vs pointwise 3188.5.
- **M1 magnetization stream** 0.0001: pointwise/W2M median 31.10 (CI 25.65–35.73), W2M smaller in 291/293; moment-eligible 300, W2M certified 293, pointwise certified 293; median bytes W2M 63.0 vs pointwise 3174.0.
- M1 — **met**.

## Paired ratios

| ratio | 1e-6 | 1e-4 |
|---|---|---|
| V/W | 2.523 (2.383–2.678) | 2.719 (2.223–3.314) |
| V/O | 4.033 (3.721–4.401) | 3.562 (2.873–4.391) |
| V/Q | 2.511 (2.371–2.662) | 2.735 (2.241–3.349) |
| V/L | 4.427 (4.086–4.827) | 4.554 (3.641–5.618) |
| V/T | 6.026 (5.582–6.549) | 4.231 (3.334–5.249) |
| V/P | 40.520 (35.882–46.098) | — |
| V/VP | 1.450 (1.352–1.575) | 2.399 (1.982–2.936) |
| VP/W | 1.740 (1.655–1.831) | 1.133 (1.102–1.172) |
| W/O | 1.599 (1.507–1.704) | 1.310 (1.256–1.372) |
| O/L | 1.098 (1.091–1.105) | 1.278 (1.233–1.336) |
| O/T | 1.494 (1.461–1.530) | 1.188 (1.145–1.228) |
| L/T | 1.361 (1.328–1.395) | 0.929 (0.889–0.963) |

## Density writer and partitions

- W2S variants: {"1e-06": {"all": 279, "none": 17, "written": 4, "w1s_over_w2s_rho": {"median": 1.809334596041578, "ci95": [1.7283388204154022, 1.914102619206659], "n": 300, "wins": 283, "ties": 0}}, "0.0001": {"all": 119, "none": 89, "written": 92, "w1s_over_w2s_rho": {"median": 1.158471051995826, "ci95": [1.1214453253473433, 1.221065254380005], "n": 300, "wins": 208, "ties": 1}}}
- Porod exponent of the decoded partition (shells 2–24): {"n": 299, "median": -2.9610340541062126, "iqr": [-3.22960926687822, -2.719657557802729]}

## Attribution (paired, same objects)

V/W = (VP/W) × (V/VP): the density writer (W2S against W1S, magnetization pointwise in both) and the magnetization
stream (W2M against pointwise, same W2S density and decoded partition).

| tau_H | V/W | density: VP/W | magnetization: V/VP |
|---|---|---|---|
| 1e-6 | 2.523 (2.383–2.678) | 1.740 (1.655–1.831) | 1.450 (1.352–1.575) |
| 1e-4 | 2.719 (2.223–3.314) | 1.133 (1.102–1.172) | 2.399 (1.982–2.936) |

At 1e-6 the density prediction carries most of the gain; at 1e-4, where the magnetization held 65% of W's bytes, the
W2M stream does. Stored size of the frame: V 6.13 GB (1e-6) and 1.82 GB (1e-4) against W 15.48 GB and 4.95 GB.

## Magnetization stream (M1 detail)

| tau_H | objects | W2M certified | ref.-map fallback | pointwise/W2M median | W2M smaller |
|---|---|---|---|---|---|
| 1e-6, all moment-eligible | 300 | 300 | 0 | 30.1 | 298/300 |
| 1e-6, magnetic (W2M writes shells) | 128 | 128 | — | 11.1 (532 vs 6,103 B) | 126/128 |
| 1e-6, zero field | 172 | 172 | — | 51.6 (26–75 B) | 172/172 |
| 1e-4, all moment-eligible | 300 | 293 | 7 | 31.1 | 291/293 |
| 1e-4, magnetic | 121 | 121 | — | 10.8 (614 vs 6,933 B) | 119/121 |

The two objects where pointwise is smaller (mp-1818959: 9,639 vs 7,606 B; mp-3150861: 7,159 vs 3,874 B at 1e-6) are
the same at both tolerances. The 7 fallbacks at 1e-4 are objects whose 1e-4 decoded partition does not reproduce the
reference moments for any writer (W, O fail on all 7, Q on 6, T on 4); they are stored with the reference atom map
(protocol storage rule) in every writer.

Porod exponent of the decoded Bader partition (slope of the shell-mean indicator spectrum, shells 2–24): median −2.96,
IQR −3.23 to −2.72, 5–95% −3.37 to −2.00 (299 objects); magnetic objects median −2.94. Porod's law for a sharp
interface is −4; the measured partitions fall as q^-3 (finite grid and basin-boundary roughness).

## Density gain by symmetry (W1S/W2S density bytes, 1e-6 / 1e-4)

| operations | objects | 1e-6 | 1e-4 |
|---|---|---|---|
| 1 | 52 | 2.31 | 1.54 |
| 2–8 | 175 | 1.87 | 1.21 |
| 9–24 | 49 | 1.47 | 0.99 |
| >24 | 24 | 1.12 | 0.99 |

## Certificates and review

- Density: 300/300 objects certified at both tolerances for V, T, O, W, Q; 0 Hartree values ≥ tau.
- Magnetization: every V (W2M) and VP (pointwise) certificate confirmed by the compiled Henkelman binary: max error
  0.00995 / 0.00998 mu_B (1e-6), 0.00995 / 0.00998 (1e-4); 0 ≥ 1e-2. T, O, W, Q decoded-frame moment certificates:
  300 each at 1e-6; 296, 292, 292, 294 at 1e-4; 0 ≥ 1e-2.
- Both aggregators re-run from the collected checkpoints (`v`, `trunc`, `w1`): SUMMARY.json and objects.csv
  byte-identical. `review_recompute.py` recomputes every point estimate and paired ratio from objects.csv and the
  committed L/P records (relative difference < 1e-12) and the moment-stream statistics from the checkpoints
  (`results/REVIEW_RECOMPUTE.json`).
- Criteria: **A1 met** (V/W 2.52 at 1e-6, CI lower 2.38 ≥ 1.10; 2.72 at 1e-4, CI lower 2.22 ≥ 1.3). **M1 met**
  (median 30.1 and 31.1 ≥ 2; W2M smaller in 99.3% of objects at both tolerances). **Validity met** (300/300; every
  magnetization certificate binary-confirmed).
