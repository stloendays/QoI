# Prior-art addendum for the reopened manuscript (Nature Communications, 2026-10-07)

Step 1 of the reopening procedure (`paper/nc_reopen/DECISIONS.md`). This addendum restates the permitted wording for
the three new claims of `paper/MANUSCRIPT.md` (law, gain prediction, joint certification) against:

- audit-H: `paper/QOAC_PRIOR_ART_NOVELTY_AUDIT_20261005.md` (QOAC-H);
- audit-P: `paper/QOAC_PROGRAM_PRIOR_ART_AUDIT_20261006.md` (claims C1–C4);
- PAV: `paper/QOAC_PROGRAM_PRIOR_ART_AUDIT_20261006_VERIFICATION.md` (verification batches 1 and 2).

Audit-P was written before the prospective results existed. Its verdicts for C1 and C2 therefore rest on 12
development materials and forbid confirmatory wording "until a frozen fresh-population protocol reproduces them". That
condition is now met for the law and for gain prediction (P1 `4164519`, P3b `eaa3267`; protocol `fe2e08a`; predictions
`d5fc30b`, `c1e6564`), and for joint certification (protocol `8a784a4`, confirmation `e4d9d0b`). This addendum updates
the wording accordingly. It does not change any audit's judgement of what is prior art. The QSQ claim keeps the
wording of the frozen manuscript and is not restated here.

## Rules that stay in force everywhere

- No "first", "novel", "unprecedented"; no "a priori" as a timing word ("predicted before compression" and
  "pre-registered" are the timing statements, backed by commit order).
- No "first QoI-aware / operator-aware / physics-informed / frequency-weighted compressor", "new bit-allocation
  method", "new coding-gain theory", "novel projection", "first multi-QoI certified compression" (audit-H "Avoid";
  audit-P "Wording to avoid everywhere").
- Classical algebra is credited where it is used: the step-size law, Lagrangian allocation, coding gain, dead-zone
  behaviour and minimum-norm constraint projection are cited, not derived as contributions.
- A citation enters the manuscript only if an audit verified its metadata. Every other source is written as
  `[CITATION NEEDED: ...]` (list at the end).

## Claim 1 — The operator law (manuscript Results 2–4; audit-P C1, audit-H)

**Evidence now available.** Prospective on two unused cohorts at tau = 1e-6: law vs equal-search pointwise codecs
10.2-fold (60/60) and 18.5-fold (32/32); law vs equal-search truncation 1.32-fold (52/60) and 1.41-fold (27/32);
operator metric vs blind metric under the same optimizer 2.12-fold (60/60) and 3.43-fold (32/32); operational
optimum over law 1.105 (bulk, CI 1.090–1.146) and 1.222 (slabs, CI 1.138–1.359)
(`analysis/general_qoac_law/results/RESULTS.md`, both `SUMMARY.json`).

**Prior art to credit.**

