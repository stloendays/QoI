# Pointwise Error Bounds Do Not Define Chemical Fidelity: Stability-Qualified Compression of Electron Densities

**Integrated manuscript draft v0.4 — 2026-09-08**

This version supersedes the 2026-09-06 writing draft. It integrates the final 63/63 frozen external confirmatory audit, the matched-realized-L∞ analysis, the independent Henkelman/BaderKit robustness supplement, and the final provenance record. Frozen scientific results are not rewritten or redefined by this manuscript revision.

## Abstract

Error-bounded lossy compression can reduce the storage and I/O cost of scientific fields, but a bound on reconstructed field values need not bound the error of a downstream scientific observable. We test this distinction for Bader charges derived from electronic-structure charge densities using 6,343 successful compressed reconstructions of 254 development materials and three general-purpose compressors, SZ3, ZFP and SPERR. Reusing Bader basins from the uncompressed field strongly suppresses the dominant downstream error channel: across 4,627 successful base-ladder reconstructions, re-deriving the partition gives larger Bader error than fixed-basin scoring in 99.7% of cases. A representative direct decomposition gives a median bounded domain-migration contribution of 0.995. Equal nominal tolerance is also not an equal-distortion comparison: ZFP realizes only ~0.158 of its requested L∞ bound, whereas SZ3 and SPERR nearly saturate theirs. After matching reconstructions within material at comparable measured L∞, ZFP retains lower resolved-Bader error than SZ3 and SPERR, demonstrating that scalar pointwise magnitude alone does not determine chemical fidelity. A second constraint precedes compression itself: under a preregistered five-seed Protocol A.1 perturbation test, 41.4% of 319 systems are non-evaluable at a 10^-3 e Bader-charge contract and 79.9% at 10^-4 e. The resulting stability-qualified rate–fidelity predictions were then tested on a pre-frozen external cohort. All 63 confirmatory systems completed, with 1,689 retained rows, zero material-level pipeline failures and zero error-bound violations; all three pre-specified codec-ordering expectations reproduced. Finally, an independent 12-material robustness panel showed that Henkelman Bader reproduces the BaderKit on-grid perturbation response with a median codec-response ratio of 1.00 (IQR 0.92–1.005), while spatial rearrangement of the same error-value multiset changes the response and periodic translation is approximately null. Together, these results support a QoI-aware certification workflow in which actual distortion is measured, the downstream analysis is re-executed, numerical resolvability is established, and scientific fidelity is validated independently of both the development corpus and a single Bader implementation.

## Introduction

Scientific simulations and instruments increasingly generate volumetric fields at rates that make storage, transfer and repeated analysis expensive. Error-bounded lossy compression addresses this pressure by allowing controlled numerical distortion in exchange for large reductions in data volume. Scientific compressors such as ZFP, SZ3 and SPERR expose pointwise-error controls that are attractive because they are explicit, inexpensive to verify and largely independent of the downstream application [1–3].

The scientist, however, rarely makes decisions from individual field values. Scientific conclusions are usually derived from quantities of interest (QoIs): integrated observables, extrema, interfaces, critical points, segmentations, transport coefficients, atomic charges or other outputs of a post-processing pipeline. Prior work has established that raw-data error control and downstream-QoI fidelity are distinct problems. QoI-preserving compression can derive guarantees for selected operators [4], while topology-aware methods preserve extrema, contour trees, Morse–Smale structures or local order that a scalar pointwise bound alone does not protect [5–9]. More recent frameworks model compression-error correlation or expose task-specific compression–QoI trade-offs [10,11]. The methodological question is therefore not whether downstream structure can matter in principle, but how a scientifically defensible fidelity contract should be defined and validated for a particular analysis.

Electron density is a stringent test because chemically meaningful quantities can depend on integration domains that are themselves derived from the field. In Bader's atoms-in-molecules construction, space is partitioned into atomic basins separated by zero-flux surfaces, and atomic charges are obtained by integrating the density over those basins [12,13]. Grid-based implementations follow local ascent relations to assign field points to atomic regions [13]. Compression can therefore change a Bader charge through two channels: the density values can change inside a fixed basin, and the basin itself can move. The second contribution is a domain error. An evaluation that reuses the original basins when scoring a reconstructed field suppresses this channel by construction and no longer reproduces the analysis that would actually be run after decompression.

