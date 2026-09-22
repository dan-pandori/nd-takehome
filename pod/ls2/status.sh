#!/usr/bin/env bash
# VPS side: one-line status per job on each pod. Usage: bash pod/ls2/status.sh [pods...]
for n in ${@:-ls2-1 ls2-2}; do
  [ -f ~/.config/nd-rl/pods/$n ] || continue
  echo "== $n"; podrun $n 'for f in artifacts/lf/logs/*.log; do j=$(basename $f .log); [ $j = setup ] && continue; s=run; [ -f artifacts/lf/$j.done ] && s=DONE; [ -f artifacts/lf/$j.failed ] && s=FAILED; echo "$j [$s] $(grep -v "^\[lean_gate\]" $f | tail -n 1 | cut -c1-150)"; done; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader' < /dev/null 2>&1 | grep -v "^Warning"
done
