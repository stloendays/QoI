#!/usr/bin/env python3
"""Data-free tests of run_joint_v2 (GF base codec, several tau_B, hartree_only) and aggregate_joint_v2.

Everything that would download or call an external binary is replaced by a stub on fabricated small fields:
- `run_engineering.fetch` returns fixed bytes; `development_compatibility_smoke` returns a fabricated periodic
  density on a triclinic cell;
- `external_end_to_end.codec_roundtrip` is a deterministic uniform quantizer with |error| <= abs_tol whose byte
  count is the zlib size of the quantization indices (it accepts exactly the codec names zfp, sz3 and sperr);
- `run_engineering.Solver` is the octant stub of smoke_stub_bader.py with charges = octant sums.
The numbers have no scientific meaning; the tests check bookkeeping, tau_B logic, reuse and aggregation.

    python -m unittest -q test_runner_v2.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import tempfile
import time
import types
import unittest
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import aggregate_joint_v2 as ag  # noqa: E402
import run_joint_v2 as rj  # noqa: E402

SHAPE = (16, 16, 18)
LATTICE = np.array([[4.1, 0.0, 0.0], [1.3, 3.7, 0.0], [0.6, -0.9, 5.2]])
MATERIALS = ("mp-fake-1", "mp-fake-2", "mp-fake-3")
MUS = (1e-4, 1.0)
TAUS = (1e-3, 1e-4, 1e-5)
BASES = ("J", "GF", "R3", "GP")
CHARGE_SCALE = 0.05   # puts unprojected stub Bader errors of Hartree-certified rows around 1e-4 ... 1e-3


def fabricated_density(seed: int) -> np.ndarray:
    """Periodic positive density (CHGCAR convention, rho * V) from a few Gaussian blobs."""
    rng = np.random.default_rng(seed)
    g = np.stack(np.meshgrid(*[np.arange(n) / n for n in SHAPE], indexing="ij"), axis=-1)
    rho = np.full(SHAPE, 5.0)
    for c, w, h in zip(rng.random((4, 3)), 0.08 + 0.05 * rng.random(4), 200 + 400 * rng.random(4)):
        d = g - c
        d -= np.rint(d)
        rho += h * np.exp(-np.sum((d @ LATTICE) ** 2, axis=-1) / (2 * (w * 4.0) ** 2))
    return rho


def blob_of(mid: str) -> bytes:
    return f"CHGCAR:{mid}".encode()


class FakeDev(types.ModuleType):
    def __init__(self):
        super().__init__("development_compatibility_smoke")

    def build_grid(self, meta, chg_blob, work):
        seed = MATERIALS.index(meta["material_id"])
        assert chg_blob == blob_of(meta["material_id"])
        sites = [types.SimpleNamespace(specie=types.SimpleNamespace(symbol=s)) for s in ("Fe", "Te")]
        structure = _Structure(LATTICE, np.array([[0.1, 0.2, 0.3], [0.6, 0.7, 0.4]]), sites)
        return types.SimpleNamespace(total=fabricated_density(seed), structure=structure), None

    def decode_mp_chgcar(self, blob):
        mid = blob.decode().split(":", 1)[1]
        rho = fabricated_density(MATERIALS.index(mid))
        return types.SimpleNamespace(data={"total": 0.5 * rho})


class _Structure:
    def __init__(self, lattice, frac, sites):
        self.lattice = types.SimpleNamespace(matrix=lattice)
        self.frac_coords = frac
        self._sites = sites

    def __iter__(self):
        return iter(self._sites)


class FakeCore(types.ModuleType):
    def __init__(self):
        super().__init__("external_end_to_end")
        self.calls = 0

    def codec_roundtrip(self, codec, array, abs_bound, workdir):
        if codec not in ("zfp", "sz3", "sperr"):
            raise ValueError(f"Unknown codec: {codec}")
        self.calls += 1
        step = 2.0 * float(abs_bound) * {"zfp": 0.5, "sz3": 0.9, "sperr": 0.7}[codec]
        q = np.rint(np.asarray(array, dtype=np.float64) / step).astype(np.int64)
        nbytes = len(zlib.compress(np.diff(q.ravel(), prepend=0).tobytes(), 6))
        return (q * step).astype(array.dtype), nbytes, codec


class StubSolver:
    """Octant labels 1..8 (Fortran flat order, as AtIndex.dat); charges = octant sums * CHARGE_SCALE."""
    solves = 0

    def __init__(self, bader, lattice, frac, symbols, shape, work):
        self.shape = tuple(int(v) for v in shape)
        idx = np.indices(self.shape)
        self.labels = sum(((idx[k] >= self.shape[k] // 2).astype(np.int64) << k) for k in range(3)) + 1
        self.flat = self.labels.ravel(order="F").astype(np.int32)

    def __call__(self, field, reference):
        StubSolver.solves += 1
        s = np.bincount(self.labels.ravel(), weights=np.asarray(field, float).ravel(), minlength=9)[1:]
        return s * CHARGE_SCALE, self.flat.copy()


def write_manifest(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["material_id", "task_id", "system_type", "source", "url", "sha256"])
        w.writeheader()
        for mid in MATERIALS:
            w.writerow({"material_id": mid, "task_id": mid, "system_type": "bulk", "source": "fabricated",
                        "url": f"fake://{mid}", "sha256": hashlib.sha256(blob_of(mid)).hexdigest()})


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("material_id")]


class RunnerAndAggregatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="qoachb2_test_")
        root = Path(cls.tmp.name)
        cls.core = FakeCore()
        saved = {k: sys.modules.get(k) for k in ("external_end_to_end", "development_compatibility_smoke")}
        saved_b1 = (rj.b1.fetch, rj.b1.Solver)
        sys.modules["external_end_to_end"] = cls.core
        sys.modules["development_compatibility_smoke"] = FakeDev()
        rj.b1.fetch = lambda url: (blob_of(url.split("//", 1)[1]) if url.startswith("fake://")
                                   else blob_of(url.rsplit("/", 1)[1].split(".")[0]))
        rj.b1.Solver = StubSolver
        decode_calls = {}
        saved_decode = {b: rj.REGISTRY[b].decode for b in BASES}
        for b in BASES:
            def counted(ctx, spec, b=b, fn=saved_decode[b]):
                decode_calls[b] = decode_calls.get(b, 0) + 1
                return fn(ctx, spec)
            rj.REGISTRY[b].decode = counted
        cls.manifest = root / "manifest.csv"
        write_manifest(cls.manifest)
        cls.shards = root / "shards"
        cls.agg = root / "agg"
        try:
            t0 = time.time()
            for i in range(2):
                rj.main(["--repo-root", str(REPO), "--frozen-root", str(root), "--manifest", str(cls.manifest),
                         "--shard-count", "2", "--shard-index", str(i), "--bader", "stub",
                         "--output-dir", str(cls.shards / f"s{i}"), "--base", *BASES,
                         "--mu", *map(str, MUS), "--tau-bader", *map(str, TAUS)])
            cls.wall = time.time() - t0
        finally:
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
            rj.b1.fetch, rj.b1.Solver = saved_b1
            for b, fn in saved_decode.items():
                rj.REGISTRY[b].decode = fn
        cls.decode_calls = decode_calls
        cls.out = {n: [r for s in sorted(cls.shards.glob(f"*/{n}_shard_*.csv")) for r in read(s)]
                   for n in ("rows", "bader", "selected", "failures", "materials")}
        ag.main(["--manifest", str(cls.manifest), "--shards-root", str(cls.shards), "--output-dir", str(cls.agg)])
        cls.summary = json.loads((cls.agg / "SUMMARY.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    # -- runner ---------------------------------------------------------------------------------------------

    def test_gf_candidates(self):
        ctx = types.SimpleNamespace(ptp=2.5)
        cands = rj.REGISTRY["GF"].candidates(ctx)
        self.assertEqual(len(cands), 75)
        self.assertEqual(len({p for p, _ in cands}), 75)
        self.assertEqual({s[0] for _, s in cands}, {"zfp", "sz3", "sperr"})
        tols = sorted({s[1] for _, s in cands})
        np.testing.assert_allclose(tols, 2.5 * np.logspace(-9, -1, 25), rtol=1e-15)
        self.assertIs(rj.REGISTRY["GF"].decode, rj.REGISTRY["GP"].decode)

    def test_tau_bader_cli(self):
        a = rj.parse_args(["--repo-root", ".", "--frozen-root", ".", "--manifest", "m", "--bader", "b",
                           "--output-dir", "o"])
        self.assertEqual(a.tau_bader, [1e-3, 1e-4, 1e-5])
        self.assertEqual(rj.TAU_H, 1e-6)
        for bad in (["0"], ["1e-3", "1e-3"], ["nan"]):
            with self.assertRaises(SystemExit):
                rj.main(["--repo-root", str(REPO), "--frozen-root", ".", "--manifest", "m", "--bader", "b",
                         "--output-dir", str(Path(self.tmp.name) / "x"), "--tau-bader", *bad])

    def test_all_materials_succeed_without_failures(self):
        mats = self.out["materials"]
        self.assertEqual(sorted(m["material_id"] for m in mats), sorted(MATERIALS))
        self.assertTrue(all(m["status"] == "SUCCESS" for m in mats), mats)
        self.assertEqual(self.out["failures"], [])

    def test_candidate_counts_and_rows(self):
        posts = rj.post_names(MUS)
        per_param = 1 + 1 + len(MUS) + 2 * (1 + len(MUS))
        for mid in MATERIALS:
            rows = [r for r in self.out["rows"] if r["material_id"] == mid]
            n = {b: len({r["param"] for r in rows if r["base"] == b}) for b in BASES}
            self.assertEqual(n, {"J": 25, "GF": 75, "R3": 6, "GP": 0})
            self.assertEqual(len(rows), sum(n.values()) * per_param)
            self.assertEqual({r["post"] for r in rows}, set(posts))
            for r in rows:
                self.assertNotIn("tau_bader", r)   # Hartree rows do not depend on tau_B
                if r["stored"] != "U":
                    self.assertLessEqual(float(r["closure_scaled"]), rj.CLOSURE)

    def test_selected_grid_per_tau(self):
        posts = [rj.HARTREE_ONLY] + rj.post_names(MUS)
        got = sorted((s["material_id"], s["base"], s["post"], float(s["tau_bader"])) for s in self.out["selected"])
        want = sorted((m, b, q, t) for m in MATERIALS for b in BASES for q in posts for t in TAUS)
        self.assertEqual(got, want)

    def test_hartree_only_is_best_hartree_row(self):
        rows = self.out["rows"]
        for s in self.out["selected"]:
            if s["post"] != rj.HARTREE_ONLY:
                continue
            cand = [r for r in rows if r["material_id"] == s["material_id"] and r["base"] == s["base"]
                    and r["post"] == "none" and r["hartree_pass"] == "True"]
            self.assertEqual(s["certified"] == "True", bool(cand))
            if cand:
                best = max(cand, key=lambda r: float(r["compression_ratio"]))
                self.assertEqual(s["param"], best["param"])
                self.assertEqual(s["stored"], "U")
                self.assertEqual(float(s["compression_ratio"]), float(best["compression_ratio"]))
                self.assertLess(float(best["hartree_hist"]), rj.TAU_H)
                self.assertLess(float(best["hartree_safe"]), rj.TAU_H)
                self.assertEqual(int(best["extra_bytes"]), 0)
        # every hartree_only row is certified for some base (J reaches the certificate on smooth fields)
        self.assertTrue(any(s["certified"] == "True" for s in self.out["selected"]
                            if s["post"] == rj.HARTREE_ONLY and s["base"] == "J"))

    def test_joint_never_beats_hartree_only_without_side_channel(self):
        sel = {(s["material_id"], s["base"], s["post"], s["tau_bader"]): s for s in self.out["selected"]}
        for (m, b, q, t), s in sel.items():
            if q == "none" and s["certified"] == "True":
                ho = sel[(m, b, rj.HARTREE_ONLY, t)]
                self.assertGreaterEqual(float(ho["compression_ratio"]), float(s["compression_ratio"]))

    def test_tau_bader_semantics(self):
        for b in self.out["bader"]:
            tau = float(b["tau_bader"])
            bu, ru = float(b["unprojected_bader_error_e"]), float(b["unprojected_reassigned_frac"])
            ok_u = bu <= tau and ru == 0.0
            if b["post"].startswith("ctp-"):
                self.assertEqual(b["ctp_decision"], "unprojected" if ok_u else "projected")
                if b["stored"] == "U":
                    self.assertEqual(b["certified"] == "True", ok_u)
                elif ok_u:
                    self.assertEqual(b["certified"], "False")
            else:
                self.assertEqual(b["ctp_decision"] or "", "")
            if b["certified"] == "True":
                self.assertLessEqual(float(b["bader_error_e"]), tau)
                self.assertEqual(float(b["reassigned_frac"]), 0.0)
        # non-CTP: a stricter tau_B never selects a larger CR
        sel = {(s["material_id"], s["base"], s["post"], float(s["tau_bader"])): s for s in self.out["selected"]}
        for (m, b, q, t), s in sel.items():
            if q.startswith("ctp-") or q == rj.HARTREE_ONLY or s["certified"] != "True":
                continue
            for t2 in TAUS:
                if t2 > t:
                    loose = sel[(m, b, q, t2)]
                    self.assertEqual(loose["certified"], "True")
                    self.assertGreaterEqual(float(loose["compression_ratio"]), float(s["compression_ratio"]))

    def test_ctp_decisions_depend_on_tau(self):
        dec = {}
        for b in self.out["bader"]:
            if b["post"].startswith("ctp-"):
                dec.setdefault((b["material_id"], b["base"], b["param"]), set()).add(b["ctp_decision"])
        self.assertTrue(any(len(v) == 2 for v in dec.values()), "fixture should exercise a tau-dependent CTP decision")

    def test_decodes_and_bader_solves_reused_across_tau(self):
        # one decode per candidate for the Hartree metrics; verification decodes only for new Bader solves
        mats = self.out["materials"]
        n_cand = sum(len({r["param"] for r in self.out["rows"] if r["material_id"] == m["material_id"]
                          and r["base"] == b}) for m in mats for b in BASES)
        redecode = sum(int(m["decodes_for_bader"]) for m in mats)
        solves = sum(int(m["bader_solves"]) - 1 for m in mats)
        self.assertEqual(sum(self.decode_calls.values()), n_cand + redecode)
        self.assertLessEqual(redecode, solves)
        keys = {(b["material_id"], b["base"], b["param"], k) for b in self.out["bader"]
                for k in ({"U", b["stored"]} if b["bader_error_e"] not in ("", "nan") else {"U"})}
        self.assertEqual(solves, len(keys))
        self.assertEqual(StubSolver.solves, solves + len(mats))
        self.assertTrue(all(m["tau_bader"] == "0.001 0.0001 1e-05" for m in mats))

    # -- aggregator -----------------------------------------------------------------------------------------

    def test_summary_structure(self):
        s = self.summary
        self.assertEqual(s["status"], "COMPLETE")
        self.assertEqual(s["tau_bader"], ["0.001", "0.0001", "1e-05"])
        self.assertEqual(s["posts"], [rj.HARTREE_ONLY] + rj.post_names(MUS))
        self.assertNotIn("gate", json.dumps(s).lower())
        for t in s["tau_bader"]:
            bt = s["by_tau"][t]
            self.assertEqual(set(bt["by_base_post"]), set(BASES))
            self.assertEqual(bt["focus_vs_others"]["base"], "R3")
            self.assertEqual(set(bt["focus_vs_others"]["same_post"]), set(rj.post_names(MUS)))
            for b in BASES:
                e = bt["by_base_post"][b]
                self.assertNotIn("joint_overhead", e[rj.HARTREE_ONLY])
                self.assertIn("ctp_projected_fraction", e["ctp-uniform"])
                self.assertIn("hap_over_uniform_hartree", e[f"hap:{MUS[0]:g}"])
                self.assertIn("hap_over_uniform_hartree", e[f"ctp-hap:{MUS[0]:g}"])

    def test_aggregate_values_match_selected(self):
        import pandas as pd
        M = pd.read_csv(self.agg / "joint_v2_material.csv", dtype={"tau_bader": str})
        self.assertEqual(len(M), len(MATERIALS) * len(BASES) * (1 + len(rj.post_names(MUS))) * len(TAUS))
        sel = {(s["material_id"], s["base"], s["post"], f"{float(s['tau_bader']):g}"): s for s in self.out["selected"]}
        for t in self.summary["tau_bader"]:
            for b in BASES:
                for q in [rj.HARTREE_ONLY] + rj.post_names(MUS):
                    cr = [float(sel[(m, b, q, t)]["compression_ratio"]) for m in MATERIALS
                          if sel[(m, b, q, t)]["certified"] == "True"]
                    e = self.summary["by_tau"][t]["by_base_post"][b][q]
                    self.assertEqual(e["n_certified"], len(cr))
                    if cr:
                        self.assertAlmostEqual(e["median_cr"], float(np.median(cr)), places=9)
                    else:
                        self.assertIsNone(e["median_cr"])
                    if q != rj.HARTREE_ONLY:
                        ov = [float(sel[(m, b, rj.HARTREE_ONLY, t)]["compression_ratio"])
                              / float(sel[(m, b, q, t)]["compression_ratio"]) for m in MATERIALS
                              if sel[(m, b, q, t)]["certified"] == "True"
                              and sel[(m, b, rj.HARTREE_ONLY, t)]["certified"] == "True"]
                        self.assertEqual(e["joint_overhead"]["n"], len(ov))
                        if ov:
                            self.assertAlmostEqual(e["joint_overhead"]["median"], float(np.median(ov)), places=9)
                    if q.startswith("ctp-"):
                        dec = [sel[(m, b, q, t)]["ctp_decision"] for m in MATERIALS
                               if sel[(m, b, q, t)]["certified"] == "True"]
                        f = e["ctp_projected_fraction"]["selected"]
                        self.assertEqual(f["n"], len(dec))
                        if dec:
                            self.assertAlmostEqual(f["fraction"], dec.count("projected") / len(dec))

    def test_focus_ratio_best_post(self):
        import pandas as pd
        B = pd.read_csv(self.agg / "joint_v2_best_post.csv", dtype={"tau_bader": str, "best_joint_post": str})
        joint = rj.post_names(MUS)
        sel = {(s["material_id"], s["base"], s["post"], f"{float(s['tau_bader']):g}"): s for s in self.out["selected"]}

        def best(m, b, t):
            c = [float(sel[(m, b, q, t)]["compression_ratio"]) for q in joint if sel[(m, b, q, t)]["certified"] == "True"]
            return max(c) if c else math.nan

        for t in self.summary["tau_bader"]:
            want = []
            for m in MATERIALS:
                r3 = best(m, "R3", t)
                other = [best(m, b, t) for b in BASES if b != "R3"]
                other = [x for x in other if not math.isnan(x)]
                if not math.isnan(r3):
                    want.append(r3 / max(other) if other else math.inf)
                row = B[(B["material_id"] == m) & (B["base"] == "R3") & (B["tau_bader"] == t)].iloc[0]
                if math.isnan(r3):
                    self.assertTrue(math.isnan(row["best_joint_cr"]))
                else:
                    self.assertAlmostEqual(row["best_joint_cr"], r3)
            got = self.summary["by_tau"][t]["focus_vs_others"]["best_post"]
            self.assertEqual(got["n"], len(want))
            self.assertEqual(got["n_sole_certifier"], sum(math.isinf(x) for x in want))
            if want:
                med = float(np.median([x if math.isfinite(x) else ag.SOLE_CERTIFIER_RATIO for x in want]))
                self.assertAlmostEqual(got["median"], med)

    def test_hap_over_uniform_ratio(self):
        import pandas as pd
        M = pd.read_csv(self.agg / "joint_v2_material.csv", dtype={"tau_bader": str, "stored": str, "post": str})
        uni = {(r["material_id"], r["base"], r["param"]): float(r["hartree_hist"]) for r in self.out["rows"]
               if r["stored"] == "uniform"}
        hap = M[M["certified"] & M["stored"].fillna("").str.startswith("hap:")]
        self.assertGreater(len(hap), 0, "fixture should certify some HAP rows")
        for _, r in hap.iterrows():
            want = r["hartree_hist"] / uni[(r["material_id"], r["base"], r["param"])]
            self.assertAlmostEqual(r["hap_over_uniform_hartree_hist"], want, places=9)
        self.assertTrue(M.loc[~M.index.isin(hap.index), "hap_over_uniform_hartree_hist"].isna().all())

    def test_runtime_reported(self):
        secs = [float(m["seconds"]) for m in self.out["materials"]]
        print(f"\n[test_runner_v2] {len(secs)} fabricated materials {SHAPE} ({np.prod(SHAPE)} points), "
              f"bases {BASES}, {len(MUS)} mu, {len(TAUS)} tau_B: per material {np.mean(secs):.1f} s "
              f"(wall {self.wall:.1f} s); roundtrips {self.core.calls}; decodes {self.decode_calls}; "
              f"stub Bader solves {StubSolver.solves}", file=sys.stderr)
        self.assertTrue(all(s > 0 for s in secs))


if __name__ == "__main__":
    unittest.main()
