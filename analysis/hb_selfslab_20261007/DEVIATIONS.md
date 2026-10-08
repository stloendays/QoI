# Deviations from PROTOCOL.md

Infrastructure fixes and any departure from the frozen protocol, recorded before the affected step is rerun.

None at freezing (2026-10-08).

## D1 (infrastructure, 2026-10-08 00:33–00:35 SGT): bundle jobs b2 and b3 failed to start 10 and 9 times

Jobs `1439806` (b2) and `1439807` (b3), submitted at 00:33, were started by PBS on CN-117 and CN-112 and ended before
the job script ran (`Exit_status = -10`, no PBS output file, no file written in any run directory), then requeued by PBS
(`run_count` 11 and 10). At 00:34:24 a user hold (`qhold`) was placed on both to stop the cycling, while the 11th and
10th starts on CN-112 succeeded; the jobs were running VASP at 00:35:05 and the holds were released (`qrls`) at 00:35. No
job, input or run was changed, nothing was rerun, and no slab result is affected.
