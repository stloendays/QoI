# WP-I execution

Purpose: isolate sensitivity to the partition-defining all-electron reference.

This package reuses the completed WP-G Vanda/Henkelman environment and inputs. It does not rerun codec ladders.

Per analyzable material:
- 1 exact CHGCAR + exact AE reference solve;
- 5 solves with exact CHGCAR and only AE reference perturbed;
- 6 Bader solves total.

Expected analyzable denominator is 50/53 because the same three published AECCAR0 inputs were entirely non-finite in WP-G.

Run from the WP-I Vanda directory after copying/linking the already verified WP-G `frozen/`, `reference_source/`, and `inputs/` directories or making the relative WP-G paths available.

After all 53 checkpoint records exist, copy the checkpoint directory back to `analysis/extensions_20261001/WP-I/vanda/results/checkpoints/` and run `analyze_wpi.py`.