| work | status (audit) | what it already establishes | used in manuscript |
|---|---|---|---|
| Shlezinger, Eldar & Rodrigues, IEEE TSP 67 (2019), DOI 10.1109/TSP.2019.2935864 | verified (PAV batch 2) | Task-based quantization: quantizers designed to recover a task vector rather than the input. | ref. 20, Introduction and Discussion; the principle the paper applies. |
| Gersho & Gray (1992), DOI 10.1007/978-1-4615-3626-0 | [M+DOI] (audit-P; chapter unverified) | High-resolution allocation under weighted MSE, Delta_k ∝ w_k^(-1/2). | ref. 21, the step-size law. |
| Goyal, IEEE SPM 18 (2001), DOI 10.1109/79.952802 | verified (audit-H) | Transform coding and bit allocation framework. | ref. 22. |
| Watson, Proc. SPIE 1913 (1993), DOI 10.1117/12.152694 | [M+DOI] (audit-P) | Per-coefficient step sizes optimized for a downstream (perceptual) error model. | ref. 23. |
| Shoham & Gersho, IEEE TASSP 36 (1988), DOI 10.1109/29.90373 | [M+DOI] (audit-P) | Lagrangian allocation over arbitrary operational quantizer sets. | ref. 30, arm A3. |
| Ortega & Ramchandran, IEEE SPM 15 (1998), DOI 10.1109/79.733495 | [M+DOI] (audit-P) | Operational RD and Lagrangian allocation. | ref. 31, arm A3. |
| Ainsworth et al., SIAM J. Sci. Comput. 41 (2019) (MGARD QoI) | verified (audit-H) | Operator-norm control of derived quantities; negative Sobolev norms. | ref. 8; MGARD baseline in SI Note 2. |
| Jiao et al. (VLDB 2022); QPET (VLDB 2025); Lee et al. (2022); TOPIQ | verified (audit-H, PAV) | QoI tolerance mapped to data bounds; pointwise bound tuning; post-hoc QoI uncertainty. | refs 9, 10, 12, 14. |
| FFCz, arXiv:2601.01596 | abstract verified (PAV batch 1) | Post-decompression projection onto spatial and frequency-domain error bounds; no physical-operator weighting. | ref. 16, Introduction. |
| Mallat & Falzon (1998); Sullivan (1996) | UNVERIFIED (audit-P) | Low-rate / dead-zone departure from high-rate theory. | `[CITATION NEEDED]` in Results 3. |
| Witsenhausen (1980), indirect RD | UNVERIFIED DOI (audit-P) | Optimum when distortion is measured after a linear map. | not cited; task-based quantization carries the credit. |

**Task-based quantization (Shlezinger et al. 2019) belongs to this claim.** The principle "design the quantizer for
the task, not the signal" is theirs. The difference: their setting is hardware-limited scalar quantization with analog
combining for estimation of a task vector; ours is compression of a stored physical field whose quantizer is shaped by
an exact physical-operator symbol on the crystal reciprocal lattice, with every decoded field recertified under that
operator by a decode-verified two-sided (historical and Nyquist-safe) certificate.

**Permitted wording.**

> Task-based quantization established that a quantizer should be designed for the task it serves rather than for the
> signal itself.<sup>20</sup> Here we apply that principle to stored physical fields. The task is a physical operator
> with an exact reciprocal-space symbol, and every decoded field is recertified under that operator.

> Under high-rate scalar quantization, minimizing this weighted error at fixed rate gives the classical step-size
> law<sup>21,22</sup> $\Delta_G\propto w^{-1/2}$. [...] The allocation algebra is textbook; what the operator adds is
> the weight [...] and the certificate.

> Under equal search, the law certified 10.2-fold (60/60) and 18.5-fold (32/32) more compression than the best
> pointwise codec at $\tau=10^{-6}$.

