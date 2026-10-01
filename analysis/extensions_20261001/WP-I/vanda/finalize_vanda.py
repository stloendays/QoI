#!/usr/bin/env python3
"""Validate the completed Vanda checkpoint package before copying it back."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parent
CK = ROOT / "results" / "checkpoints"
ids = [x.strip() for x in (ROOT/"material_ids.txt").read_text().splitlines() if x.strip()]
expected_wp_g_failures = {"mp-1192831", "mp-1193567", "mp-776331"}
assert len(ids) == 53
files = [CK/(m+".json") for m in ids]
missing = [p.stem for p in files if not p.exists()]
if missing:
    raise SystemExit("missing checkpoints: " + ",".join(missing))
records = {p.stem: json.loads(p.read_text()) for p in files}
success = {m for m,d in records.items() if d.get("status") == "SUCCESS"}
failed = {m for m,d in records.items() if d.get("status") != "SUCCESS"}
if failed != expected_wp_g_failures:
    raise SystemExit("unexpected failure set: %r" % sorted(failed))
for m in success:
    d = records[m]
    if len(d.get("probes", [])) != 5 or d.get("bader_solves") != 6:
        raise SystemExit("invalid completed record %s" % m)
sha = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(ROOT/"CHECKPOINT_SHA256.json").write_text(json.dumps(sha, indent=1))
(ROOT/"FINALIZED").touch()
print("WP-I FINALIZED success=%d failed=%d" % (len(success), len(failed)))
