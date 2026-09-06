# Related-work delta — 2026-09-06

This note records important literature found after manuscript v0.3.1 scientific freeze. It should be incorporated during the final bibliography/editorial pass without reopening the frozen benchmark or Protocol A.1.

## High-priority adjacent 2026 paper: MARGR

Junyi Gong, Zheng Zhao and Ben Zhong Tang, **Bridging Machine Learning and Electron Density Theory with Adaptive Real-Space Integration**, *Journal of Chemical Theory and Computation* (published online 29 August 2026). DOI: `10.1021/acs.jctc.6c01124`.

### Why it is close

The paper explicitly frames a **fidelity gap in downstream tasks** for machine-learned electron densities and attributes part of that gap to real-space integration error and imbalanced uniform grids. It proposes an adaptive real-space integration/refinement framework and benchmarks molecular-property accuracy.

This makes it directly relevant to any claim that electron-density fidelity should be judged only at the raw-grid level.

### Why it does not subsume the QoI manuscript

The present manuscript studies a different perturbation source and a different downstream failure mechanism:

1. **Source of approximation**
   - MARGR: machine-learned electron densities and grid integration/refinement.
   - QoI manuscript: error-bounded lossy compression of existing DFT density fields.

2. **Downstream domain**
   - MARGR: adaptive real-space integration for molecular properties.
   - QoI manuscript: Bader charges whose integration domains are themselves re-derived from the perturbed field.

3. **Mechanism isolated here**
   - explicit decomposition `Delta Q_total = Delta Q_integrand + Delta Q_domain`;
   - representative-set domain-migration dominance;
   - full-benchmark basin-reassignment attenuation after controlling realized L-infinity.

4. **Numerical-contract layer unique to the present evaluation**
   - Protocol-A.1 QoI resolvability qualification before codec pass/fail;
   - validated perturbation probe with seed and amplitude sensitivity;
   - NON_EVALUABLE semantics separated from codec failure.

5. **Compression-specific statistical separation**
   - nominal error-budget utilization versus realized field-error magnitude;
   - matched-realized-L-infinity codec comparisons;
   - complete-case downstream-failure sensitivity.

### Recommended manuscript insertion

Add one sentence to the Introduction after the general QoI/topology literature:

> Related work on machine-learned electron densities has independently identified a downstream-fidelity gap arising from real-space integration and grid representation, motivating adaptive integration rather than treating density-grid error alone as sufficient evidence of property accuracy [MARGR].

Then sharpen the transition:

> Our setting adds a distinct complication: the integration domains are not fixed numerical quadrature regions but are themselves derived from the reconstructed field, so compression can alter both the integrand and the domain on which the QoI is defined.

### Recommended Discussion comparison

> MARGR addresses downstream integration fidelity by adaptively refining where an approximate electron density is integrated. Our results expose a complementary problem for partition-defined observables: even when pointwise reconstruction error is bounded, the field can change the partition itself. For Bader charge, this domain-migration term—not global electron-count error—accounts for the dominant measured failure mode in the representative mechanism set and for the codec-associated residual across the benchmark.

## Impact on novelty positioning

This paper makes the following generic novelty formulations even less defensible:

- “first work to identify a fidelity gap between electron density and downstream chemistry”;
- “first work to show electron-density approximation can cause integration errors”;
- “first work to argue grid-level accuracy is insufficient for downstream properties.”

The manuscript should instead continue to own the narrower and stronger contribution:

> a stability-qualified fidelity contract for lossy-compressed electron densities when the downstream chemical observable is defined over field-derived integration domains.

## Impact on venue selection

The appearance of a closely adjacent electron-density fidelity methodology paper in JCTC in August 2026 is positive evidence that the JCTC readership/editorial scope recognizes downstream electron-density fidelity as a current methodological problem. It also raises the standard for the introduction: the present submission should explicitly distinguish **adaptive quadrature/integration error** from **compression-induced field-derived domain migration** rather than presenting the downstream-fidelity premise as new.

## Bibliography status

Verified metadata:

- Authors: Junyi Gong; Zheng Zhao; Ben Zhong Tang.
- Journal: *Journal of Chemical Theory and Computation*.
- Published online: 29 August 2026.
- DOI: `10.1021/acs.jctc.6c01124`.

Add the final volume/issue/page information from ACS metadata at submission time if assigned after online publication.
