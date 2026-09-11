# P3B scope decision

Status: **DEFERRED_NO_NEW_DFT**

After completing P2 prospective validation and P3A implementation-transfer validation, the current submission scope does not include new electronic-structure density-grid recomputations.

This is a scope decision, not a scientific pass/fail result. Existing P3B provenance-audit materials are retained unchanged for future work or a reviewer-requested targeted calculation.

## Consequence for claims

The paper may claim that the QSQ stability measure is operationally defined under the declared density representation and downstream-analysis contract, is prospectively predictive on fresh perturbations, and transfers strongly across independently implemented on-grid Bader analyses in the tested 24-system panel.

The paper must **not** claim that:

- the measured QSQ floor is a grid-independent material constant;
- Bader numerical instability has been proven independent of the underlying electronic-structure density grid;
- the present study establishes a unique physical Bader reference;
- interpolation or resampling constitutes electronic-structure grid convergence.

P3B can be reconsidered only as explicitly labeled future work or a targeted response to review. No P3B result is required for the current P4 chemical-decision utility experiment, whose escalation step is restricted to an independent on-grid Bader implementation and does not invoke new DFT.
