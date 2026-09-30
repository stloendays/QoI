"""WP-G frame check: are AECCAR0/AECCAR2 published for each development MP task id? (HEAD only)"""
import csv, re, urllib.request, json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent; REPO = HERE.parents[2]
rows = [r for r in csv.DictReader(open(REPO / "materials_metadata.csv", encoding="utf-8")) if r["corpus"] == "dev_bulk"]
def head(url):
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=60) as r:
            return int(r.headers.get("Content-Length", -1))
    except Exception:
        return None
def check(r):
    tid = re.search(r"chgcars/(mp-\d+)\.json\.gz", r["url"]).group(1)
    base = "https://materialsproject-parsed.s3.amazonaws.com/"
    a0 = head(base + "aeccar0s/%s.json.gz" % tid); a2 = head(base + "aeccar2s/%s.json.gz" % tid)
    return dict(material_id=r["material_id"], task_id=tid, chgcar_bytes=r["source_bytes"], aeccar0_bytes=a0 or "", aeccar2_bytes=a2 or "",
                both=int(bool(a0) and bool(a2)))
with ThreadPoolExecutor(16) as ex:
    out = list(ex.map(check, rows))
w = csv.DictWriter(open(HERE / "aeccar_availability.csv", "w", newline="", encoding="utf-8"), fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print(json.dumps(dict(dev_bulk=len(out), both=sum(o["both"] for o in out),
      aeccar_GB=round(sum(int(o["aeccar0_bytes"] or 0) + int(o["aeccar2_bytes"] or 0) for o in out) / 1e9, 2))))
