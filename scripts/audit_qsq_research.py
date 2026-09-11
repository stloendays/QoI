#!/usr/bin/env python3
"""Retrospective QSQ audits. Reads frozen inputs; never rewrites their labels.

Outputs separate fixed-pipeline agreement from QSQ eligibility. A missing
reconstruction is unavailable, not a measured codec failure. Existing seeds
are reused retrospectively: this is NOT an independent validation of QSQ.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

TAUS = ("0.0001", "0.001", "0.01")
CODECS = ("ZFP", "SZ3", "SPERR")
SEEDS = (20260905, 1, 2, 3, 4)
BOOTSTRAPS = 2000


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def flag(s: pd.Series) -> pd.Series:
    v = s.astype(str).str.strip().str.lower()
    require(v.isin(["true", "false", "1", "0"]).all(), "Missing/invalid Boolean flag")
    return v.isin(["true", "1"])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ratio(n: float, d: float) -> float:
    return float(n / d) if d else float("nan")


def cluster_ratio(frame: pd.DataFrame, numerator: str, denominator: str) -> tuple[float, float]:
    """Descriptive material-cluster percentile interval, not a guarantee."""
    v = frame.groupby("material_id")[[numerator, denominator]].sum().to_numpy(float)
    if not len(v) or not v[:, 1].sum():
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(20260911)
    draws = rng.integers(0, len(v), (BOOTSTRAPS, len(v)))
    totals = v[draws].sum(axis=1)
    z = totals[totals[:, 1] > 0]
    q = np.quantile(z[:, 0] / z[:, 1], [.025, .975])
    return float(q[0]), float(q[1])


def decisions(rows: pd.DataFrame, universe: pd.DataFrame, tau: str, design: str) -> pd.DataFrame:
    idx = ["material_id", "codec"]
    tmp = rows.copy()
    tmp["finite_result"] = np.isfinite(tmp["Bader_error_resolved_e"])
    tmp["numerical_pass"] = tmp["finite_result"] & (tmp["Bader_error_resolved_e"] < float(tau))
    grouped = tmp.groupby(idx).agg(valid_rows=("finite_result", "sum"), numerical_pass=("numerical_pass", "any"))
    out = universe.merge(grouped, on=idx, how="left")
    out["valid_rows"] = out.valid_rows.fillna(0).astype(int)
    out["numerical_pass"] = out.numerical_pass.eq(True)
    out["available"] = out.valid_rows > 0
    out["eligible"] = out.stability_floor_A1_e < float(tau)
    out["no_pass_observed"] = out.available & ~out.numerical_pass
    out["qualified_pass"] = out.available & out.eligible & out.numerical_pass
    out["eligible_no_pass"] = out.no_pass_observed & out.eligible
    out["non_evaluable"] = ~out.eligible
    out["non_evaluable_no_pass"] = out.non_evaluable & out.no_pass_observed
    out["non_evaluable_pass"] = out.non_evaluable & out.numerical_pass
    out["design"] = design
    out["tau_e"] = float(tau)
    return out


def summarize(d: pd.DataFrame) -> dict:
    n = len(d)
    nf = int(d.no_pass_observed.sum())
    ne = int(d.non_evaluable.sum())
    ef = int(d.eligible_no_pass.sum())
    nef = int(d.non_evaluable_no_pass.sum())
    npass = int(d.numerical_pass.sum())
    eligible_available = int((d.eligible & d.available).sum())
    ne_available = int((d.non_evaluable & d.available).sum())
    lo, hi = cluster_ratio(d, "non_evaluable_no_pass", "no_pass_observed")
    return dict(n_decisions=n, available=int(d.available.sum()), unavailable=int((~d.available).sum()),
                numerical_pass=npass, no_pass_observed=nf, qualified_pass=int(d.qualified_pass.sum()),
                eligible_no_pass=ef, non_evaluable=ne, non_evaluable_no_pass=nef,
                non_evaluable_pass=int(d.non_evaluable_pass.sum()),
                non_evaluable_share=ratio(ne, n),
                fraction_no_pass_non_evaluable=ratio(nef, nf),
                reclassification_cluster_ci_low=lo, reclassification_cluster_ci_high=hi,
                fraction_numerical_pass_non_evaluable=ratio(int(d.non_evaluable_pass.sum()), npass),
                no_pass_risk_eligible=ratio(ef, eligible_available),
                no_pass_risk_non_evaluable=ratio(nef, ne_available),
                risk_ratio_non_evaluable_vs_eligible=ratio(ratio(nef, ne_available), ratio(ef, eligible_available)))


def audit_ladders(root: Path, outdir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    d = pd.read_csv(root / "benchmark/master_benchmark_full.csv")
    d["codec"] = d.codec.str.upper()
    require(len(d) == 6343, "Frozen master row count changed")
    require(set(d.codec) == set(CODECS), "Unexpected codec set")
    require(set(d.ladder) == {"base", "tight"}, "Unexpected ladder set")
    keys = ["material_id", "codec", "nominal_tolerance_relative"]
    require(not d.duplicated(keys).any(), "Duplicate material-codec-tolerance key")
    cols = ["system_type", "corpus", "stability_floor_A1_e"]
    require((d.groupby("material_id")[cols].nunique(dropna=False) == 1).all().all(), "Inconsistent material attributes")
    require(np.isfinite(d.stability_floor_A1_e).all(), "Missing reference floor")
    meta = d[["material_id"] + cols].drop_duplicates()
    require(len(meta) == 254, "Frozen development universe changed")
    u = meta.merge(pd.DataFrame({"codec": CODECS}), how="cross")
    for t in TAUS:
        e = flag(d[f"eligible_A1_at_{t}"])
        p = flag(d[f"certified_at_{t}_ignoring_eligibility"])
        c = flag(d[f"certified_at_{t}"])
        require((e == (d.stability_floor_A1_e < float(t))).all(), f"Eligibility mismatch {t}")
        require((p == (d.Bader_error_resolved_e < float(t))).all(), f"Numerical-pass mismatch {t}")
        require((c == (e & p)).all(), f"Certified flag mismatch {t}")
    base = d[d.ladder.eq("base")].copy()
    support = base.groupby(["material_id", "nominal_tolerance_relative"]).codec.nunique()
    support = support[support.eq(len(CODECS))].reset_index()[["material_id", "nominal_tolerance_relative"]]
    common = base.merge(support, on=["material_id", "nominal_tolerance_relative"], how="inner")
    expected = {
        "0.0001": (229, 533, 123, 15, 624, 106, 518),
        "0.001": (452, 310, 415, 14, 333, 37, 296),
        "0.01": (654, 108, 640, 47, 75, 14, 61),
    }
    checkcols = ["numerical_pass", "no_pass_observed", "qualified_pass", "eligible_no_pass", "non_evaluable", "non_evaluable_pass", "non_evaluable_no_pass"]
    all_d, all_s = [], []
    for name, rows in [("full_record", d), ("base_only", base), ("shared_base_rungs", common)]:
        for t in TAUS:
            z = decisions(rows, u, t, name)
            s = summarize(z)
            if name == "full_record":
                require(tuple(s[c] for c in checkcols) == expected[t], f"Frozen Figure 3 does not reproduce at {t}")
            all_d.append(z)
            for scope, zz in [("all", z)] + [(cc, z[z.codec.eq(cc)]) for cc in CODECS]:
                all_s.append(dict(design=name, tau_e=float(t), scope=scope, **summarize(zz)))
    decision_table = pd.concat(all_d, ignore_index=True)
    summary = pd.DataFrame(all_s)
    coverage = u.merge(d.groupby(["material_id", "codec", "ladder"]).size().unstack(fill_value=0).reset_index(), how="left")
    coverage["tight_access"] = coverage.tight.gt(0)
    coverage.to_csv(outdir / "ladder_coverage.csv", index=False)
    decision_table.to_csv(outdir / "ladder_decisions.csv", index=False)
    summary.to_csv(outdir / "ladder_summary.csv", index=False)
    transitions = []
    for t in TAUS:
        a = decision_table[decision_table.design.eq("base_only") & decision_table.tau_e.eq(float(t))]
        b = decision_table[decision_table.design.eq("full_record") & decision_table.tau_e.eq(float(t))]
        w = a.merge(b, on=["material_id", "codec"], suffixes=("_base", "_full"))
        newpass = ~w.numerical_pass_base & w.numerical_pass_full
        transitions.append(dict(tau_e=float(t), base_to_full_added_passes=int(newpass.sum()),
                                added_eligible_passes=int((newpass & w.eligible_full).sum()),
                                added_non_evaluable_passes=int((newpass & ~w.eligible_full).sum())))
    pd.DataFrame(transitions).to_csv(outdir / "ladder_transitions.csv", index=False)
    return summary, coverage


def audit_seeds(root: Path, outdir: Path) -> pd.DataFrame:
    s = pd.read_csv(root / "stability/stability_floor_A1_per_seed.csv")
    require(not s.duplicated(["material_id", "seed"]).any(), "Duplicate material-seed key")
    require(set(s.seed) == set(SEEDS), "Seed set changed")
    require((s.groupby("material_id").size() == 5).all(), "Incomplete five-seed panel")
    require(np.isfinite(s.floor_noise_resolved_e).all(), "Missing probe responses")
    meta = s.groupby("material_id").corpus.first()
    p = s.pivot(index="material_id", columns="seed", values="floor_noise_resolved_e").reindex(columns=SEEDS)
    require(len(p) == 319, "Stability universe changed")
    v = p.to_numpy()
    records = []
    for k in range(1, 5):
        for train in itertools.combinations(range(5), k):
            test = tuple(i for i in range(5) if i not in train)
            tr = v[:, train].max(axis=1)
            te = v[:, test].max(axis=1)
            for t in TAUS:
                eligible = tr < float(t)
                for j, mid in enumerate(p.index):
                    records.append(dict(material_id=mid, corpus=meta.loc[mid], train_n=k,
                                        train_seeds=";".join(str(SEEDS[i]) for i in train), tau_e=float(t),
                                        train_eligible=bool(eligible[j]), heldout_exceeds=bool(te[j] >= float(t)),
                                        false_safe=bool(eligible[j] and te[j] >= float(t)),
                                        train_max_e=float(tr[j]), heldout_max_e=float(te[j])))
    detail = pd.DataFrame(records)
    summary = []
    for cohort, subset in [("all_stability_319", detail),
                           ("development", detail[detail.corpus.str.startswith("dev_")]),
                           ("external_descriptive", detail[~detail.corpus.str.startswith("dev_")])]:
        for (k, t), z in subset.groupby(["train_n", "tau_e"], sort=True):
            lo, hi = cluster_ratio(z, "false_safe", "train_eligible")
            eligible_n = int(z.train_eligible.sum())
            fail_n = int(z.false_safe.sum())
            summary.append(dict(cohort=cohort, train_n=int(k), test_n=5-int(k), tau_e=float(t),
                                n_materials=z.material_id.nunique(), n_material_splits=len(z),
                                eligible_splits=eligible_n, heldout_exceedances=fail_n,
                                heldout_exceedance_fraction=ratio(fail_n, eligible_n),
                                material_cluster_ci_low=lo, material_cluster_ci_high=hi,
                                affected_materials=z.loc[z.false_safe, "material_id"].nunique(),
                                validation_type="retrospective_reused_seeds_not_prospective"))
    result = pd.DataFrame(summary)
    result.to_csv(outdir / "seed_holdout_summary.csv", index=False)
    detail[detail.train_n.eq(4)].to_csv(outdir / "seed_holdout_four_to_one.csv", index=False)
    return result


def markdown(frame: pd.DataFrame) -> str:
    def text(v: object) -> str:
        if isinstance(v, (float, np.floating)):
            return f"{v:.6g}" if math.isfinite(v) else "NA"
        return str(v)
    return "\n".join(["| " + " | ".join(frame.columns) + " |", "| " + " | ".join(["---"]*len(frame.columns)) + " |"] +
                     ["| " + " | ".join(text(v) for v in row) + " |" for row in frame.itertuples(index=False, name=None)])


def self_test() -> None:
    u = pd.DataFrame([dict(material_id="a", codec="ZFP", stability_floor_A1_e=.001),
                      dict(material_id="b", codec="ZFP", stability_floor_A1_e=0.)])
    rows = pd.DataFrame([dict(material_id="a", codec="ZFP", Bader_error_resolved_e=0.)])
    z = decisions(rows, u, "0.001", "unit_test")
    require(bool(z.iloc[0].numerical_pass) and not bool(z.iloc[0].eligible), "Lossless reference counterexample lost")
    require(not bool(z.iloc[1].available) and not bool(z.iloc[1].no_pass_observed), "Missing row treated as failure")
    require(not bool(z.iloc[0].qualified_pass), "Boundary should be non-evaluable")
    x = np.array([0., 0., 0., 0., 2.])
    require((x[:4].max() < 1) and (x[4] >= 1), "Held-out exceedance logic")
    print("SELF_TEST_PASS: strict threshold; numerical/robust distinction; missingness; holdout")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--output", type=Path, default=Path("analysis/research_upgrade"))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    self_test()
    if args.self_test:
        return
    root = args.root.resolve()
    out = args.output if args.output.is_absolute() else root / args.output
    out.mkdir(parents=True, exist_ok=True)
    paths = ["benchmark/master_benchmark_full.csv", "stability/stability_floor_A1_per_seed.csv", "protocol/PROTOCOL_A1.md"]
    before = {p: sha256(root / p) for p in paths}
    ladders, coverage = audit_ladders(root, out)
    seeds = audit_seeds(root, out)
    after = {p: sha256(root / p) for p in paths}
    require(before == after, "Frozen input was mutated")
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        commit = "not_a_git_checkout"
    manifest = dict(source_commit=commit, input_sha256=before, inputs_unchanged=True,
                    frozen_figure3_reproduced=True, bootstrap_replicates=BOOTSTRAPS,
                    bootstrap_unit="material", retrospective=True,
                    numpy_version=np.__version__, pandas_version=pd.__version__)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    pooled = ladders[ladders.scope.eq("all")]
    selected = pooled[["design", "tau_e", "n_decisions", "unavailable", "numerical_pass", "no_pass_observed", "non_evaluable_no_pass", "fraction_no_pass_non_evaluable", "non_evaluable_share"]]
    hold = seeds[seeds.cohort.eq("all_stability_319") & seeds.train_n.eq(4)]
    report = "# QSQ research audit\n\nStatus: executed retrospective audit, not prospective confirmation.\n\n"
    report += f"Source commit: `{commit}`. Frozen inputs unchanged; original Figure 3 counts reproduced exactly.\n\n"
    report += "## Common-ladder comparison\n\n" + markdown(selected) + "\n\n"
    report += "`base_only` removes the eligibility-targeted tight extension. `shared_base_rungs` additionally keeps only within-material nominal rungs observed for all three codecs; this is observed-support sensitivity, not a missingness cure. Neither makes nominal error equal realized error. `no_pass_observed` means no available rung passed, not proof of intrinsic compressor failure. Full per-codec results, material-cluster intervals, eligibility prevalence and no-pass risks are in `ladder_summary.csv`. Report prevalence alongside reclassification: an already-large excluded population can produce a large concentration of no-pass outcomes.\n\n"
    report += "## Four training seeds to one held-out seed\n\n" + markdown(hold[["tau_e", "n_materials", "eligible_splits", "heldout_exceedances", "heldout_exceedance_fraction", "affected_materials", "material_cluster_ci_low", "material_cluster_ci_high"]]) + "\n\n"
    report += "Each material occurs in five correlated splits; uncertainty resamples materials, never treats 1,595 splits as independent materials. Seeds were already used in development. This estimates retrospective four-seed screening fragility, NOT the false-eligibility rate of the deployed five-seed rule on fresh perturbations. A degenerate bootstrap interval at zero events is NOT a zero upper error bound. Results for one/two/three training seeds are exploratory and have different held-out-set sizes, so their rates are not a controlled seed-budget comparison. External descriptive records are not the 63-system confirmatory cohort.\n\n"
    report += "## Next decisive experiments\n\nFreeze a new perturbation/validation manifest before new runs; retain the current QSQ record. Test fresh seeds and independently specified perturbation families; measure both rejection coverage and conditional held-out exceedance risk. Separate deterministic pipeline fidelity from perturbation robustness. A single valid counterexample refutes uniform robustness; no finite random probe panel establishes it without assumptions. Under independent Bernoulli trials from one fixed perturbation distribution, zero exceedances in n trials gives one-sided 95% upper limit 1-0.05**(1/n). This is about perturbation risk for that target/family, not risk across materials or all possible perturbations.\n\n"
    report += f"For n=5 this limit is {1-.05**(1/5):.6f}; for n=59 it is {1-.05**(1/59):.6f}. Multiple families/materials require separately declared multiplicity handling.\n\n"
    report += "## Integrity\n\nNo densities, reconstruction rows, seeds, thresholds, protocol files or frozen labels were changed. All outputs are additive; no new scientific measurements were synthesized.\n"
    (out / "REPORT.md").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
