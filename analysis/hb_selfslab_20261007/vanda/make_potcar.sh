#!/usr/bin/env bash
# Assemble POTCAR in each run directory from POTCAR.spec (MPRelaxSet symbols, POSCAR species order) out of the Vanda
# PBE PAW library. POTCARs stay on the server. Writes potcar_headers.tsv (directory, symbol, TITEL, ZVAL) for the record.
# Usage (on Vanda): bash make_potcar.sh <run-dir> [<run-dir> ...]
set -euo pipefail
LIB=/home/svu/junbotong/software/vasp/potpaw_PBE.54
ROOT=/scratch/junbotong/qoi_selfslab_20261007
for d in "$@"; do
  test -s "$d/POTCAR.spec" || { echo "missing $d/POTCAR.spec" >&2; exit 1; }
  species=$(sed -n 6p "$d/POSCAR" | xargs)
  elems=$(sed 's/_.*//' "$d/POTCAR.spec" | xargs)
  [ "$species" = "$elems" ] || { echo "$d: POSCAR species '$species' != POTCAR.spec '$elems'" >&2; exit 1; }
  : > "$d/POTCAR"
  while read -r s; do
    [ -n "$s" ] || continue
    test -s "$LIB/$s/POTCAR" || { echo "$d: $LIB/$s/POTCAR missing" >&2; exit 1; }
    cat "$LIB/$s/POTCAR" >> "$d/POTCAR"
    t=$(grep -m1 "TITEL" "$LIB/$s/POTCAR" | sed 's/.*= *//')
    z=$(grep -m1 "ZVAL" "$LIB/$s/POTCAR" | sed 's/.*ZVAL *= *\([0-9.]*\).*/\1/')
    printf '%s\t%s\t%s\t%s\n' "$(basename "$d")" "$s" "$t" "$z" >> "$ROOT/potcar_headers.tsv"
  done < "$d/POTCAR.spec"
  echo "$(basename "$d") POTCAR $(grep -c TITEL "$d/POTCAR") entries"
done
