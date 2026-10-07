"""Word count of paper/MANUSCRIPT.md under the WORD_COUNT.md rule (running text; headings, display math and citation
superscripts excluded; each inline math expression one word; tables counted separately).

    python word_count.py
"""
import os
import re

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "MANUSCRIPT.md")
s = open(P, encoding="utf-8").read()
s = re.sub(r"\$\$.*?\$\$", " ", s, flags=re.S)
s = re.sub(r"<sup>[^<]*</sup>", "", s)
s = re.sub(r"\$[^$]+\$", " MATH ", s)


def words(t):
    t = "\n".join(l for l in t.splitlines() if not l.startswith("|") and not l.startswith("#"))
    t = re.sub(r"\*\*Table 1[^\n]*", "", t)
    return len(re.findall(r"\S+", t.replace("*", "").replace("`", "")))


sec = re.split(r"\n(?=## )", s)
out = {}
for blk in sec:
    name = blk.splitlines()[0].lstrip("# ").strip()
    if name in ("References",):
        continue
    if name == "Results" or name == "Methods":
        for sub in re.split(r"\n(?=### )", blk)[1:]:
            out["%s — %s" % (name, sub.splitlines()[0].lstrip("# ").strip())] = words(sub)
    elif name == "Figure legends":
        for para in [x for x in blk.split("\n\n")[1:] if x.strip()]:
            out["Legend " + re.match(r"\*\*Fig\. (\d)", para).group(1)] = words(para)
    else:
        out[name] = words(blk)
for k, v in out.items():
    print("%-110s %5d" % (k[:110], v))
main = sum(v for k, v in out.items() if k in ("Introduction", "Discussion") or k.startswith("Results"))
meth = sum(v for k, v in out.items() if k.startswith("Methods"))
print("Intro+Results+Discussion", main, "| Methods", meth, "| total", main + meth,
      "| legends", sum(v for k, v in out.items() if k.startswith("Legend")))
