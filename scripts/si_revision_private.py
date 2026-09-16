from __future__ import annotations
import re, sys, hashlib
from pathlib import Path

src=Path(sys.argv[1]); out=Path(sys.argv[2])
t=src.read_text(encoding='utf-8')

t=re.sub(r'\n?<!--\s*P4_CONTRACT_BOUNDARY_SI\s*-->\n?', '\n', t)
t=re.sub(r'\n# Current completion assessment\n.*?(?=\n## Supplementary Note \| Outcome-blind chemical-decision boundary case study|\Z)', '\n', t, flags=re.S)

t=t.replace('The SI uses frozen data assets already versioned in the repository. No supplementary result should be transcribed manually when a machine-readable source exists.','The SI uses frozen data assets maintained in the private version-controlled research archive during manuscript development. Numerical values are regenerated from machine-readable sources rather than transcribed from prose summaries; a public archival release of the derived data and analysis code required for reproduction will accompany publication.')
t=t.replace('**319 stability-tested systems**: QSQ stability-floor and eligibility summaries.', '**319 stability-tested systems**: QSQ response-scale and eligibility summaries.')
t=t.replace('Five pre-registered uniform perturbations', 'Five pre-specified uniform perturbations, frozen before execution,')
t=t.replace('The material-specific QSQ stability floor is', 'The material-specific operational QSQ response scale is')
t=t.replace('the per-material log10 floor span', 'the per-material log10 response-scale span')
t=t.replace('the floor changed by a median', 'the response scale changed by a median')
t=t.replace('the reported floor is qualification-defined', 'the reported response scale is qualification-defined')
t=t.replace('Error relative to the independent stability floor', 'Error relative to the operational QSQ response scale')
t=t.replace('The strictest certified regime is therefore floor-scale.', 'The strictest certified regime is therefore on the same numerical scale as the QSQ response.')
t=t.replace('the QSQ floor.', 'the QSQ response scale.')
t=t.replace('QSQ-floor ratios', 'QSQ-scale ratios')
t=t.replace('QSQ floor', 'QSQ response scale')
t=t.replace('QSQ-floor', 'QSQ-scale')
t=t.replace('stability-floor distribution', 'response-scale distribution')
t=t.replace('stability floor', 'response scale')
t=t.replace('Historical repository identifiers such as `Protocol A`, `Protocol A.1`, and filenames containing `_A1` are retained only to preserve the frozen development record and machine-readable provenance; they are not the preferred scientific names of the qualification method.','Historical protocol identifiers and `_A1`-suffixed filenames are retained only inside machine-readable provenance paths; QSQ is the reader-facing scientific name of the qualification procedure.')

needle='\n---\n\n## Supplementary Note 3 — Sensitivity analyses for eligibility and certification\n'
p2='''\n---\n\n## Supplementary Note 3 — Prospective validation of the frozen QSQ gate\n\nThe five-seed QSQ gate was frozen before a prospective perturbation challenge. Each of the **254 development materials** was then evaluated under **59 fresh iid-uniform perturbations**, using deterministic labels 10000–10058 and the same material-specific float32-scale amplitude without retuning. All **14,986/14,986** planned trials produced valid Bader responses, with no unresolved cells. The same 59 response vectors are evaluated against all three chemical thresholds and therefore should not be treated as three independent experiments.\n\nAt the primary $10^{-3}\\,e$ endpoint, QSQ admitted **143/254 materials (56.3%)**. Fresh threshold exceedances occurred in **135/8,437 eligible trials (1.600%)** versus **5,326/6,549 screen-rejected trials (81.325%)**, a rejected-to-eligible risk ratio of **50.83-fold**. Material-cluster bootstrap 95% confidence intervals were **0.782–2.596%** and **75.981–86.257%**, respectively. At least one fresh exceedance occurred in **20/143** eligible materials versus **110/111** screen-rejected materials.\n\nThe direction is consistent at the two pre-specified secondary thresholds: at $10^{-4}\\,e$, exceedance rates are **4.016%** for eligible versus **86.938%** for screen-rejected trials (risk ratio **21.65-fold**); at $10^{-2}\\,e$, they are **0.148%** versus **79.593%** (risk ratio **537.69-fold**). For a material–threshold cell with zero exceedances among 59 iid draws, the one-sided 95% exact Bernoulli upper bound on the per-draw exceedance probability is approximately **4.95%**.\n\nThese results support prospective risk stratification under the declared iid-uniform perturbation model. They do not establish a worst-case robustness guarantee, simultaneous confidence across all materials, transfer to arbitrary new material populations, or equivalence to physical uncertainty. Machine-readable sources are `analysis/research_upgrade/p2_fresh_probe_discrimination.csv` and `validation/qsq_prospective/p2_fresh_probes/`.\n'''
if needle not in t: raise SystemExit('P2 insertion point not found')
t=t.replace(needle,p2+'\n---\n\n## Supplementary Note 4 — Sensitivity analyses for eligibility and certification\n',1)

