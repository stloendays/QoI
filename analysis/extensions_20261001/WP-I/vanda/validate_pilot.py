#!/usr/bin/env python3
"""Pre-production checks for WP-I after the three-material pilot."""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CK = HERE / "results" / "checkpoints"
PILOT = ("mp-214", "mp-1065204", "mp-30772")

def main():
    for mid in PILOT:
        p = CK / (mid + ".json")
        if not p.exists():
            raise SystemExit("missing pilot checkpoint: %s" % mid)
        d = json.loads(p.read_text())
        if d.get("status") != "SUCCESS":
            raise SystemExit("pilot failure %s: %s" % (mid, d.get("error")))
        probes = d.get("probes", [])
        if len(probes) != 5:
            raise SystemExit("%s has %d probes, expected 5" % (mid, len(probes)))
        if d.get("bader_solves") != 6:
            raise SystemExit("%s uses %r Bader solves, expected 6" % (mid, d.get("bader_solves")))
        if d.get("g3_floor_e") != max(x["g3_response_e"] for x in probes):
            raise SystemExit("%s floor/probe mismatch" % mid)
        if not all(0.0 <= x["g3_reassigned_frac"] <= 1.0 for x in probes):
            raise SystemExit("%s invalid reassignment fraction" % mid)
    print("WP-I PILOT_VALIDATED", len(PILOT))

if __name__ == "__main__":
    main()
