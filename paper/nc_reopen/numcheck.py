"""Number-provenance sweep: every number in the manuscript (outside references) must occur in a committed source."""
import glob
import json
import re
import subprocess
import sys

ROOT = sys.argv[1]
ms = open(f"{ROOT}/paper/MANUSCRIPT.md", encoding="utf-8").read()
ms_body = ms.split("## References")[0] + ms.split("## Figure legends")[1]

srcs = []
for pat in ["analysis/general_qoac_law/results/**/*.md", "analysis/general_qoac_law/results/**/*.json",
            "analysis/qoac_hb_v2/results/**/*.md", "analysis/qoac_hb_v2/results/**/*.json",
            "analysis/qoac_b3_design/results/**/*.md", "analysis/fresh_population_20261006/*.md",
            "analysis/general_qoac_operators/results/*.md", "analysis/qoac_v03_rdo/results/*.md",
            "analysis/qoac_h_strong_baselines/results/*.md", "analysis/hartree_baselines_mgard_qpet_20261007/RESULTS.md", "analysis/p3b_vacuum_level_20261007/RESULTS.md", "analysis/p3b_vacuum_level_20261007/results/summary.csv", "analysis/p3b_vacuum_level_20261007/PROTOCOL.md", "analysis/hartree_baselines_mgard_qpet_20261007/PROTOCOL.md", "sync/PROGRAM_STATUS_20261007.md",
            "paper/program_draft/v2/*.md", "paper/FIGURE_CAPTIONS.md", "analysis/general_qoac_law/DESIGN.md",
            "analysis/qoac_v03_rdo/DESIGN.md", "analysis/qoac_hb_v2/DESIGN.md",
            "analysis/fresh_population_20261006/P3B_SELECTION_RULE.md", "figures/nc/fig4/KCN_STATS.json",
            "figures/nc/fig4/data/kcn_law.json", "figures/nc/fig6/LADDER_STATS.json", "figures/nc/fig7/POST_COUNTS.json",
            "analysis/qoac_hb_v2/results/**/*.md"]:
    for f in glob.glob(f"{ROOT}/{pat}", recursive=True):
        srcs.append(open(f, encoding="utf-8", errors="ignore").read())
frozen = subprocess.run(["git", "-C", ROOT, "show", "efd1e2c:paper/MANUSCRIPT.md"], capture_output=True, text=True,
                        encoding="utf-8").stdout
frozen_si = subprocess.run(["git", "-C", ROOT, "show", "efd1e2c:paper/SUPPLEMENTARY_INFORMATION.md"],
                           capture_output=True, text=True, encoding="utf-8").stdout
corpus = "\n".join(srcs) + frozen + frozen_si

# json numbers rounded variants
extra = set()
for f in glob.glob(f"{ROOT}/analysis/**/results/**/*.json", recursive=True) + glob.glob(f"{ROOT}/figures/nc/**/*.json", recursive=True):
    try:
        txt = open(f, encoding="utf-8").read()
    except Exception:
        continue
    for x in re.findall(r"-?\d+\.\d+(?:e-?\d+)?", txt):
        v = float(x)
        for d in (0, 1, 2, 3, 4):
            extra.add(f"{v:.{d}f}")
nums = set(re.findall(r"(?<![\w.])\d[\d,]*\.\d+|\d+/\d+|(?<![\w.^{-])\d{2,}(?:,\d{3})*(?![\w.])", ms_body))
missing = []
for n in sorted(nums):
    if n in corpus or n in extra or n.replace(",", "") in corpus or n.replace(",", "") in extra:
        continue
    missing.append(n)
print(len(nums), "numbers checked;", len(missing), "not found verbatim:")
print(" ".join(missing))