renames={
'## Supplementary Note 4 — Extended operator controls':'## Supplementary Note 5 — Extended operator controls',
'## Supplementary Note 5 — Binary-to-three-state reclassification':'## Supplementary Note 6 — Equal-search control and historical binary sensitivity audit',
'## Supplementary Note 6 — Extended Bader mechanism and cross-implementation robustness':'## Supplementary Note 7 — Extended Bader mechanism and implementation-transfer robustness',
'## Supplementary Note 7 — Realized-distortion matching diagnostics':'## Supplementary Note 8 — Realized-distortion matching diagnostics',
'## Supplementary Note 8 — Stability-qualified rate–fidelity tables':'## Supplementary Note 9 — Stability-qualified rate–fidelity tables',
'## Supplementary Note 9 — External confirmation':'## Supplementary Note 10 — External confirmation',
'## Supplementary Note 10 — Failure taxonomy and negative results':'## Supplementary Note 11 — Failure taxonomy and negative results',
'## Supplementary Note | Outcome-blind chemical-decision boundary case study':'## Supplementary Note 12 — Outcome-blind chemical-decision boundary case study'}
for a,b in renames.items():
    if a not in t: raise SystemExit(f'missing note heading: {a}')
    t=t.replace(a,b,1)

p1_anchor='''The primary Figure 3 audit uses one material–codec decision per Bader threshold, giving **254 materials × 3 codecs = 762 decisions per threshold**. The pooled results are frozen in `analysis/certifiability_reclassification_pooled_20260911.csv`; codec-resolved counts are in `analysis/certifiability_reclassification_by_codec_20260911.csv`.\n'''
p1_new='''The equal-search control removes unequal ladder coverage as an explanation for the QSQ separation. Completing the same tight search ladder for every material–codec pair added **1,332/1,332 successful reconstructions**. At the primary $10^{-3}\\,e$ contract, failure to find any numerical pass occurs for **3.3%** of QSQ-eligible versus **66.4%** of screen-rejected material–codec pairs, a **20.34-fold** ratio. The additional search yields **214** extra numerical passes at $10^{-3}\\,e$, all in QSQ-eligible pairs. This supports persistence of the association after equalizing search opportunity; it does not assign causality to a codec. Source: `analysis/research_upgrade/P1_COMMON_TIGHT_REPORT.md`.\n\nThe historical binary-to-three-state audit is retained as a sensitivity analysis rather than the headline evidence. It uses one material–codec decision per Bader threshold, giving **254 materials × 3 codecs = 762 decisions per threshold**. The pooled results are frozen in `analysis/certifiability_reclassification_pooled_20260911.csv`; codec-resolved counts are in `analysis/certifiability_reclassification_by_codec_20260911.csv`.\n'''
if p1_anchor not in t: raise SystemExit('P1 anchor not found')
t=t.replace(p1_anchor,p1_new,1)
t=t.replace('At \\(10^{-4}\\,e\\), a naive binary benchmark reports', 'In the historical, ladder-sensitive audit, at \\(10^{-4}\\,e\\), a naive binary benchmark reports')

p3_anchor='''A separate independent-Bader study in `mechanism/independent_bader_20260908/` provides an implementation-robustness check. It contains **1,560/1,560 expected outcome rows** across a stratified panel and three solver modes. Henkelman on-grid reproduces BaderKit on-grid codec response with a median ratio of **1.00** (IQR approximately 0.92–1.005), aside from systems whose unperturbed basin sets differ. Codec ordering at relative tolerance \\(10^{-4}\\) is preserved across BaderKit on-grid, Henkelman on-grid and Henkelman near-grid. These results should remain supplementary because they validate robustness rather than define the central benchmark claim.\n'''
p3_new='''An earlier independent-Bader mechanism study in `mechanism/independent_bader_20260908/` provides a secondary robustness check. It contains **1,560/1,560 expected outcome rows** across a stratified panel and three solver modes. Henkelman on-grid reproduces BaderKit on-grid codec response with a median ratio of **1.00** (IQR approximately 0.92–1.005), aside from systems whose unperturbed basin sets differ. Codec ordering at relative tolerance $10^{-4}$ is preserved across BaderKit on-grid, Henkelman on-grid and Henkelman near-grid.\n\nThe main implementation-transfer result uses a separately frozen, deterministically stratified **24-system** panel spanning bulk/slab systems and four QSQ response-scale bands. The first execution blocked **360** cells before solver evaluation because a provenance check compared source-rederived amplitudes with decimal-serialized historical values at binary-ULP precision; the blocked cells were classified before an engineering-only retry and no scientific setting was changed. The retry completed **360/360** cells, with **72/72** relevant solver–material summaries complete. Henkelman on-grid reproduced the frozen QSQ eligibility classification for **24/24 systems** at each of $10^{-4}$, $10^{-3}$ and $10^{-2}\\,e$ (Cohen's $\\kappa=1.000$ at every threshold) and preserved the QSQ response-scale ordering (Spearman $\\rho=0.995$). Henkelman near-grid agreement was **82.6%**, **83.3%** and **95.8%** at the three thresholds, with $\\rho=0.754$.\n\nThe transfer result therefore supports implementation robustness under matched on-grid analysis semantics while also demonstrating that the numerical analysis algorithm is part of the measurement contract. It does not establish electronic-structure grid convergence or a unique physical Bader reference. The resolved summary is in Supplementary Table S11 and `validation/qsq_prospective/p3a_implementation_transfer_resolved/P3A_IMPLEMENTATION_TRANSFER_RESOLVED_REPORT.md`.\n'''
if p3_anchor not in t: raise SystemExit('P3A anchor not found')
t=t.replace(p3_anchor,p3_new,1)

