# Scope v6 — storyline draft for a broader paper (owner's decision)

Status: proposal. All numbers are now measured (S0–S3). Nothing here touches
`paper/MANUSCRIPT.md`.

## The shift in one sentence

- **rev5:** the downstream operator qualifies, predicts and shapes certified compression of electronic
  **densities**.
- **v6:** the downstream operator qualifies, predicts and shapes certified compression of **the stored
  electronic-structure object**: every field the archive serves, for every class of analysis run on it.

## What the extension adds, and the evidence behind each piece

| addition | why reviewers care | evidence | status |
|---|---|---|---|
| Magnetization block as a second stored field; per-atom moments as a contract | every MP CHGCAR carries it (300/300); it is 52% of the served bytes; rev5 is silent about it | S0, S0b, S1 | measured |
| Archive estimate for the whole served object (rho + m, plus the atom map) | removes the like-for-like objection to "8.50 TB shrinks 356-fold": whole object 4.36× (Bader) and 232× (Hartree, with the map) | S2 | measured |
| Moment contract qualifies almost everywhere (16/16 engineering and 300/300 archive objects at 1e-2 mu_B) | QSQ generalizes to a second physical field without retuning | S1, S2 | measured |
| Charge and moment contracts compose when m is certified on the decoded partition (60/62, byte cost 1.00×) | a general rule: certify each quantity in the frame the user computes it in | S3 v2 | measured |
| Contract-budgeted partition relaxation with a proved per-atom bound | bridges exact topology preservation (B3) and the Bader tolerance; validated on the compiled binary | B4 | measured, byte effect small: SI sentence only |
| Finite-panel ceiling as a design rule; transfer to turbulence | answers "why five probes?" and shows QSQ is not electronic-structure-specific | SI 1.5 + turbulence n19 | measured, excluded by the 10-03 decision |

## A possible operator-class map (one panel, or an SI table)

| operator class | example QoI | design pattern | where |
|---|---|---|---|
| diagonal linear (Fourier) | Hartree potential / field, smoothing | spectral allocation (closed-form law) | main |
| linear on a fixed partition | Bader charges, **magnetic moments** | constraint projection / certified pointwise | main / **new** |
| the partition itself | Henkelman labels | exact correction, or a stored label map | SI 5 |
| partition under a tolerance | Bader with tau_B | budgeted relaxation (proved bound) | **new SI** |
| derivative / threshold on another field | vortex mask, enstrophy | QSQ only | **new SI** (if accepted) |

## Budget

The main text is at 4,992 / 5,000 words and 10 / 10 display items. A v6 needs about 120–180 words for the
spin channel and the whole-object archive, plus one panel. Candidate cuts, for the owner to judge:

- the deployment paragraph shares Table 2 with Methods detail;
- the gain-ladder paragraph overlaps Fig. 6.

## Minimum change, if the scope stays at rev5

Apply `OPTION1_archive_wording_draft.md`: archive claims quoted against the charge-density block, plus one
Methods sentence. This removes the like-for-like weakness even without the extension.
