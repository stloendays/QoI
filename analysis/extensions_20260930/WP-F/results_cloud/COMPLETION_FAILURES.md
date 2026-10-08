# WP-F completion phase: the 12 cloud failures (run 37632960406)

Each of these jobs ended without returning a checkpoint, so the collect job recorded the object as FAILED (stage `worker`, `NoArtifact`; DEVIATIONS.md 8). No artifact was uploaded for any of them, so no `memory.log`, `oom.txt` or `run.log` exists in `completion_logs/` for these objects; the cause below is GitHub's job record (job annotations and step log). Final under DEVIATIONS.md 7-8 and counted under the storage rule.

| object | stratum | json.gz (MB) | job id | steps run | run step duration in the job record (min) | cause (GitHub job record) |
|---|---|---:|---:|---:|---:|---|
| mp-1825100 | D09 | 32.6 | 112831833865 | 11 | 154.5 | runner received a shutdown signal during run_wpf.py (step exit 143) |
| mp-1826245 | D09 | 29.8 | 112831834104 | 0 | 0 (not started) | never started: no runner acquired (5 attempts) |
| mp-2019659 | D09 | 38.5 | 112831833896 | 11 | 278.5 | runner received a shutdown signal during run_wpf.py (step exit 143) |
| mp-2045979 | D09 | 40.2 | 112831834144 | 11 | 246.8 | hosted runner lost communication with the server during run_wpf.py |
| mp-2046569 | D09 | 40.0 | 112831833946 | 0 | 0 (not started) | never started: no runner acquired (5 attempts) |
| mp-2234070 | D09 | 32.6 | 112831834023 | 0 | 0 (not started) | never started: no runner acquired (5 attempts) |
| mp-2490962 | D09 | 39.3 | 112831834014 | 11 | 114.5 | hosted runner lost communication with the server during run_wpf.py |
| mp-3092553 | D09 | 33.6 | 112831834017 | 0 | 0 (not started) | never started: no runner acquired (5 attempts) |
| mp-3150861 | D09 | 40.6 | 112831833760 | 10 | 348.8 | hosted runner lost communication with the server during run_wpf.py |
| mp-1543577 | D10a | 52.2 | 112831834355 | 0 | 0 (not started) | never started: no runner acquired (5 attempts) |
| mp-1920806 | D10a | 53.5 | 112831833759 | 11 | 252.8 | runner received a shutdown signal during run_wpf.py (step exit 143) |
| mp-2355832 | D10b | 86.6 | 112831833602 | 0 | 0 (not started) | never started: no runner acquired (5 attempts) |

Counts: hosted runner lost communication with the server during run_wpf.py: 3; never started: no runner acquired (5 attempts): 6; runner received a shutdown signal during run_wpf.py (step exit 143): 3.