> The operator metric carries the gain: the optimum under the operator metric certified 2.12-fold (60/60) and 3.43-fold
> (32/32) more than the same optimum under the blind metric. (Audit-P C1: "No retrieved work reports this ablation for
> an electronic-structure QoI" — usable in a reply to reviewers, not as a priority claim in the text.)

> For bulk crystals the closed-form law is within 10.5% of the operational optimum (median ratio 1.105 [...]); for
> surface slabs operational allocation adds 22% (median ratio 1.222 [...]), at a Hartree tolerance of $10^{-6}$.

**Wording to avoid.** "We derive the optimal allocation" (it is classical); "new bit-allocation / RDO method" (A3 is
Shoham–Gersho class); "near-optimal for electronic densities" or any near-optimality statement without the system
class (near-optimality holds for bulk; the slab value is stated as a class property); mixing the ladder-searched
15.016-fold (QOAC-H, SI Note 2) with the equal-search 10.2-fold in one sentence; "the law beats truncation" without
naming the tolerance (at 1e-4 truncation certifies more: 0.79 bulk, 0.69 slab).

## Claim 2 — Gain predicted before compression (manuscript Results 6; audit-P C2)

**Evidence now available.** Predictions committed before any compression (P1 `d5fc30b`, P3b `c1e6564`); all B-H1 to
B-H4 criteria pass in both cohorts: median absolute log error 0.024 (300 pairs) and 0.029 (160 pairs), Spearman 0.978
and 0.979; pooled over 92 materials 0.026 and 0.977 (`POOLED_P1_P3B.json`, `062d782`).

**Status change relative to audit-P.** Audit-P C2 forbade "predicted a priori" because both its cases were
retrospective, and it called the finite-rate correction "a diagnosis, not a validated predictor". Both objections are
now answered: the finite-rate Laplacian-ECSQ predictor was specified (`f4baa7a`), frozen with the protocol (`fe2e08a`)
and tested prospectively on two unused cohorts. The timing word remains "before compression", never "a priori".

**Prior art to credit.**

| work | status | what it already establishes | used in manuscript |
|---|---|---|---|
| Jayant & Noll, *Digital Coding of Waveforms* (1984) | [M] (audit-P) | Coding gain as an arithmetic/geometric-mean ratio under optimal allocation. | ref. 32. |
| Huang & Schultheiss (1963) | [M], DOI UNVERIFIED | Block quantization of correlated Gaussian variables; origin of coding gain. | `[CITATION NEEDED]`. |
| Wei, Shaw & Varley, ICASSP 1997 | title, pages UNVERIFIED | Perceptual (weighted) coding gain; the same object under a perceptual weight. | `[CITATION NEEDED]`. |
| Underwood et al. (2023) | [M], DOI UNVERIFIED | Black-box prediction of compression ratio from data statistics. | `[CITATION NEEDED]`. |
| Mallat & Falzon (1998); Sullivan (1996); He & Mitra (2002) | UNVERIFIED | Dead-zone and low-rate behaviour that the finite-rate model includes. | Mallat–Falzon and Sullivan as `[CITATION NEEDED]` in Results 3. |

**Permitted wording.**

> Before any compression, we computed the predicted gain for every material and operator from the operator symbol and
> the material's reference spectrum alone, with a finite-rate entropy-coded quantization model, and committed the
> predictions to the repository. [...] The predictions matched.

> The predictor is the classical coding-gain construction evaluated with a physical weight and a finite-rate dead-zone
> model.

> Its form was fixed by a retrospective calibration on 12 engineering materials and then tested only prospectively.

**Wording to avoid.** "A priori theory", "new coding-gain theory", "we derive a gain formula" without the classical
credit; any pooled-only statement that hides per-cohort values (both are reported); stating the Gaussian operator as
"predicted accurately" (predicted 17.6 and 22.0 against measured 12.1 and 15.3 — the manuscript reports both values).

## Claim 3 — Joint certification on one stream (manuscript Results 5; audit-P C3 and C4)

**Evidence now available.** Frozen protocol `8a784a4`, fresh P2 population: 48/48 jointly certified at
tau_B = 1e-3, 1e-4 and 1e-5 e; overhead 1.000 (CI 1.000–1.000) at 1e-4 e; R3 over the best other base 48/48, median
1.317 (CI 1.269–1.360) (`analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/RESULTS.md`).

**Status change relative to audit-P.** Audit-P C4 recorded the v1 joint test as a formal FAIL of its effect-size
criterion and forbade "outperforms competitors under the joint contract" as a confirmed result. HB v2 is a new protocol
frozen before any run on a fresh population, with its own effect-size criterion, which passed. The manuscript reports
the v2 result only; v1 numbers are not quoted (evidence map G4).

**Prior art to credit.**

| work | status | what it already establishes | used in manuscript |
|---|---|---|---|
| Wu et al., SC24, arXiv:2411.05333 | arXiv verified (PAV batch 2); proceedings DOI open | Error-controlled progressive retrieval guaranteeing errors on derivable QoIs composed from a basis; several QoIs controlled at once. | ref. 17, Introduction and Discussion. |
| QPET, VLDB 18 (2025) / arXiv:2412.02799 | verified (audit-H, PAV batch 2) | Preservation of most differentiable univariate and multivariate QoIs inside error-bounded compressors. | ref. 10. |
| Gong et al. (2022), CCIS 1512 | verified (frozen reference audit) | Several XGC QoIs preserved with QoI-adapted quantization. | ref. 11. |
| Lee et al., Appl. Sci. 12, 6718 (2022) | full text read 2026-10-07 (mdpi.com/2076-3417/12/13/6718, Sect. 3.2.1, Eqs. 6-23) | Constraint-satisfaction post-processing preserving QoIs on XGC: minimizes the Bregman divergence of x log x (generalized KL) between the corrected and the decompressed velocity histogram subject to four linearized moment constraints per mesh node; dual Newton solve; multiplicative correction f = f0 exp(-K); Lagrange multipliers vector-quantized and stored. | ref. 12, credited as the constraint-satisfaction framework; the uniform basin projection is its Euclidean (additive, minimum L2 and L-inf) counterpart on a real-space partition. |
| Compression Safeguards, DOI 10.5194/egusphere-2026-4266 | DOI verified (PAV batch 1) | Combinable pointwise and QoI safeguards with stored corrections. | ref. 15. |
| FFCz, arXiv:2601.01596 | abstract verified | One corrected stream jointly bounding spatial and spectral error. | ref. 16. |
| Banerjee et al. (e-Science 2023) | verified (frozen reference audit) | Scalable QoI-guaranteed pipeline. | ref. 13. |
| Coulomb-metric density fitting (Dunlap 1979; Vahtras 1993) | DOIs UNVERIFIED | Ancestor of the Hartree-aware projection. | not cited; the manuscript claims no gain from that projection. |

**Wu et al. SC24 and QPET belong to this claim.** Controlling several QoIs on one stored or retrieved representation
is established (Wu et al.; QPET; Gong et al.; Lee et al.; Compression Safeguards; FFCz). The defensible difference
(audit-P C4): the two contracts differ in kind — a global elliptic-operator norm on the reciprocal lattice with a
two-sided Nyquist-safe certificate, and integrals over a topologically defined real-space partition certified by the
production Henkelman Bader code with zero basin reassignment — and the joint result is a pre-registered effect-size
test.

**Permitted wording.**

> Several QoIs have been controlled on one stream before, in fusion data, progressive retrieval and combinable
> safeguards.<sup>11,12,15,17</sup> Here the two contracts differ in kind: a global elliptic-operator norm on the
> reciprocal lattice and integrals over a topologically defined real-space partition, certified by the production
> Bader code.

> On 48 fresh bulk crystals, one stream from the operational Hartree encoder (R3), certified for the Hartree potential
> at $10^{-6}$, was also certified for Bader charges with zero basin reassignment at $10^{-3}$, $10^{-4}$ and
> $10^{-5}\,e$ in 48/48 materials.

> [...] uniform per-basin projection, which restores each basin's charge with the minimum-norm correction in the manner
> of constraint-satisfaction post-processing.<sup>12</sup>

> The Hartree certificate already carries the Bader charges under an exact partition.

**Wording to avoid.** "First multi-QoI / joint certified compression"; "novel projection" or a theorem-style
presentation of the uniform shift (elementary; Lee et al.'s construction specialized); any gain claimed for the
Hartree-aware projection (it gave the same certified ratio as uniform projection, 1.00); "Bader-preserving
compression" or "topology-preserving" without "exact partition reference"; any generalization to arbitrary QoIs or to
slabs (the joint population is bulk only).

## Citations still needed in the manuscript

| placeholder in `paper/MANUSCRIPT.md` | reason |
|---|---|
| Mallat & Falzon 1998; Sullivan 1996 (Results 3) | DOI and pages UNVERIFIED in audit-P |
| Huang & Schultheiss 1963; Wei, Shaw & Varley 1997 (Results 6) | DOI / title UNVERIFIED in audit-P |
| Underwood et al. 2023 (Results 6) | DOI UNVERIFIED in audit-P |
| Materials Project database (Methods; Data availability) | not covered by any audit |
| NOMAD repository (Methods; Data availability) | not covered by any audit |
| AFLOW repository (Data availability) | not covered by any audit |
| Wu et al. SC24 proceedings DOI and pages (ref. 17) | open in PAV; arXiv id verified |

Open full-text checks carried over from PAV: the norm of Lee et al.'s constraint step; the full texts of Compression
Safeguards and BlockMGARD (BlockMGARD is not cited in the manuscript).
