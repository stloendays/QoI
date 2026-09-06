from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "submission/JCTC_MANUSCRIPT_v0.2.2.md"
out = ROOT / "submission/JCTC_MANUSCRIPT_v0.2.3.md"
text = src.read_text(encoding="utf-8")
text = text.replace("JCTC Article submission draft v0.2.2", "JCTC Article submission draft v0.2.3", 1)

# Renumber figures to follow first appearance in the seven-section narrative:
# old Fig.5 (codec error structure) -> new Fig.2
# old Fig.2 (fixed vs re-derived chemical fidelity) -> new Fig.3
# old Fig.4 (resolvability) -> new Fig.4
# old Fig.3 (mechanism) -> new Fig.5
# old Fig.6 (frontier) -> new Fig.6
repls = {
    "Fig. 5a": "@@OLD5A@@",
    "Fig. 5b": "@@OLD5B@@",
    "Fig. 5c": "@@OLD5C@@",
    "Fig. 2a": "@@OLD2A@@",
    "Fig. 2b": "@@OLD2B@@",
    "Fig. 2c": "@@OLD2C@@",
    "Fig. 3a": "@@OLD3A@@",
    "Fig. 3b": "@@OLD3B@@",
    "Fig. 3c": "@@OLD3C@@",
    "Fig. 3d": "@@OLD3D@@",
}
for a,b in repls.items():
    text = text.replace(a,b)
final = {
    "@@OLD5A@@": "Fig. 2a",
    "@@OLD5B@@": "Fig. 2b",
    "@@OLD5C@@": "Fig. 2c",
    "@@OLD2A@@": "Fig. 3a",
    "@@OLD2B@@": "Fig. 3b",
    "@@OLD2C@@": "Fig. 3c",
    "@@OLD3A@@": "Fig. 5a",
    "@@OLD3B@@": "Fig. 5b",
    "@@OLD3C@@": "Fig. 5c",
    "@@OLD3D@@": "Fig. 5d",
}
for a,b in final.items():
    text = text.replace(a,b)

out.write_text(text, encoding="utf-8")
print(f"Built {out.relative_to(ROOT)}")
