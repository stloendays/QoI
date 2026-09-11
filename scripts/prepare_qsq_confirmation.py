#!/usr/bin/env python3
"""Prepare immutable QSQ work orders; no density or Bader calculation is run."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import pandas as pd

CODECS = ("ZFP", "SZ3", "SPERR")
OLD_SEEDS = {20260905, 1, 2, 3, 4}
FRESH_SEEDS = tuple(range(10000, 10059))


def check(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def stream_seed(material: str, label: int) -> int:
    msg = f"QSQ-heldout|{material}|iid_uniform|{label}".encode()
    return int.from_bytes(hashlib.sha256(msg).digest()[:8], "little")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    check(not OLD_SEEDS.intersection(FRESH_SEEDS), "Seed-label overlap")
    check(len(FRESH_SEEDS) == 59, "Wrong validation size")
    check(stream_seed("test", 10000) == stream_seed("test", 10000), "Non-deterministic stream")
    check(stream_seed("test", 10000) != stream_seed("test", 10001), "Stream collision")
    if args.self_test:
        print("WORK_ORDER_SELF_TEST_PASS")
        return
    root = args.root.resolve()
    out = root / "validation/qsq_prospective"
    out.mkdir(parents=True, exist_ok=True)
    inputs = ["benchmark/master_benchmark_full.csv", "stability/stability_floor_A1_per_seed.csv", "validation/qsq_prospective/PROTOCOL.md"]
    hashes = {p: digest(root / p) for p in inputs}
    d = pd.read_csv(root / inputs[0])
    s = pd.read_csv(root / inputs[1])
    d["codec"] = d.codec.str.upper()
    cols = ["material_id", "system_type", "corpus", "stability_floor_A1_e", "npoints", "natoms", "field_sha256_prefix"]
    check((d.groupby("material_id")[cols[1:]].nunique(dropna=False) == 1).all().all(), "Inconsistent material provenance")
    meta = d[cols].drop_duplicates().sort_values("material_id")
    check(len(meta) == 254, "Development population changed")
    check((s.groupby("material_id").probe_linf.nunique() == 1).all(), "Probe amplitude changed within material")
    eps = s.groupby("material_id").probe_linf.first()
    meta["epsilon"] = meta.material_id.map(eps)
    check(meta.epsilon.notna().all() and (meta.epsilon >= 0).all(), "Missing/negative epsilon")
    tight = d[d.ladder.eq("tight")]
    rungs = sorted(tight.nominal_tolerance_relative.unique().tolist())
    check(len(rungs) == 4 and tight.material_id.nunique() == 143, "Tight design changed")
    existing = set(zip(d.material_id, d.codec, d.nominal_tolerance_relative))
    jobs = []
    for m in meta.itertuples(index=False):
        for codec in CODECS:
            for rung in rungs:
                if (m.material_id, codec, rung) not in existing:
                    config = d.loc[(d.material_id == m.material_id) & (d.codec == codec), "codec_config"].unique()
                    check(len(config) == 1, "Codec configuration is not unique")
                    jobs.append(dict(material_id=m.material_id, codec=codec, nominal_tolerance_relative=rung,
                                     codec_config=config[0], field_fingerprint=m.field_sha256_prefix,
                                     status="PREPARED_NOT_EXECUTED"))
    missing = pd.DataFrame(jobs)
    check(len(missing) == 1332 and missing.material_id.nunique() == 111, "Missing-tight design differs from audit")
    missing.to_csv(out / "missing_tight_jobs.csv", index=False)
    probes = []
    for m in meta.itertuples(index=False):
        for seed in FRESH_SEEDS:
            probes.append(dict(material_id=m.material_id, family="iid_uniform", seed_label=seed,
                               stream_seed=stream_seed(m.material_id, seed), epsilon=m.epsilon,
                               field_fingerprint=m.field_sha256_prefix, npoints=m.npoints,
                               status="PREPARED_NOT_EXECUTED"))
    probes = pd.DataFrame(probes)
    check(len(probes) == 14986 and not probes.stream_seed.duplicated().any(), "Probe work order collision or size error")
    probes.to_csv(out / "fresh_seed_jobs.csv", index=False)
    meta["floor_band"] = pd.cut(meta.stability_floor_A1_e,
        bins=[float("-inf"), 1e-4, 1e-3, 1e-2, float("inf")], right=False,
        labels=["below_1e-4", "1e-4_to_1e-3", "1e-3_to_1e-2", "at_least_1e-2"])
    meta["selection_hash"] = meta.material_id.map(lambda m: hashlib.sha256(f"QSQ-convergence|{m}".encode()).hexdigest())
    groups = meta.groupby(["system_type", "floor_band"], observed=True)
    check(len(groups) == 8 and groups.size().min() >= 3, "Cannot fill convergence strata")
    panel = meta.sort_values("selection_hash").groupby(["system_type", "floor_band"], observed=True).head(3)
    panel = panel.sort_values(["system_type", "floor_band", "selection_hash"])
    check(len(panel) == 24, "Convergence panel size mismatch")
    panel["status"] = "PREPARED_NOT_EXECUTED"
    panel.to_csv(out / "convergence_panel.csv", index=False)
    check(hashes == {p: digest(root / p) for p in inputs}, "Input mutated during preparation")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    manifest = dict(status="PREPARED_NOT_EXECUTED", preparation_commit=commit,
                    input_sha256=hashes, primary_tau_e=1e-3, secondary_taus_e=[1e-4, 1e-2],
                    new_seed_labels=list(FRESH_SEEDS), old_seed_labels=sorted(OLD_SEEDS),
                    missing_tight_jobs=len(missing), missing_tight_materials=111, tight_relative_settings=rungs,
                    fresh_seed_jobs=len(probes), fresh_seed_materials=254, convergence_panel_materials=24,
                    new_material_external_validation=False,
                    required_before_execution=["original density-loader/compute-runner commit", "solver and environment fingerprints", "baseline-density/atom-mapping checks"],
                    work_order_sha256={p.name: digest(p) for p in [out/"missing_tight_jobs.csv", out/"fresh_seed_jobs.csv", out/"convergence_panel.csv"]})
    (out / "execution_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