A second issue arises before compression is evaluated. A QoI can function as an accuracy contract only if the reference analysis is numerically resolvable at the requested scale. If perturbations at the numerical representation scale move the downstream result by more than the proposed scientific threshold, assigning a codec pass or fail at that threshold creates false precision. The perturbation used to measure stability must itself be capable of disturbing the mathematical structure used by the downstream algorithm.

Here we separate scientific compression into four layers: reconstruction, QoI resolvability, downstream fidelity and independent validation. We benchmark SZ3, ZFP and SPERR on 254 DFT electron-density fields; re-run Bader partitioning on every reconstruction; measure actual rather than nominal L∞ error; and qualify materials using a calibrated five-seed stability protocol before certification. We then control realized distortion by within-material matching, decompose charge error into integrand and domain terms, and test whether basin reassignment statistically accounts for codec-associated residuals. Finally, we challenge the development findings in a pre-frozen 63-system external cohort and with an independent Bader implementation. The objective is not to declare one compressor universally best. It is to define the evidence required before an error-bounded reconstruction can be called chemically trustworthy.

## Results

### 1. The benchmark separates reconstruction error from chemical fidelity

The released development master table contains 6,343 successful compressed reconstructions of 254 materials: 4,627 rows on the base tolerance ladder and 1,716 rows on a tighter ladder. Each row records the requested error tolerance, measured `realized_Linf`, compression ratio, fixed-basin Bader error, Bader error after re-deriving the partition, basin reassignment diagnostics and Protocol-A.1 eligibility. Downstream failures are retained explicitly in a registry rather than converted into successes or silently dropped.

The primary fidelity metric is

\[
\Delta Q_{\mathrm{resolved}}=\max_a\left|Q_a[\tilde\rho,\mathcal B(\tilde\rho)]-Q_a[\rho,\mathcal B(\rho)]\right|,
\]

where \(\rho\) is the original density, \(\tilde\rho\) the reconstruction and \(\mathcal B\) the Bader partition derived from its argument. A fixed-basin diagnostic instead evaluates the reconstruction on \(\mathcal B(\rho)\):

\[
\Delta Q_{\mathrm{fixed}}=\max_a\left|Q_a[\tilde\rho,\mathcal B(\rho)]-Q_a[\rho,\mathcal B(\rho)]\right|.
\]

Across all 4,627 successful base-ladder rows, the re-derived error exceeds the fixed-basin estimate in 99.7% of cases. The pooled ratio is strongly right-skewed and can reach orders of magnitude; the robust statement is directional rather than a universal multiplicative constant. Reusing the original partition therefore measures a useful diagnostic, but not the chemical error of the analysis that would actually be run on the decompressed field.

This full-corpus result also corrects an early pilot interpretation. A small pilot suggested that changing from fixed to re-derived basins could reverse the identity of the best codec. The full benchmark does not support that claim: ZFP is generally the best of the tested codecs under both metrics. What survives is more important methodologically—the fixed-basin shortcut systematically hides domain migration and can substantially understate downstream error.

### 2. Domain migration dominates the representative mechanism set

For atomic basin \(\Omega_a\), the charge perturbation can be written as

\[
\Delta Q_a=\Delta Q_{a,\mathrm{integrand}}+\Delta Q_{a,\mathrm{domain}},
\]

where the first term changes density values on the reference domain and the second captures the consequence of changing the domain itself. We evaluated this decomposition on a stability-stratified 12-material mechanism panel across three codecs and three compression tolerances. The successful material–codec–tolerance cases close to numerical precision.

Because cancellation can make \(|\Delta Q_{\mathrm{domain}}|/|\Delta Q_{\mathrm{total}}|>1\), dominance is summarized by the bounded quantity

\[
f_{\mathrm{domain}}=\frac{|\Delta Q_{\mathrm{domain}}|}{|\Delta Q_{\mathrm{domain}}|+|\Delta Q_{\mathrm{integrand}}|}.
\]

The median bounded domain contribution is 0.995 (IQR 0.965–0.999), and 84.9% of successful cases exceed 0.90. In this representative panel, the measured maximum-atom error is therefore dominated by movement of the field-derived integration domain rather than by integrating a slightly perturbed density over a fixed atom.

