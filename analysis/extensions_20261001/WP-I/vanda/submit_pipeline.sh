#!/bin/bash
# Submit pilot -> production -> finalization with PBS dependencies.
set -euo pipefail
cd /scratch/junbotong/qoi-wpi-20261001
test -f PREPARED

pilot=$(qsub pilot.pbs)
prod=$(qsub -W depend=afterok:"$pilot" production.pbs)
fin=$(qsub -W depend=afterok:"$prod" finalize.pbs)

cat > submitted_jobs.json <<EOF
{
  "pilot": "$pilot",
  "production": "$prod",
  "finalize": "$fin"
}
EOF
echo "WP-I submitted"
echo "pilot=$pilot"
echo "production=$prod"
echo "finalize=$fin"
