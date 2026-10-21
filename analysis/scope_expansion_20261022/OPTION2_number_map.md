# Option 2 — sentence-by-sentence number map (whole served object)

Status: for the owner. `paper/MANUSCRIPT.md` is unchanged.

- **Numbers.** From `results/whole_object_estimates/TABLE.md`, regenerated with
  `whole_object_estimates.py` from committed per-object tables. Bootstrap seeds are the protocol seeds.
- **m policy.** Bader rows and the non-1e-6 Hartree rows carry the reference atom map (conservative). The
  Hartree-law 1e-6 row is map-free (decoded-frame m, S2b).

| manuscript place (rev5) | current text | whole-object replacement |
|---|---|---|
| Abstract | "shrink the 8.50 TB … archive 4.4-fold for Bader charges at 10⁻³ e" | **4.3-fold** (4.34 [3.61, 5.37]) |
| Abstract | "356-fold for the Hartree potential at 10⁻⁶ (pointwise: 35-fold)" | **316-fold** [290, 350] (pointwise: **33-fold**) |
| Results, archive (Bader) | "shrinks 4.37-fold (95% CI 3.64–5.46), … saving of 6.55 TB" | 4.34-fold (3.61–5.37), 6.54 TB |
| Results, archive (Bader) | "lossless binary storage accounts for 2.00-fold … certified compression adds 2.66-fold (2.21–3.27)" | lossless binary: **0.99-fold**; certified compression over lossless binary: **5.35-fold (4.49–6.58)** |
| Results, archive (Bader) | "At 10⁻⁴ and 10⁻² e the archive shrinks 2.36- and 8.99-fold" | 2.35- and 8.88-fold |
| Results, archive (Hartree) | "356-fold (95% CI 327–395), from 8.50 TB to an estimated 24 GB, against 35.0-fold (32.7–37.7)" | 316-fold (290–350), to an estimated 27 GB, against 33.3-fold (31.2–35.7) |
| Results, archive (Hartree) | "the law's archive is 10.2-fold smaller (9.35–11.2)" | 9.5-fold (8.79–10.4) |
| Results, archive (Hartree) | "The factors are 1,751 and 168 at 10⁻⁴" | law **1,036** (hybrid policy: atom map only for the 10/300 objects that need it; S2c). The pointwise figure is available only under the always-map policy, 134. See note 1 |
| Results, archive (Hartree) | "and 7.8 and 6.1 at 10⁻⁸" | 7.7 and 6.0 |
| Discussion | "the law's Hartree-certified store is 356-fold smaller than the public one" | 316-fold, magnetization included |
| Methods, archive | — | one sentence on the magnetization block and the moment contract, plus a pointer to the new SI note (`WS_S_SI_note_draft.md`) |

## Notes

1. **Hartree at 10⁻⁴** (now measured, S2c).
   - Map-free, 10/300 objects cannot certify m in the decoded frame, giving 76×.
   - With the hybrid policy (atom map only for those 10), the law reaches 1,036× [927, 1,152].
   - A like-for-like pointwise figure under the same hybrid policy was not measured.
2. **Word budget.** The abstract replacement can keep its length ("Certified storage of whole objects
   would …" = +2 words; cut "unused" and one other word). The Methods sentence needs about 30 words; cut
   them from the deployment paragraph.
3. **Re-run the audits.** After any edit, run `paper/nc_reopen/audit_manuscript.py` and
   `test_scientific_claims.py`. The tests read archive numbers from the committed estimates, so they must be
   pointed at the new estimate files.