The full benchmark supports the same mechanism at population scale. In material-fixed-effect models at the 10^-3 e A.1 contract, controlling measured L∞ but not basin reassignment gives codec multipliers of 2.34 for SZ3 relative to ZFP and 2.08 for SPERR relative to ZFP. Adding the reassigned-voxel fraction attenuates these multipliers to 0.96 and 0.94. The reassignment term has a log–log coefficient of 0.880 [0.723, 1.037] with \(p=5.78\times10^{-28}\). We interpret this as mechanism-consistent attenuation, not as formal causal mediation: basin reassignment is a post-compression variable and a voxel count does not encode where exchanged volume is located or how much charge it carries.

A global conservation proxy does not produce the same attenuation. Adding absolute total electron-count deviation leaves the SZ3/ZFP and SPERR/ZFP multipliers essentially intact, whereas basin reassignment collapses them toward unity. When both terms are present, the electron-count term is not significant, while the reassignment coefficient remains strongly associated with resolved-Bader error. The codec-associated residual is therefore linked to redistribution among field-derived domains rather than to simple global integral drift.

### 3. Equal nominal tolerance confounds error-budget utilization with reconstruction structure

Every successful reconstruction respects its requested pointwise bound, but the codecs use that bound differently. The median ratio

\[
L_{\infty,\mathrm{realized}}/L_{\infty,\mathrm{nominal}}
\]

is approximately 0.158 for ZFP and approximately 1.000 for SZ3 and SPERR. Equal requested tolerance therefore does not provide equal actual perturbation. Same-nominal comparisons materially exaggerate the apparent ZFP advantage.

We controlled this confounding by matching codec operating points within each material on \(\log_{10}(\mathrm{realized}\ L_\infty)\). At the primary 0.10-decade caliper, ZFP/SZ3 resolved-Bader error is 0.557 [0.525, 0.598], ZFP/SPERR is 0.601 [0.534, 0.662], and SZ3/SPERR is 1.033 [0.976, 1.072]. Equivalently, at comparable measured L∞, SZ3 carries about 1.79 times the resolved-Bader error of ZFP and SPERR about 1.66 times. The result is stable across 0.05–0.30-decade calipers.

This residual is decision-relevant. At \(\tau=10^{-2}\) e among jointly A.1-eligible matched pairs, ZFP certification exceeds SZ3 by 14.9 percentage points and SPERR by 17.0 percentage points at the primary caliper, while SZ3 and SPERR are statistically similar. Thus, controlling the maximum pointwise perturbation removes a large part of the same-nominal difference but not all of it. The supported conclusion is deliberately narrow: scalar L∞ magnitude alone does not determine chemical fidelity, and the remaining codec-associated difference is consistent with differences in error-field organization and domain migration.

### 4. Bader charge has a protocol-defined numerical resolvability floor

A codec should be scored against a Bader-charge threshold \(\tau\) only if the uncompressed analysis is stable at that scale. Protocol A.1 defines a material-specific numerical stability floor by adding uniform noise \(U(-\epsilon_i,+\epsilon_i)\), where \(\epsilon_i\) is that material's float32 round-trip L∞ amplitude, re-deriving the Bader partition for five preregistered seeds, and taking the maximum atom-wise charge deviation. A material is eligible only when this floor is below \(\tau\).

Across the full 319-system stability corpus, 255 systems (79.9%) are non-evaluable at \(10^{-4}\) e, 132 (41.4%) at \(10^{-3}\) e and 31 (9.7%) at \(10^{-2}\) e. These are not codec failures. They are reported as `NON_EVALUABLE_BADER_UNSTABLE` and excluded from codec pass/fail certification at that scientific contract.

Protocol A.1 replaced, rather than silently edited, an earlier frozen Protocol A based on a deterministic float32 round trip. The round trip is order-preserving for unequal values and is unusually benign for an on-grid watershed that follows local ascent. In an 18-material calibration study, the archived probe creates many exact neighboring ties and frequently produces zero reassignment; matched-amplitude random noise perturbs the relevant discrete structure more effectively. Single-seed floors also vary materially, which is why A.1 uses five preregistered seeds and takes the maximum response.

The A.1 floor is operational, not an intrinsic constant of the material. It depends on perturbation family, amplitude, seed aggregation and Bader implementation. Throughout the manuscript, it is therefore described as a **Protocol-A.1 numerical stability floor at the stated perturbation amplitude**.

### 5. Stability-qualified compression produces a contract-dependent rate–fidelity frontier

