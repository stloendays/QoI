#!/usr/bin/env python3
"""Vanda login node: download CHGCAR (SHA-256 checked against the frozen metadata) and AECCAR0/2 for the 53 WP-G
materials into inputs/, record the AECCAR SHA-256 and write tasks.json. Python 3.9 standard library only."""
import hashlib, json, os, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent; INP = ROOT / "inputs"; INP.mkdir(exist_ok=True)
tasks = json.loads((ROOT / "tasks_base.json").read_text())
def get(url, dest):
    if dest.exists():
        return dest.read_bytes()
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "QoI-QSQ-WPG/1.0"}), timeout=900) as r:
                b = r.read()
            tmp = dest.with_suffix(".part"); tmp.write_bytes(b); os.replace(str(tmp), str(dest)); return b
        except Exception as e:
            err = e; time.sleep(10 * (k + 1))
    raise RuntimeError("download failed %s: %s" % (url, err))
for m, t in sorted(tasks.items()):
    b = get(t["chgcar_url"], INP / ("%s_chgcar.json.gz" % m))
    if hashlib.sha256(b).hexdigest() != t["chgcar_sha256"] or len(b) != t["chgcar_bytes"]:
        raise SystemExit("CHGCAR checksum mismatch for %s" % m)
    for k in ("aeccar0", "aeccar2"):
        t[k + "_sha256"] = hashlib.sha256(get(t[k + "_url"], INP / ("%s_%s.json.gz" % (m, k)))).hexdigest()
    print(m, "ok", flush=True)
(ROOT / "tasks.json").write_text(json.dumps(tasks, indent=1))
(ROOT / "material_ids.txt").write_text("\n".join(sorted(tasks, key=lambda m: -tasks[m]["npoints"])) + "\n")   # largest first
print("tasks.json written:", len(tasks))
