#!/usr/bin/env python3
"""results/RESULTS.md of study 4 and of study 5 (partition fix) from results/SUMMARY.json (numbers first)."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE.parent / "archive_partition_fix_20261025"
NAMES = {"V": "V: W2S density + W2M magnetization", "VP": "VP: W2S density + pointwise magnetization",
         "W": "W: W1S (revision 11), partition fixed", "Q": "Q: O1S on W1 (revision 11), partition fixed",
         "O": "O: operational allocation A3 (revision 10), partition fixed", "L": "L: closed-form law",
         "T": "T: truncation (revision 10), partition fixed", "P": "P: best pointwise codec"}


def est(S, k):
    v = S["estimates"].get(k)
    return "—" if not v else f"{v['R']:,.0f} ({v['ci95'][0]:,.0f}–{v['ci95'][1]:,.0f})"


def pr(S, k):
    v = S["paired"].get(k)
    return "—" if not v else f"{v['ratio']:.3f} ({v['ci95'][0]:.3f}–{v['ci95'][1]:.3f})"


def main():
    S = json.loads((HERE / "results" / "SUMMARY.json").read_text(encoding="utf-8"))
    out = ["# Study 4 — the archive under the W2 writer: results", "",
           f"Whole-object reduction of the 8.50 TB frame (stratified ratio estimate, 300 objects, paired bootstrap seed "
           f"{S['seed']}, {S['resamples']} resamples). Objects processed: {json.dumps(S['objects_success'])}.", "",
           "| writer | 1e-6 | 1e-4 | magnetization share 1e-6 / 1e-4 |", "|---|---|---|---|"]
    for w in ("V", "VP", "W", "Q", "O", "L", "T", "P"):
        ms = " / ".join(f"{S['m_share'][f'{w}_{k}'] * 100:.1f}%" if f"{w}_{k}" in S["m_share"] else "—"
                        for k in ("1e-06", "0.0001"))
        out.append(f"| {NAMES[w]} | {est(S, f'{w}_1e-06')} | {est(S, f'{w}_0.0001')} | {ms} |")
    a1v = [S["paired"].get("V/W_1e-06"), S["paired"].get("V/W_0.0001")]
    met_a1 = bool(a1v[0] and a1v[1] and a1v[0]["ratio"] >= 1.15 and a1v[0]["ci95"][0] >= 1.10
                  and a1v[1]["ratio"] >= 1.5 and a1v[1]["ci95"][0] >= 1.3)
    out += ["", "## Criteria", "",
            f"- **A1 archive** V/W: 1e-6 {pr(S, 'V/W_1e-06')}, 1e-4 {pr(S, 'V/W_0.0001')} — "
            f"**{'met' if met_a1 else 'not met'}**."]
    m_ok = []
    for k in ("1e-06", "0.0001"):
        m = S["moment_stream"].get(k) or {}
        x = m.get("pw_over_w2m") or {}
        ok = bool(x and x["median"] >= 2 and x["wins"] >= 0.7 * x["n"])
        m_ok.append(ok)
        out.append(f"- **M1 magnetization stream** {k}: pointwise/W2M median {x.get('median', 0):.2f} "
                   f"(CI {x['ci95'][0]:.2f}–{x['ci95'][1]:.2f}), W2M smaller in {x.get('wins')}/{x.get('n')}; "
                   f"moment-eligible {m.get('m_eligible')}, W2M certified {m.get('w2m_certified')}, pointwise certified "
                   f"{m.get('pw_certified')}; median bytes W2M {m.get('w2m_bytes_median')} vs pointwise "
                   f"{m.get('pw_bytes_median')}." if x else f"- **M1** {k}: no comparable objects.")
    out.append(f"- M1 — **{'met' if all(m_ok) else 'not met'}**.")
    out += ["", "## Paired ratios", "", "| ratio | 1e-6 | 1e-4 |", "|---|---|---|"]
    for a, b in (("V", "W"), ("V", "O"), ("V", "Q"), ("V", "L"), ("V", "T"), ("V", "P"), ("V", "VP"), ("VP", "W"),
                 ("W", "O"), ("O", "L"), ("O", "T"), ("L", "T")):
        out.append(f"| {a}/{b} | {pr(S, f'{a}/{b}_1e-06')} | {pr(S, f'{a}/{b}_0.0001')} |")
    out += ["", "## Density writer and partitions", "",
            f"- W2S variants: {json.dumps(S['variants'], default=str)}",
            f"- Porod exponent of the decoded partition (shells 2–24): {json.dumps(S['porod_exponent'])}", ""]
    (HERE / "results" / "RESULTS.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    fx = ["# Study 5 — partition fix: results", "",
          "Revision 10's T/O and revision 11's W/Q rerun with every decoded Bader partition rebuilt (study 4's "
          "`whole_archive.py`, same estimator).", "", "| writer | committed | fixed | change |", "|---|---|---|---|"]
    for k, v in S["committed"].items():
        fx.append(f"| {k} | {v['committed_R']:,.1f} | {v['fixed_R']:,.1f} | {v['change'] * 100:+.2f}% |")
    (FIX / "results").mkdir(exist_ok=True)
    (FIX / "results" / "RESULTS.md").write_text("\n".join(fx) + "\n", encoding="utf-8")
    print("\n".join(out[:16]))
    print("\n".join(fx))


if __name__ == "__main__":
    main()