Once non-evaluable systems are separated, practical compressor selection becomes a joint problem in certified compression ratio and coverage. On the development set at \(\tau=10^{-2}\) e, the bulk median best certified ratio is about 52.0× for SZ3, 30.0× for ZFP and 11.6× for SPERR; SZ3 achieves the highest rate, while ZFP retains very high coverage. For slab systems the same loose-contract trade-off is more pronounced, with SZ3 reaching about 69.6× and ZFP about 40.5×.

The ordering changes as the chemical contract tightens. At \(10^{-3}\) e, bulk SZ3 and ZFP are essentially tied at about 12.9× and 13.5×, respectively. At \(10^{-4}\) e, ZFP leads the development bulk frontier at 7.6×, compared with 6.3× for SZ3 and 4.2× for SPERR. The engineering conclusion is therefore not that one codec is universally superior. The best operating point depends on the downstream contract, the desired coverage and the degree to which each codec uses its nominal error budget.

### 6. The pre-frozen external cohort reproduces all directional rate–fidelity expectations

The strongest test of the development findings is whether they survive on systems that were not used to formulate or tune the rate–fidelity conclusions. The external corpus contains 65 frozen systems. Two were designated before the corpus-scale run as implementation sentinels because their rate–fidelity behavior had already been inspected during harness validation; the remaining 63 form the primary confirmatory cohort.

The final confirmatory audit completed all 63/63 systems. The frozen aggregator retained 1,689 successful rows, recorded three row-level Bader-solver failures, and reported zero material-level pipeline failures and zero pointwise-bound violations. Protocol-A.1 eligibility counts exactly matched the pre-frozen expectations: 16 systems at \(10^{-4}\) e, 42 at \(10^{-3}\) e and 57 at \(10^{-2}\) e. The confirmatory builder returned `PASS` without changing the split, thresholds, codec set, Bader settings, tolerance ladder, early-stop semantics or certification logic.

The three pre-specified directional expectations all reproduced. At \(10^{-4}\) e, median certified compression ratios are 13.03 [7.09, 20.43] for ZFP, 12.06 [7.28, 17.72] for SZ3 and 5.17 [4.23, 6.23] for SPERR. At \(10^{-3}\) e, ZFP and SZ3 are effectively tied at 18.76 [14.27, 25.04] and 18.76 [12.14, 24.56], while SPERR is 6.40 [5.88, 6.88]. At \(10^{-2}\) e, the ordering reverses to SZ3 > ZFP > SPERR, with medians 65.89 [40.67, 101.85], 40.57 [35.40, 46.03] and 10.82 [10.18, 12.44], respectively.

Material-level paired comparisons reinforce the loose-contract result: at \(10^{-2}\) e, SZ3 beats ZFP in 89.47% of eligible materials (bootstrap interval 80.70–96.49%). At \(10^{-4}\) e, ZFP beats SZ3 in 68.75% of eligible materials; the direction agrees with development, but the separation is smaller and the confidence interval includes substantial uncertainty. We therefore avoid language such as “strongly superior” at the tightest threshold. The external result supports the directional ordering, not numerical identity of effect sizes.

The completed external audit also closes an important failure-accounting loophole. The final material, `aflow-Cl1O12Pb5V3_ICSD_203074`, was recovered using the exact frozen CHGCAR bytes and SHA-256 identity. A broken AFLOW property endpoint was replaced only at the transport layer by metadata from the same AFLOW entry, cross-checked independently against `OUTCAR.static.xz` and the CHGCAR atom counts. No scientific parameter changed. The 65-system descriptive aggregate therefore also reaches 65/65 material completeness.

### 7. An independent Bader implementation reproduces the perturbation sensitivity

External validation addresses dataset dependence, but a separate concern is implementation dependence: could the observed instability be a peculiarity of BaderKit? We therefore ran an independent supplement on 12 development materials selected by Protocol-A.1 stability stratum, with one separately labeled probe-failure sentinel. The supplement used BaderKit 0.10.2 and Henkelman Bader 1.05 in on-grid and near-grid modes and generated 1,560/1,560 expected outcome rows.

For 10 of the 12 representative materials, Henkelman on-grid reproduces the BaderKit on-grid five-seed noise floor to print precision. Across codec perturbations, the Henkelman/BaderKit on-grid response ratio has a median of 1.00 and an IQR of 0.92–1.005. The two large exceptions are precisely the materials whose unperturbed per-atom charges already differ between implementations because of persistence/basin-set differences; they therefore identify an implementation-sensitive baseline rather than a compression-specific discrepancy.

