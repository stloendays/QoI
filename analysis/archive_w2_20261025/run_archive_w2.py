#!/usr/bin/env python3
"""Whole-object Hartree archive under the W2 writer: V (total density by W2S, magnetization by W2M) and, for
attribution, VP (W2S density, magnetization by the pointwise policy on the same decoded partition).

Frame, sample, storage rule, moment contract and estimators are those of the truncation/operational-optimum study
(`analysis/archive_truncation_20261024/`) and the W1 archive (`analysis/archive_waterfill_20261025/`). Per object and
per tau_H in {1e-6, 1e-4}:

1. if the object is Hartree-eligible at tau_H (archive-law record), write the total density with `w2.search_w2`
   (symmetry; the smallest of no prediction, prediction on every gated shell, prediction on the written gated shells)
   and verify the decoded Hartree certificate;
2. derive the Bader partition of this tau's decoded density with the compiled binary, under a partition id unique to
   the tau (the partition field is rewritten for every decoded density; see DEVIATIONS of
   `analysis/archive_partition_fix_20261025/`);
3. magnetization, if moment-eligible (QSQ floor < tau_mu): W2M (`w2.search_m` on that partition, final check by the
   binary) and the pointwise policy (`run_archive_truncation.certify_m` logic: best of ZFP/SZ3/SPERR, final check by the
   binary), both against the reference moments at tau_mu = 1e-2 mu_B;
4. record stored bytes: rho stream (lossless rho if not eligible or not certified) plus the magnetization stream
   (W2M or pointwise where it certifies, otherwise the reference atom map plus the reference-frame m of S2). When the
   density is stored losslessly, the W2M sub-stream is charged the 84 bytes of grid shape and lattice it would
   otherwise take from the density stream.

Also recorded per object: the Porod exponent of the decoded partition at 1e-6 (descriptive), the W2M symmetry, the
SFP shells and the W2S variant. Checkpoint per object: checkpoints/<task_id>.json.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import time
import traceback
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
AN = HERE.parent
sys.path.insert(0, str(AN / "sfp_spin_writer_20261025"))
import w2  # noqa: E402

w1 = w2.w1
_spec = importlib.util.spec_from_file_location("run_archive_truncation", AN / "archive_truncation_20261024" /
                                               "run_archive_truncation.py")
RAT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RAT)

TAUS_H = RAT.TAUS_H
TAU_MU = RAT.TAU_MU
tkey = RAT.tkey
SHAPE_LAT_BYTES = 12 + 72


def structure_of(d):
    from pymatgen.core import Lattice, Structure
    return Structure(Lattice(d["lattice"]), d["symbols"], d["frac"])


def pointwise_m(S, B, m, rec_r, mu_ref, natoms, lossless_m, work, pid):
    """The pointwise moment policy of run_archive_truncation.certify_m on the partition `pid` of rec_r."""
    s1, core, m_search = S["s1"], S["core"], S["m_search"]
    _, atom_d = B(m, rec_r, pid)
    ptp_m = float(np.ptp(m)) or 1.0
    cands = []
    for c in s1.CODECS:
        b = m_search(c, m, ptp_m, lambda r: float(np.max(np.abs(s1.sums(r, atom_d, natoms) - mu_ref))) < TAU_MU,
                     core, work)
        if b is not None:
            cands.append((b[0], c, b[1]))
    for nb, c, rec in sorted(cands, key=lambda z: z[0]):
        if nb >= lossless_m:
            break
        mu_j, _ = B(rec, rec_r, pid)
        ej = float(np.max(np.abs(mu_j - mu_ref)))
        if ej < TAU_MU:
            return nb, c, ej
    return None, "no certified point", None


def process(row: dict, blob_path: Path, S: dict, bader: Path) -> dict:
    s1, RC, v02 = S["s1"], S["RC"], S["v02"]
    t0 = time.time()
    out = {"task_id": row["task_id"], "stratum": row["stratum"], "status": "SUCCESS", "error": "", "results": {}}
    try:
        blob = blob_path.read_bytes()
        if len(blob) != int(row["frame_bytes"]):
            raise RuntimeError("size mismatch against the frame")
        out["input_sha256"] = hashlib.sha256(blob).hexdigest()
        d = s1.decode(blob)
        del blob
        rho, m = d["rho"], d["m"]
        lat, natoms = d["lattice"], len(d["symbols"])
        out.update(npoints=int(rho.size), natoms=natoms, lossless_rho=int(row["lossless_bytes"]),
                   lossless_m=len(zlib.compress(m.tobytes(), 6)))
        rh, rs = v02.reference_hartree_rms(rho, lat)
        ptp = float(np.ptp(rho))
        ptp_m = float(np.ptp(m)) or 1.0

        def certify(rec):
            return RC.certify(rec, rho, lat, rh, rs)

        F = info = Fm = None
        with tempfile.TemporaryDirectory(prefix="arch_w2_") as td:
            work = Path(td) / "codec"
            work.mkdir()
            B = s1.Bader(bader, lat, d["frac"], d["symbols"], rho.shape, Path(td))
            mu_ref, _ = B(m, rho, "ref")
            e_r, e_m = s1.f32_eps(rho), s1.f32_eps(m)
            floor = 0.0
            for s in s1.SEEDS:
                rng = np.random.default_rng(s)
                mu_p, _ = B(m + rng.uniform(-e_m, e_m, m.shape), rho + rng.uniform(-e_r, e_r, rho.shape), f"p{s}")
                floor = max(floor, float(np.max(np.abs(mu_p - mu_ref))))
            out["floor_muB"] = floor
            for tau in TAUS_H:
                k = tkey(tau)
                pid = f"dec-V-{k}"
                eligible = str(row[f"eligible_{k}"]) == "True"
                ts = time.time()
                r = {"eligible": eligible, "certified": False, "rho_bytes": out["lossless_rho"], "param": "",
                     "variant": "", "w1s_rho_bytes": None}
                rec_r = rho
                if eligible:
                    if F is None:
                        F = w1.prepare(rho, lat, rh, structure_of(d), use_symmetry=True)
                        info = w2.sfp_fit(F, d["symbols"], d["frac"])
                        out["symmetry"] = F.sym_status
                        out["sfp_shells"] = len(info["used"]) if info else 0
                        out["sfp_block_bytes"] = len(w2.sfp_block(info)) if info else 0
                    res = w2.search_w2(F, info, tau, ptp, certify)
                    if res is not None:
                        r.update(certified=True, rho_bytes=int(res["bytes"]), param=res["param"],
                                 variant=res["variant"], sfp_shells_used=res["sfp_shells"],
                                 hartree_hist=float(res["hartree_hist"]), hartree_safe=float(res["hartree_safe"]),
                                 w1s_rho_bytes=res.get("none_bytes"))
                        rec_r = res["rec"]
                r["rho_seconds"] = time.time() - ts
                ts = time.time()
                if floor >= TAU_MU:
                    r.update(m_eligible=False, w2m_bytes=None, pw_bytes=None, pw_codec="not eligible")
                else:
                    r["m_eligible"] = True
                    _, atom_d = B(m, rec_r, pid)
                    if Fm is None:
                        rhm, _ = v02.reference_hartree_rms(m, lat)
                        Fm = w1.prepare(m, lat, max(rhm, 1e-300), structure_of(d), use_symmetry=True)
                        out["m_symmetry"] = Fm.sym_status
                    if "porod_exponent" not in out:
                        out["porod_exponent"] = w2.porod_exponent(atom_d, natoms, lat)
                    rm = w2.search_m(Fm, m.shape, lat, atom_d, natoms, mu_ref, TAU_MU, ptp_m,
                                     final_check=lambda rec: float(np.max(np.abs(B(rec, rec_r, pid)[0] - mu_ref))))
                    if rm is not None:
                        extra = 0 if r["certified"] else SHAPE_LAT_BYTES
                        r.update(w2m_bytes=int(rm["bytes"]) + extra, w2m_err_partition=rm["err_partition"],
                                 w2m_err_binary=rm["err_final"], w2m_shells=rm["shells_written"],
                                 w2m_alpha_rel=rm["alpha_rel"])
                    else:
                        r["w2m_bytes"] = None
                    r["w2m_seconds"] = time.time() - ts
                    ts = time.time()
                    nb, codec, err = pointwise_m(S, B, m, rec_r, mu_ref, natoms, out["lossless_m"], work, pid)
                    r.update(pw_bytes=nb, pw_codec=codec, pw_err_binary=err, pw_seconds=time.time() - ts)
                # the archive record format: V and VP as writers
                out["results"][f"V_{k}"] = dict(r, m_decframe_bytes=r.get("w2m_bytes"), m_codec="w2m")
                out["results"][f"VP_{k}"] = dict(r, m_decframe_bytes=r.get("pw_bytes"), m_codec=r.get("pw_codec"))
                print("ARCHW2", row["task_id"], k, r["certified"], r["rho_bytes"], r.get("variant"), r.get("w2m_bytes"),
                      r.get("pw_bytes"), flush=True)
    except Exception as e:  # noqa: BLE001
        out.update(status="FAILED", error=f"{type(e).__name__}: {e}"[:500], traceback=traceback.format_exc()[-2000:])
    out["wall_seconds"] = time.time() - t0
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--inputs", type=Path, required=True, help="prefetched <task_id>.json.gz")
    ap.add_argument("--checkpoints", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--frozen-root", type=Path, required=True)
    ap.add_argument("--bader", type=Path, required=True)
    a = ap.parse_args(argv)
    rows = {x["task_id"]: x for x in RAT._read(a.repo_root / "analysis" / "scope_expansion_20261022" /
                                                 "archive_hartree_objects.csv")}
    row = rows[a.task_id]
    a.checkpoints.mkdir(parents=True, exist_ok=True)
    ck = a.checkpoints / f"{a.task_id}.json"
    if ck.exists() and json.loads(ck.read_text(encoding="utf-8")).get("status") == "SUCCESS":
        print("SKIP complete", a.task_id)
        return 0
    S = RAT.load_stack(a.repo_root.resolve(), a.frozen_root.resolve())
    rec = process(row, a.inputs / f"{a.task_id}.json.gz", S, a.bader)
    tmp = ck.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=float) + "\n", encoding="utf-8")
    os.replace(tmp, ck)
    print("DONE", a.task_id, rec["status"], rec.get("error", ""))
    return 0 if rec["status"] == "SUCCESS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
