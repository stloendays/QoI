# WS-S1 — the spin channel as a measurement contract (engineering, descriptive)

- **Run.** CI run 39633829124 on 16 development-panel MP materials, chosen deterministically from the S0
  census (`S1_ENGINEERING_MANIFEST.csv`): the 12 smallest grids with max |mu_atom| ≥ 0.1 mu_B and the 4
  smallest with max |mu_atom| < 0.01 mu_B.
- **Contract.** Per-atom moments from the compiled Henkelman Bader 1.05,
  `bader CHGCAR(m) -ref REFCAR(rho) -b ongrid -vac 0.001`.
- **Outcome.** 144/144 rows OK, 0 failures.
- **Search consistency.** Moments from per-atom sums over the reference AtIndex map match the binary's ACF to
  at most 4.9e-7 mu_B. The certified error and the binary-verified error differ by at most 4.9e-7 mu_B.

## Qualification

- **Floors.** The QSQ moment floor (five frozen seeds, rho and m perturbed at their float32 amplitudes) is
  tiny: median 1.4e-5 mu_B, maximum 6.3e-3 mu_B (FeCo9).
- **Eligibility.** Eligible at tau_mu = 1e-1 and 1e-2 mu_B: 16/16. Eligible at 1e-3: 15/16 (FeCo9 is not).
  Unlike the Bader charge contract at tight tolerances, the moment contract is almost always resolvable.

## Certified compression of m (rho exact; best of ZFP/SZ3/SPERR per material)

| group | tau_mu (mu_B) | certified | median CR of m | min CR | median m bytes / lossless rho | max m bytes / lossless rho |
|---|---|---|---|---|---|---|
| magnetic (12) | 1e-1 | 12/12 | 2,114 | 573 | 0.0008 | 0.0034 |
| magnetic (12) | 1e-2 | 12/12 | 706 | 244 | 0.0032 | 0.0106 |
| magnetic (12) | 1e-3 | 12/12 | 180 | 102 | 0.0084 | 0.0252 |
| non-magnetic (4) | all | 4/4 | 1,134* | 1,049* | 0.0023* | 0.0041* |

- **Codec mix.** SZ3 wins most often: 9, 8 and 5 of 12 magnetic materials at 1e-1, 1e-2 and 1e-3, with
  SPERR taking the rest except 3 ZFP wins at 1e-3.
- **\*Search cap.** For non-magnetic objects every certified point sits at the search cap (bound
  0.1·ptp(m)). Their m is numerical noise, so these ratios are lower bounds set by the search range, not by
  the contract.
- **Total magnetization.** It is not part of the contract. At the certified points its error reached
  0.024 mu_B at 1e-2 and 0.40 mu_B at 1e-1. A user who also needs M would add it as a second contract; it
  is linear and cheap to certify.

## Reading

- **New QoI class.** Per-atom magnetic moments are a resolvable, cheaply certifiable QoI of the second block
  that every MP CHGCAR carries. Losslessly, m costs about as much as rho (median 1.03×). Under the moment
  contract it costs a median 0.3% of lossless rho at 1e-2 mu_B, at most 1.1%.
- **Archive.** This is what S2 needs: the whole served object, rho plus m, can be stored under contracts
  without the magnetization block dominating. A projection from these medians, which is not a measurement,
  puts the Hartree-law whole-object archive ratio near 227× at 1e-6, against 356× for the rho block alone.
  S2 measures it on the 300 archive objects.