The codec ordering is also robust. At relative tolerance \(10^{-4}\), the SZ3/ZFP Bader-error ratio is 6.2× under BaderKit, 4.8× under Henkelman on-grid and 3.2× under Henkelman near-grid; SPERR/ZFP is 6.7×, 5.5× and 2.9×, respectively. The absolute magnitude depends on implementation, but the qualitative sensitivity ordering survives.

A spatial-control experiment further narrows the mechanism. Keeping the exact error-value multiset but randomly permuting its spatial arrangement moderately changes the Bader response, with the clearest increase for SZ3 and a smaller effect for ZFP. A density-stratified permutation gives the same directional conclusion while limiting unphysical movement of errors between dense and vacuum regions. In contrast, periodic translation of the entire error field is approximately null. The supported interpretation is therefore not that a single boundary-local statistic has been proven causal, but that **error organization beyond scalar magnitude matters**, and that destroying spatial autocorrelation changes the downstream response.

The independent supplement also reproduces the decomposition logic. For codec rows, the median bounded domain share is approximately 0.990, compared with ~0.02 for the float32 round-trip perturbation. This explains why the archived order-preserving stability probe was misleading and independently reinforces the central distinction between small value perturbations and movement of field-derived domains.

## Discussion

### Scientific fidelity requires a contract at the level of the downstream analysis

The results separate quantities that are often collapsed into one notion of compression accuracy. A nominal codec tolerance is not the error actually realized. A realized scalar field norm does not uniquely determine a field-derived downstream error. The downstream quantity may itself be numerically unresolved at the requested threshold. And an apparent mechanism should not be trusted until it survives both out-of-sample data and an independent implementation check.

The practical evaluation rule is straightforward: **if the downstream analysis derives its own domains, labels or topology from the reconstructed field, that analysis must be re-executed during validation.** Reusing the original partition can make the QoI artificially stable by construction. Bader charge is a chemically meaningful example because domain migration dominates the representative decomposition and statistically accounts for the matched-L∞ codec-associated residual across the development benchmark.

### The matched-L∞ residual is smaller than the nominal gap but more informative

The distinction between nominal and realized error changes the codec story materially. ZFP's strong same-nominal performance is partly mechanical because it uses only about one sixth of the requested L∞ budget. Once actual pointwise magnitude is matched, the gap contracts to approximately 1.7–1.8× relative to SZ3/SPERR rather than the much larger nominal comparison. This smaller residual is scientifically stronger evidence because the obvious magnitude confounder has been controlled.

The residual should not be described as a pure “topology effect.” Matching L∞ controls one scalar norm, not RMSE, correlation length, localization or every statistic of the error field. What the evidence supports is a hierarchy: scalar maximum amplitude is insufficient; codec-associated structure remains; basin reassignment absorbs that residual statistically; direct domain decomposition shows the relevant mathematical channel; spatial permutation changes the response; and an independent Bader implementation retains the qualitative ordering. This convergence of orthogonal controls is more persuasive than any single large effect size.

### External confirmation changes the status of the main claims

Before the final external run, the central conclusions were development findings supported by internal controls. They are now externally supported. The frozen 63-system cohort reproduces all three pre-specified rate–fidelity directions, exact A.1 eligibility denominators, high ZFP certification at tight thresholds, the ZFP≈SZ3 tie at the intermediate threshold, and the SZ3 advantage at the loose threshold.

The external data are not numerically identical to development, nor should they be. The tight-threshold ZFP–SZ3 difference narrows substantially. This is useful rather than problematic: it identifies which parts of the development story are stable in direction but variable in magnitude. In a confirmatory framework, preserving the pre-specified direction and failure semantics is more important than reproducing the original point estimates.

### Implementation robustness narrows the remaining methodological uncertainty

The independent Henkelman analysis removes a major alternative explanation: the main perturbation response is not specific to BaderKit. It also shows where implementation dependence genuinely exists. A small subset of materials has different unperturbed basin sets across solvers, so their absolute stability floors are implementation-dependent. This is exactly why the manuscript uses the phrase “protocol-defined numerical stability floor” and avoids presenting the floor as an intrinsic constant of the material.

The appropriate scientific claim is therefore not solver invariance of every atomic charge. It is robustness of the central qualitative conclusions: field-derived domains dominate the sensitive response; the codec ordering persists across implementations; and spatial organization of error matters beyond the maximum pointwise distortion.

### Stability qualification changes the semantics of failure