p4_start=t.find('## Supplementary Note 12 — Outcome-blind chemical-decision boundary case study')
if p4_start < 0: raise SystemExit('P4 section missing')
p4=t[p4_start:].strip(); t=t[:p4_start].rstrip()+'\n'
p4=p4.replace('Full pair-level reference values and policy accounting are provided in Supplementary Tables S15-S16.','Full pair-level reference values and policy accounting are provided in Supplementary Tables S15–S16.')
p4=p4.replace('P3B new-DFT grid convergence was not used; the source reference is a BaderKit/Henkelman on-grid consensus under the declared density representation.','P3B new-DFT grid convergence was not used; the source reference is a BaderKit/Henkelman on-grid consensus under the declared density representation. A targeted independent-solver audit would require **48 Henkelman calls / 397.2 s** under the QSQ policy versus **108 calls / 733.3 s** for a blanket audit; this is an audit-cost reduction, not a correctness gain. The five-pair case study is a task-boundary demonstration rather than a prevalence estimate.')

idx=t.find('# Proposed Supplementary Tables')
if idx < 0: raise SystemExit('table heading missing')
t=t[:idx].rstrip()+'\n\n---\n\n'+p4+'\n\n---\n\n'+t[idx:]

t=t.replace('# Proposed Supplementary Tables','# Supplementary table inventory')
t=t.replace('# Proposed Supplementary Figures','# Supplementary figure inventory')
t=t.replace('All final supplementary figures should be generated from R sources and exported as PNG/PDF/SVG, following the same reproducibility standard as Figures 1–7.','Supplementary figures are generated from versioned R sources and frozen data assets, with publication outputs exported as PNG/PDF/SVG from the same code path.')
t=t.replace('| **Table S14** | Failure taxonomy and negative algorithm results | `failure_registry.csv`; `paper/CLAIM_EVIDENCE_MATRIX.md` | **READY, needs compact aggregation** |','| **Table S14** | Failure taxonomy and negative algorithm results | `failure_registry.csv`; `paper/CLAIM_EVIDENCE_MATRIX.md` | **READY, needs compact aggregation** |\n| **Table S15** | Outcome-blind P4 pair-level source-reference values, eligibility and qualitative decision outcomes | `paper/SUPPLEMENTARY_TABLES_S15_S16_20260911.md`; `validation/p4_*` | **BUILT** |\n| **Table S16** | P4 policy-level accounting, retained decisions and independent-solver audit cost | `paper/SUPPLEMENTARY_TABLES_S15_S16_20260911.md`; P4 frozen audit outputs | **BUILT** |')
t=t.replace('Cross-implementation Bader robustness + resolved 24-system QSQ classification transfer','Cross-implementation Bader robustness and resolved 24-system QSQ classification transfer')
t=t.replace('Certified Bader error relative to QSQ response scale','Certified Bader error relative to the operational QSQ response scale')
t=t.replace('Archived float32-probe vs QSQ response-scale distribution and threshold eligibility','Archived float32 probe versus operational QSQ response-scale distribution and threshold eligibility')
t=t.replace('Tight-regime Bader error/QSQ-scale ratios and tight-ladder diagnostic','Tight-regime Bader error/QSQ-response-scale ratios and tight-ladder diagnostic')
t=t.replace('Supplementary figures should be regenerated in R rather than using legacy exploratory plots as final publication graphics.','Publication supplementary figures must be generated from the locked R sources rather than legacy exploratory plots.')
needle_b='8. Negative algorithm results belong in the SI to show what was tested and falsified; they should not compete with the benchmark-validity narrative.'
t=t.replace(needle_b,needle_b+'\n9. The P2 prospective result is a risk-stratification result under the declared iid-uniform perturbation model, not a worst-case, simultaneous, universal-material or physical-uncertainty guarantee.\n10. P4 demonstrates endpoint dependence: zero sign errors in the five frozen pairs do not license ignoring QSQ for the stricter absolute-charge contract.')
t=t.replace('The final submission should preserve these labels explicitly. A reader should never be forced to infer why a reported denominator is 254, 319, 65 or 63.','These labels are preserved explicitly so that the denominators 254, 319, 65 and 63 are never conflated.')

t=re.sub(r'\n{4,}','\n\n\n',t).strip()+'\n'
out.write_text(t,encoding='utf-8')
print(hashlib.sha256(t.encode()).hexdigest())
