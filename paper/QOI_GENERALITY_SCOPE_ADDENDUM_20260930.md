# Author-authorized scope addendum — QoI generality and qualification robustness (2026-09-30)

## Authorization and purpose

The author explicitly reopened the frozen 2026-09-27 manuscript scope to evaluate the four pre-declared extension work packages in `analysis/extensions_20260928/PROTOCOL.md`. The evidence packages WP-A through WP-D are now integrated on the manuscript-integration branch. This addendum defines what is promoted into the reader-facing scientific story and what remains supporting evidence.

## Canonical extension decision

### WP-B — promote to the main scientific story

Reader-facing name: **grid-local density extrema**, not “density critical points”.

The implementation identifies discrete grid voxels that are strict local maxima or minima relative to their 26 neighbours. It does not locate continuous QTAIM critical points and must not be described as doing so.

The decisive prospective result uses the same five-seed qualification logic and 59 fresh iid perturbations per development material. At the strict maximum-set qualification endpoint, 118/254 materials are eligible. Among 6,962 fresh trials on eligible materials, 0 change the maximum count, whereas 6,444/8,024 fresh trials on screen-rejected materials do so. The secondary maximum-set endpoint changes in 3/6,962 eligible versus 7,509/8,024 rejected trials.

Cross-QoI transfer is weak: Cohen's kappa between Bader eligibility at 1e-3 e and grid-local-extrema eligibility is 0.1337, and the Spearman correlation between the corresponding stability floors is 0.1389. The scientific interpretation is therefore:

> **The qualification principle generalizes across topology-sensitive QoIs, but the evaluability boundary is QoI-specific.**

This result may enter the main text because it changes the generality claim of the paper.

### WP-C — retain as strong robustness evidence in SI and Discussion

Codec-shaped perturbations do not improve the qualification contract relative to the codec-independent iid family. The iid family is conservative on aggregate for ZFP and SPERR and statistically indistinguishable from the codec-shaped family for SZ3 under the pre-declared rule. At the primary 1e-3 e endpoint, agreement between iid and codec-shaped eligibility is 0.902 for ZFP and 0.937 for SZ3 and SPERR.

Among the 143 iid-admitted materials, the codec-shaped floor does not improve prospective prediction of fresh iid exceedance risk; it is worse for ZFP and indistinguishable for SZ3/SPERR. The low-G Fourier descriptor that explains the Hartree codec effect does not provide a common explanation for codec-shaped versus iid Bader stability floors.

Reader-facing conclusion: the codec-independent iid QSQ probe remains the primary qualification procedure; perturbation-family robustness is supportive, not a new main endpoint.

### WP-A — Discussion-only interpretive evidence

Continuous risk models based on log10(f_m/tau) predict prospective exceedance risk more accurately than the binary gate, but the pre-declared low-risk contract does not improve operational coverage. At tau=1e-3 e and p*=2%, the cross-validated isotonic contract admits 115/254 materials (45.3%) versus 143/254 (56.3%) for the gate.

This analysis must not become a separate Results or Methods line, headline statistic, abstract claim, or main figure. If retained in the submitted manuscript, it belongs only in Discussion, with numerical details in the SI. Its role is explanatory: the continuous floor contains graded risk information, but risk rises sharply as f_m approaches tau, so a stringent probabilistic cutoff moves inside the binary eligibility boundary and necessarily sacrifices coverage. The binary QSQ rule is therefore retained as a transparent qualification boundary rather than presented as a calibrated per-material risk guarantee.

### WP-D — Discussion-only limitation and mechanism evidence

Cheap reference-density descriptors show interpretable associations with the measured Bader QSQ floor, especially basin-boundary gap statistics, but do not predict the floor reliably out of domain. A development-trained ridge model gives external held-out R2=0.134 with RMSE=1.208 decades, failing the pre-declared replacement criterion.

This analysis must not become a separate Results or Methods line, headline statistic, abstract claim, or main figure. If retained in the submitted manuscript, it belongs only in Discussion, with numerical details in the SI. Its role is explanatory: local boundary-gap descriptors capture one physically plausible source of basin fragility, but Bader stability reflects a nonlinear, collective response of density ordering, basin topology, grid semantics and material class. Those relationships shift between development and external domains, so cheap proxies can reveal mechanism without replacing direct measurement.

## Revised manuscript-level thesis

**Scientific compression should be scored only after the reference QoI is qualified at the requested tolerance; qualification itself is QoI-specific, while codec performance further depends on the downstream operator and the spatial/frequency structure of reconstruction error.**

## Figure policy

The existing eight-figure main-text architecture remains unchanged for this integration. WP-B is introduced as a compact main-text generality result supported by SI tables rather than by adding a ninth main figure. WP-C remains SI/Discussion robustness evidence. WP-A and WP-D are Discussion-only interpretive evidence, with full numerical details confined to the SI/repository; they must not define new Results, Methods, abstract claims or main figures. A later figure redesign may promote the WP-B result only if it replaces, rather than simply appends to, an existing panel.

## Claim boundaries

Do not claim:
- that discrete grid-local extrema are continuous QTAIM critical points;
- that QSQ eligibility transfers from one QoI to another;
- that the five-seed probe is a worst-case stability certificate;
- that codec-shaped probes are uniformly more realistic or more predictive;
- that reference-density descriptors can replace direct QSQ measurement;
- that the Hartree Fourier mechanism explains Bader instability.

This addendum re-freezes the scientific scope after integration of the pre-declared WP-A–WP-D extension package.