`NON_EVALUABLE_BADER_UNSTABLE` is intentionally neither a pass nor a codec failure. Treating an unstable reference as a codec failure would penalize a compressor for a precision the downstream analysis cannot reliably define. Ignoring instability would create false precision. The eligibility layer separates these cases explicitly.

The same principle applies to row-level solver failures. The final external analysis records three such rows rather than deleting their materials or converting them to successful points. Material-level completeness can coexist with row-level failure when other operating points succeed. This distinction makes denominators auditable and prevents selective survival from silently favoring one codec.

### Scope and limitations

Bader charge is a demanding exemplar, not a claim about all scientific QoIs. Smooth algebraic functionals may have much tighter relationships between field norms and downstream error, whereas partition-, threshold- or topology-dependent observables can respond discontinuously to local perturbations. Extending the workflow to additional electronic-structure quantities will determine how broadly the same stability and re-derivation logic applies.

The direct mechanism panel is deliberately stratified rather than population-representative. It supports mechanism characterization, not prevalence estimation. Full-benchmark reassignment models and the external cohort triangulate the same failure mode, but they do not turn the 12-material decomposition into a population frequency estimate.

The three compressors span important general-purpose algorithmic families but are not exhaustive. Recent topology- and local-order-preserving compressors may better protect the structures relevant to Bader analysis [5–9]. Their omission limits comparative scope but does not weaken the central methodological conclusion that a pointwise bound is not, by itself, a chemical-fidelity contract.

Protocol A.1 is operational. Its floor depends on perturbation amplitude, perturbation family, seed aggregation and solver implementation. The independent solver check makes that dependence explicit rather than eliminating it. The protocol should therefore be transferred to other QoIs by preserving its logic—measure numerical resolvability under an analysis-relevant perturbation—not by assuming the same noise distribution or threshold is universal.

## Conclusions

A scientific compressor should not be judged solely by whether it respects a pointwise error bound. In this electron-density benchmark, fixed-domain scoring misses the dominant Bader error channel, equal nominal tolerances produce unequal realized perturbations, matched L∞ does not eliminate codec-associated chemical differences, and many systems do not support the requested Bader-charge precision before compression is introduced. A stability-qualified certification framework resolves these ambiguities by separating field error, QoI resolvability, downstream fidelity and failure semantics.

The evidence now spans three independent axes. Within the development benchmark, matched-distortion and mechanism analyses show that scalar L∞ does not uniquely determine Bader fidelity and that domain migration is the dominant sensitive channel. In a pre-frozen external cohort, all 63 confirmatory systems complete and all three directional rate–fidelity expectations reproduce. In a separate robustness study, an independent Henkelman implementation preserves the central perturbation response and codec ordering. The resulting conclusion is not that one compressor is universally best. It is that **trustworthy scientific compression requires a downstream contract: measure the distortion actually realized, establish that the QoI is numerically defined, re-run the analysis that will be used scientifically, and certify the rate only where that complete chain remains valid.**

## Methods

### Data, provenance and benchmark strata

The development compression benchmark contains 254 charge-density fields: 186 bulk materials and 68 slab systems. The frozen external corpus contains 37 AFLOW bulk systems and 28 NOMAD vacuum-containing two-dimensional systems. Two external records were designated in advance as implementation sentinels; the remaining 63 constitute the primary confirmatory rate–fidelity cohort. Together, the development and external corpora form the 319-system stability corpus. Source URLs, byte counts, hashes, formulas, grid sizes and atom counts are recorded in `materials_metadata.csv` and `external_test_MANIFEST.json`. No new DFT calculations were required for the released benchmark.

### Compressors and error ladders

SZ3 was evaluated through `pysz` 1.0.3 in absolute `INTERP_LORENZO` mode, ZFP through `zfpy` 1.0.1 in fixed-accuracy mode, and SPERR through `hdf5plugin` 7.0.0 in absolute single-chunk mode. Compression ratio is reported relative to the float64 field payload. The base ladder spans relative requested tolerances from 10^-5 to 10^-1, converted to absolute bounds using each field's peak-to-peak range. Runs are early-stopped after the re-derived Bader error reaches 0.05 e. A tight ladder at 10^-7, 3×10^-7, 10^-6 and 3×10^-6 resolves the strict-accuracy frontier for A.1-eligible systems. `realized_Linf` is measured directly for every successful reconstruction.

### Bader analysis and fidelity metrics

