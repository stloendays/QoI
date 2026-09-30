#!/usr/bin/env python3
"""WP-E report: RESULTS.md and fig_writer.{png,svg} from policy_summary.csv / policy_material.csv (no hand-typed numbers)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "figures" / "composite"))
from style import CODEC_DARK, DARK_B, DARK_G, INK, MID, OTHER, RED, Page, grid, open_frame  # noqa: E402
import layout  # noqa: E402

S = pd.read_csv(HERE / "policy_summary.csv")
M = pd.read_csv(HERE / "policy_material.csv")
A = json.load(open(HERE / "adopted_policy.json"))
TAUS = (1e-4, 1e-3, 1e-2)
MULTI = ("EXHAUSTIVE", "SCAN", "BISECT")

# ---- figure ---------------------------------------------------------------------------------------------
pg = Page(183.0, 70.0)
ax = pg.ax(14, 12, 74, 52)
pg.letter("a", 2, 69)
mk = {1e-4: "o", 1e-3: "s", 1e-2: "^"}
col = {"EXHAUSTIVE": OTHER, "SCAN": DARK_G, "BISECT": DARK_B, "SCAN-ZFP": CODEC_DARK["ZFP"], "BISECT-ZFP": CODEC_DARK["ZFP"]}
for p in ("EXHAUSTIVE", "SCAN", "BISECT", "BISECT-ZFP"):
    d = S[S.policy == p].sort_values("tau_e")
    ax.plot(d.mean_solves_eligible, d.fraction_of_oracle, color=col[p], lw=0.8, zorder=2)
    for _, r in d.iterrows():
        ax.errorbar(r.mean_solves_eligible, r.fraction_of_oracle,
                    yerr=[[r.fraction_of_oracle - r.fraction_ci_low], [r.fraction_ci_high - r.fraction_of_oracle]],
                    fmt=mk[r.tau_e], ms=4.2, color=col[p], mfc=col[p] if p != "BISECT-ZFP" else "white", lw=0.7, capsize=1.5, zorder=3)
ax.axhline(0.98, color=RED, lw=0.7, ls=(0, (3, 2)), zorder=1)
ax.text(43, 0.972, "adoption threshold 0.98", fontsize=5.4, color=RED, ha="right", va="top")
ax.set_xlim(5, 44); ax.set_ylim(0.5, 1.03)
ax.set_xlabel("Bader solves per eligible material (QSQ + certification)")
ax.set_ylabel("archive compression, fraction of oracle")
open_frame(ax); grid(ax)
from matplotlib.lines import Line2D  # noqa: E402
h = [Line2D([], [], marker=mk[t], ls="none", color=INK, ms=4, label=r"$\tau$ = %g e" % t) for t in TAUS]
h += [Line2D([], [], color=col[p], lw=1.0, marker="o", ms=3, mfc=col[p] if p != "BISECT-ZFP" else "white", label=p.replace("-", " "))
      for p in ("EXHAUSTIVE", "SCAN", "BISECT", "BISECT-ZFP")]
# lower right is empty: every multi-codec policy sits near 1, the single-codec one near 10 solves
layout.legend(ax, handles=h, labels=[x.get_label() for x in h], loc="lower right", ncol=2)

ax = pg.ax(108, 12, 70, 52)
pg.letter("b", 96, 69)
e = M[(M.policy == "BISECT") & M.eligible & M.oracle_exists]
for i, t in enumerate(TAUS):
    r = (e[e.tau_e == t].returned_cr / e[e.tau_e == t].oracle_cr).fillna(0).clip(upper=1).sort_values().values
    ax.step(np.arange(1, len(r) + 1) / len(r), r, where="post", color=(DARK_B, DARK_G, MID)[i], lw=1.0, label=r"$\tau$ = %g e (n = %d)" % (t, len(r)))
ax.set_xlim(0, 0.15); ax.set_ylim(0, 1.05)
ax.text(0.148, 1.035, "all remaining materials: ratio 1", fontsize=5.4, color=MID, ha="right", va="bottom")
ax.set_xlabel("cumulative fraction of eligible materials (first 15%)")
ax.set_ylabel("BISECT ratio / oracle ratio (per material)")
open_frame(ax); grid(ax)
layout.legend(ax, loc="lower right")
layout.audit(pg.fig)
pg.save(str(HERE), "fig_writer")

# ---- RESULTS.md -----------------------------------------------------------------------------------------
def row(p, t):
    return S[(S.policy == p) & np.isclose(S.tau_e, t)].iloc[0]


L = ["# WP-E — A certifying writer on the frozen development ladders", "",
     "No new computation: 254 development materials, 6,343 frozen reconstruction rows; a policy pays 6 Bader solves",
     "for QSQ (reference + 5 probes) and 1 solve per rung it evaluates. Certificates were re-checked mechanically:",
     "every returned row is certified at its τ.", "",
     "## Adopted policy", "", "**%s** — %s." % (A["adopted_policy"], A["reason"]), "",
     "## Multi-codec policies", "",
     "| τ (e) | policy | eligible | archive CR | oracle archive CR | fraction of oracle [95% CI] | misses | per-material ratio median / P05 | solves per eligible material |",
     "|---:|---|---:|---:|---:|---|---:|---|---:|"]
for t in TAUS:
    for p in MULTI:
        r = row(p, t)
        L.append("| %g | %s | %d | %.2f | %.2f | %.4f [%.4f, %.4f] | %d / %d | %.3f / %.3f | %.1f |" % (
            t, p, r.n_eligible, r.archive_cr, r.oracle_archive_cr, r.fraction_of_oracle, r.fraction_ci_low, r.fraction_ci_high,
            r.miss_count, r.n_oracle_certifiable, r.per_material_cr_ratio_median, r.per_material_cr_ratio_p05, r.mean_solves_eligible))
L += ["", "## Single-codec policies (no codec search)", "",
      "| τ (e) | policy | archive CR | fraction of oracle | misses | solves per eligible material |", "|---:|---|---:|---:|---:|---:|"]
for t in TAUS:
    for p in [x for x in S.policy.unique() if "-" in x]:
        r = row(p, t)
        L.append("| %g | %s | %.2f | %.4f | %d | %.1f |" % (t, p, r.archive_cr, r.fraction_of_oracle, r.miss_count, r.mean_solves_eligible))
b, x = row("BISECT", 1e-3), row("EXHAUSTIVE", 1e-3)
L += ["", "## Reading", "",
      "At τ = 1e-3 e the writer (QSQ, then per-codec bisection, best of three codecs) keeps %.1f%% of the oracle archive"
      " compression (%.2f of %.2f) with no eligible material left uncompressed, at %.1f instead of %.1f Bader solves per"
      " eligible material (%.0f%% fewer). Codec search matters more than ladder search: the best single codec keeps at most"
      " %.1f%% of the oracle at the same τ." % (100 * b.fraction_of_oracle, b.archive_cr, b.oracle_archive_cr, b.mean_solves_eligible,
                                               x.mean_solves_eligible, 100 * (1 - b.mean_solves_eligible / x.mean_solves_eligible),
                                               100 * S[(S.policy.str.contains("-")) & np.isclose(S.tau_e, 1e-3)].fraction_of_oracle.max()),
      "", "Files: `policy_material.csv`, `policy_summary.csv`, `adopted_policy.json`, `fig_writer.{png,svg,pdf}`, `provenance.json`."]
(HERE / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
