# Local recovery of the final four external E2E systems

This launcher is an orchestration aid only. It does not modify Protocol A.1, the frozen tolerance ladder, codec set, Bader settings, failure semantics, or the scientific implementation.

The scientific checkout is pinned internally to:

`893f931b3045b0b628329db81999c2f439d4e830`

and the environment reproduces the formal GitHub Actions run with Python `3.12.14` plus `validation/requirements-external-e2e.txt`.

## Systems

- recovery slot 03: `aflow-Cl1O12Pb5V3_ICSD_203074`
- recovery slot 09: `aflow-B1C1F6K1_ICSD_1194`
- recovery slot 10: `aflow-B6H2O13Sr3_ICSD_262541`
- recovery slot 16: `aflow-Mo3Na1O16P3_ICSD_66877`

The runner is sequential by default so two topology-heavy Bader cases do not compete for memory. There is no six-hour job timeout.

## Recommended Windows route: WSL2 Ubuntu

Use WSL rather than native Windows so the runtime is as close as practical to the Linux GitHub Actions environment.

### 1. Check/install WSL from Windows PowerShell

```powershell
wsl --status
```

If WSL/Ubuntu is not installed, run PowerShell as Administrator:

```powershell
wsl --install -d Ubuntu-24.04
```

Reboot if Windows requests it, then open Ubuntu.

### 2. Install local prerequisites inside Ubuntu/WSL

```bash
sudo apt update
sudo apt install -y git curl ca-certificates build-essential tmux
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

`uv` is used only to obtain the exact Python patch version. Package installation is still performed by `pip`, matching the formal workflow.

### 3. Clone/update QoI

The repository can be cloned over HTTPS; no SSH deploy key is required for this local run.

```bash
cd ~
if [ ! -d QoI/.git ]; then
  git clone https://github.com/stloendays/QoI.git
fi
cd QoI
git checkout main
git pull --ff-only
```

Confirm the launcher exists:

```bash
ls -l validation/local_final4/run_final4_local.sh
```

### 4. Start the run in tmux

```bash
chmod +x validation/local_final4/run_final4_local.sh
tmux new -s qoi-final4
bash validation/local_final4/run_final4_local.sh
```

Detach from tmux without stopping the calculation with:

`Ctrl+B`, then `D`.

Reattach later with:

```bash
tmux attach -t qoi-final4
```

### 5. Monitor from another WSL terminal

```bash
cat ~/qoi-final4-local/status/*.status 2>/dev/null
```

```bash
tail -f ~/qoi-final4-local/logs/controller.log
```

To inspect the currently running material in more detail:

```bash
ls -lt ~/qoi-final4-local/logs/
tail -100 ~/qoi-final4-local/logs/recovery_*.log
```

## Resume semantics

If Windows reboots, WSL is stopped, the network drops, or one material fails, run the same launcher again:

```bash
cd ~/QoI
bash validation/local_final4/run_final4_local.sh
```

Materials already marked `SUCCESS` are skipped. Failed or interrupted materials are rerun from a clean material output directory. No scientific thresholds or exclusion rules are changed.

## Output layout

All local state is kept outside the Git checkout:

```text
~/qoi-final4-local/
├── frozen_repo/       # detached checkout at the frozen scientific commit
├── venv/              # Python 3.12.14 environment
├── results/
│   ├── recovery_03/
│   ├── recovery_09/
│   ├── recovery_10/
│   └── recovery_16/
├── logs/
├── status/
├── provenance/
└── qoi-final4-local-*.tar.gz
```

Each material output records the requested material, recovery slot, Python version, `pip freeze`, requirements SHA256, and frozen Git commit. A timestamped tarball containing results/logs/status/provenance is generated at the end of each launcher invocation.

## Important local-machine note

Closing the terminal is safe if the job is inside `tmux`, but Windows sleep/hibernate suspends WSL computation. While the run is active, configure Windows not to sleep when plugged in.