Primary Bader partitions were computed with `baderkit` 0.10.2 using `method="ongrid"`. The primary downstream error is the maximum absolute per-atom charge difference after re-deriving the Bader partition from each reconstructed density. A fixed-domain diagnostic integrates reconstructed densities over the original basins. `n_voxels_reassigned` and `frac_voxels_reassigned` record changes in Bader labels between reference and reconstructed partitions.

### Protocol A.1 stability qualification

For material \(i\),

\[
\epsilon_i=\|\mathrm{float32}(\rho_i)-\rho_i\|_\infty.
\]

Protocol A.1 generates five additive uniform perturbations \(U_s(-\epsilon_i,+\epsilon_i)\) using preregistered seeds {20260905, 1, 2, 3, 4}. The Bader partition is re-derived for every perturbation. The material floor is the maximum atom-wise Bader-charge deviation over the five seeds. Scientific contracts are \(\tau\in\{10^{-4},10^{-3},10^{-2}\}\) e. A material is eligible when its A.1 floor is below \(\tau\); otherwise it is reported as `NON_EVALUABLE_BADER_UNSTABLE` and receives no codec pass/fail at that threshold.

Protocol A, which used a deterministic float32 round trip, remains archived unchanged. Protocol A.1 changed the perturbation probe and seed aggregation while retaining the threshold set, exclusion semantics and reporting rules.

### Realized-L∞ matching and material-level inference

Codec operating points are matched within material using \(\log_{10}(\mathrm{realized}\ L_\infty)\). The primary analysis uses a 0.10-decade caliper, with sensitivity analyses at 0.05, 0.20 and 0.30 decades. Ratios are summarized first within material and then across materials; uncertainty is estimated by material-level bootstrap resampling. A conservative failure-free sensitivity removes an entire material if any codec has a registered downstream failure in the specified operating range. Separate material-fixed-effect models include centered \(\log_{10}L_\infty\), codec indicators and, for mechanism consistency, the reassigned-voxel fraction. Changes in codec coefficients after adding reassignment are interpreted as attenuation evidence, not causal mediation.

### Certified compression ratio

For each eligible material, codec and chemical contract, the certified compression ratio (CCR) is the maximum compression ratio among retained rows satisfying `Bader_error_resolved_e < tau`. Non-evaluable systems are not counted as codec failures. The external aggregator reports medians, quantiles, certification fractions and deterministic material-bootstrap confidence intervals.

### Frozen external confirmation

The external scientific implementation was frozen at commit `893f931b3045b0b628329db81999c2f439d4e830`. Corpus-scale aggregation uses the byte-frozen `validation/aggregate_formal_external.py`; the 63-system primary cohort is generated by the byte-frozen `validation/build_confirmatory_external.py` and the pre-frozen split in `validation/external_rate_fidelity_split.json`. The final gate requires exact 65-system descriptive coverage, exact 63-system confirmatory coverage, 63 material-level completions, zero pointwise-bound violations and exact A.1 eligibility counts of 16/42/57.

The final Cl-containing AFLOW record retained the exact frozen CHGCAR (2,437,424 bytes; SHA-256 `eb5872d5229ab8e3f7360c0add9e8619cf357bff1e11a7e494b68f2d5c36e983`). Because AFLOW's property endpoint returned HTTP 500, metadata were read from `aflowlib.json` from the same entry and cross-checked against `OUTCAR.static.xz` and the CHGCAR atom-count line. This was a transport/provenance recovery only; codec, Bader, A.1, tolerance, early-stop and certification semantics were unchanged.

### Independent Bader implementation and spatial controls

The independent robustness supplement uses 12 development materials selected by A.1 stability-floor stratum, plus one separately labeled sentinel. Henkelman Bader 1.05 was compiled from official source and evaluated in on-grid and near-grid modes. A header-format adapter changed only geometry-header parsing and was verified against the unmodified binary before production. The same original, codec-perturbed, noise-perturbed and spatial-control densities were analyzed by BaderKit and Henkelman.

Spatial controls preserve the source codec error-value multiset while changing its organization. A global permutation destroys spatial autocorrelation; a density-stratified permutation rearranges errors within density strata and is the cleaner physical control; a periodic translation preserves autocorrelation while changing alignment with the reference field. These controls test sensitivity to error organization but do not establish a unique causal boundary-local statistic.

## Data and code availability

