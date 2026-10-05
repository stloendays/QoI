# WP-I — Partition-reference-only sensitivity decomposition

Purpose: isolate sensitivity to the partition-defining all-electron reference while keeping CHGCAR exact.

The scientific protocol and acceptance criteria are frozen in `analysis/extensions_20261001/QSQ_OPTIMIZATION_PROTOCOL.md`.

## Vanda execution

The Vanda package is self-contained and does not depend on the deleted WP-G scratch directory.

From a checkout of branch `ext/QSQ-optimization-20261001` on the Vanda login node:

```bash
cd /path/to/QoI
git switch ext/QSQ-optimization-20261001
git pull
bash analysis/extensions_20261001/WP-I/vanda/prepare_stage.sh "$PWD"
cd /scratch/junbotong/qoi-wpi-20261001
bash submit_pipeline.sh
```

`prepare_stage.sh`:
- reconstructs the exact decoder/runtime used by the frozen study;
- builds the same Henkelman Bader 1.05 implementation used by WP-G;
- copies the completed WP-G G1/G2 reference table;
- downloads and SHA-verifies the 53 CHGCAR/AECCAR input sets;
- creates the self-contained stage at `/scratch/junbotong/qoi-wpi-20261001`.

`submit_pipeline.sh` submits three PBS jobs with dependencies:

1. **pilot** — three representative analyzable materials;
2. **production** — all 53 materials, up to 34 concurrent workers;
3. **finalize** — verifies all 53 checkpoints, requires exactly the three previously documented non-finite AECCAR failures, writes SHA-256s, and creates `wpi_results.tar.gz`.

Status:

```bash
cd /scratch/junbotong/qoi-wpi-20261001
venv/bin/python status.py
cat submitted_jobs.json
```

## G3 measurement semantics

Per analyzable material:
- exact CHGCAR;
- exact reference solve with AECCAR0+AECCAR2;
- five probes in which only AECCAR0+AECCAR2 is perturbed;
- identical WP-G AE perturbation amplitude and deterministic seed mapping;
- Henkelman Bader 1.05 on-grid, `-vac 0.001`;
- six Bader solves total;
- no codec ladder rerun.

Expected denominator:
- 53 planned materials;
- 50 analyzable under the published AECCAR inputs;
- 3 input failures preserved: `mp-1192831`, `mp-1193567`, `mp-776331`.

No reader-facing mechanism conclusion is allowed until the completed checkpoint package is copied back and `analyze_wpi.py` is run against the pre-declared criteria.
