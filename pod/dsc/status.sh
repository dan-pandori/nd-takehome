#!/usr/bin/env bash
# VPS side: one-line status per job on each pod. Usage: bash pod/dsc/status.sh [pods...]
for n in ${@:-dsc-c0 dsc-a1 dsc-a2 dsc-a3 dsc-a4}; do
  [ -f ~/.config/nd-rl/pods/$n ] || continue
  echo "== $n $(date -u +%H:%M)"; bash /home/dan/work/ds-composition/pod/dsc/w.sh $n sh 'for f in artifacts/dsc/logs/*.log; do j=$(basename $f .log); [ $j = setup ] && continue; s=run; [ -f artifacts/dsc/$j.done ] && s=DONE; [ -f artifacts/dsc/$j.failed ] && s=FAILED; echo "$j [$s] $(grep -v "^\[lean_gate\]" $f | tail -n 1 | cut -c1-140)"; done; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader' < /dev/null 2>&1 | grep -v "^Warning"
done