The current repository state is `stloendays/QoI`. The development master table is `benchmark/master_benchmark_full.csv`. Matched-realized-L∞ outputs are in `analysis/matched_realized_linf_v1/`. The final external audit is released under `validation/final_external_confirmatory63_20260908/`, including the 65-system descriptive aggregate, 63-system confirmatory aggregate and Cl recovery provenance. The independent implementation and spatial-control supplement is in `mechanism/independent_bader_20260908/`. Protocol A.1 and the archived Protocol A are retained under `protocol/` and `stability/`. Failure records are explicit and are not silently converted into successful rows.

## References

1. Diffenderfer, J., Fox, A. L., Hittinger, J. A. F., Sanders, G. & Lindstrom, P. G. Error Analysis of ZFP Compression for Floating-Point Data. *SIAM J. Sci. Comput.* **41**, A1867–A1898 (2019). DOI: 10.1137/18M1168832.
2. Liang, X., Zhao, K., Di, S., Li, S., Underwood, R., Gok, A. M., Tian, J., Deng, J., Calhoun, J. C., Tao, D., Chen, Z. & Cappello, F. SZ3: A Modular Framework for Composing Prediction-Based Error-Bounded Lossy Compressors. *IEEE Trans. Big Data* **9**, 485–498 (2023). DOI: 10.1109/TBDATA.2022.3201176.
3. Li, S., Lindstrom, P. & Clyne, J. Lossy Scientific Data Compression With SPERR. In *2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)*, 1007–1017 (IEEE, 2023). DOI: 10.1109/IPDPS54959.2023.00104.
4. Jiao, P., Di, S., Guo, H., Zhao, K., Tian, J., Tao, D., Liang, X. & Cappello, F. Toward Quantity-of-Interest Preserving Lossy Compression for Scientific Data. *Proc. VLDB Endow.* **16**, 697–710 (2022/2023). DOI: 10.14778/3574245.3574255.
5. Yan, L., Liang, X., Guo, H. & Wang, B. TopoSZ: Preserving Topology in Error-Bounded Lossy Compression. *IEEE Trans. Vis. Comput. Graph.* **30**, 1302–1312 (2024). DOI: 10.1109/TVCG.2023.3326920.
6. Gorski, N., Liang, X., Guo, H., Yan, L. & Wang, B. A General Framework for Augmenting Lossy Compressors With Topological Guarantees. *IEEE Trans. Vis. Comput. Graph.* **31**, 3693–3705 (2025). DOI: 10.1109/TVCG.2025.3567054.
7. Li, Y., Xia, M., Liang, X., Wang, B. & Guo, H. Preserving Discrete Morse–Smale Complexes in Error-Bounded Lossy Compression. *IEEE Trans. Vis. Comput. Graph.* **32**, 6593–6609 (2026). DOI: 10.1109/TVCG.2026.3684385.
8. Li, Y. et al. pMSz: A Distributed Parallel Algorithm for Correcting Morse-Smale Segmentations for Lossy Compression. *IPDPS* (2026).
9. Fallin, A., Gorski, N., Agarwal, T., Wang, B., Gopalakrishnan, G. & Burtscher, M. Fast Topology-Aware Lossy Data Compression with Full Preservation of Critical Points and Local Order. *IEEE Trans. Big Data* (2026). DOI: 10.1109/TBDATA.2026.3705355.
10. Liu, Y. et al. TOPIQ: Statistical Error Propagation for Quantity-of-Interest Prediction under Lossy Compression. *SC 2026*, accepted; arXiv:2608.26912 (2026).
11. Liu, G. et al. FZ-VIS: A Visual Analytics Framework for Quantities-of-Interest-Aware Scientific Lossy Compression. *IEEE VIS / IEEE TVCG*, accepted (2026); arXiv:2608.08386.
12. Bader, R. F. W. *Atoms in Molecules: A Quantum Theory*. Oxford University Press (1990).
13. Henkelman, G., Arnaldsson, A. & Jónsson, H. A fast and robust algorithm for Bader decomposition of charge density. *Comput. Mater. Sci.* **36**, 354–360 (2006). DOI: 10.1016/j.commatsci.2005.04.010.
14. Brehm, M. & Thomas, M. An Efficient Lossless Compression Algorithm for Trajectories of Atom Positions and Volumetric Data. *J. Chem. Inf. Model.* **58**, 2092–2107 (2018). DOI: 10.1021/acs.jcim.8b00501.
