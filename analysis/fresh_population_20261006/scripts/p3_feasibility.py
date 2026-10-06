"""Metadata-only feasibility of P3 (72 slab strata) on the frozen NOMAD frame.

No candidate file is downloaded. Counts eligible frame rows per size stratum
under the frozen rule, and under the rule without the upload exclusion.

Usage: p3_feasibility.py <out_dir>
"""
from __future__ import annotations

import csv
import gzip
import json
import sys
from pathlib import Path

MB = 10**6
K = 72


def main() -> int:
    out = Path(sys.argv[1])
    with (out / "exclusion_ids.csv").open(newline="", encoding="utf-8") as f:
        ids = {r["id"] for r in csv.DictReader(f)}
    with (out / "exclusion_formulas.csv").open(newline="", encoding="utf-8") as f:
        fx = {r["reduced_formula"] for r in csv.DictReader(f)}
    with gzip.open(out / "nomad_frame_surface_vasp.csv.gz", "rt", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    excl_up = {r["upload_id"] for r in rows
               if r["entry_id"] in ids or "nomad-" + r["entry_id"][:12] in ids}
    frame = sorted((int(r["chgcar_bytes"]), r["entry_id"], r) for r in rows
                   if MB <= int(r["chgcar_bytes"]) <= 80 * MB)
    n = len(frame)

    def scenario(use_upload: bool) -> dict:
        per, formulas, uploads, total = [], set(), set(), 0
        for k in range(K):
            s = frame[(k * n) // K:((k + 1) * n) // K]
            e = [r for _, _, r in s
                 if r["entry_id"] not in ids and "nomad-" + r["entry_id"][:12] not in ids
                 and r["reduced_formula"] not in fx
                 and not (use_upload and r["upload_id"] in excl_up)]
            per.append(len(e))
            total += len(e)
            formulas |= {r["reduced_formula"] for r in e}
            uploads |= {r["upload_id"] for r in e}
        return {"eligible_rows": total, "eligible_per_stratum": per,
                "strata_with_zero_eligible": sum(1 for x in per if x == 0),
                "distinct_eligible_reduced_formulas": len(formulas),
                "distinct_eligible_uploads": len(uploads),
                "max_acceptable_materials_upper_bound": min(K - sum(1 for x in per if x == 0),
                                                            len(formulas))}

    res = {
        "frame_rows": len(rows), "frame_rows_1_to_80_MB": n, "strata": K,
        "excluded_uploads": sorted(excl_up),
        "frame_rows_in_excluded_uploads": sum(1 for _, _, r in frame if r["upload_id"] in excl_up),
        "frozen_rule": scenario(True),
        "without_upload_exclusion": scenario(False),
        "required_materials": 72,
    }
    (out / "p3_feasibility.json").write_text(json.dumps(res, indent=2))
    print(json.dumps({k: v for k, v in res.items() if k != "excluded_uploads"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
