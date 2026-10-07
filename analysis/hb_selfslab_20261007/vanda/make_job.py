#!/usr/bin/env python3
"""Fill job_bundle.pbs.template for one bundle. Usage: make_job.py <bundle> <ncpus> <mem> <dir> [<dir> ...]"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
bundle, ncpus, mem, dirs = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
t = (HERE / "job_bundle.pbs.template").read_text(encoding="utf-8")
t = t.replace("@BUNDLE@", bundle).replace("@NCPUS@", ncpus).replace("@MEM@", mem).replace("@MATERIALS@", " ".join(dirs))
(HERE / "jobs").mkdir(exist_ok=True)
(HERE / "jobs" / f"{bundle}.pbs").write_text(t, encoding="utf-8", newline="\n")
print(HERE / "jobs" / f"{bundle}.pbs")
