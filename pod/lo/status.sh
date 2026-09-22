#!/usr/bin/env bash
# VPS side: one-line status per job on each pod. Usage: bash pod/lf/status.sh [pods...]
for n in ${@:-lo-1 lo-2 lo-3 lo-4 lo-5 lo-6}; do
  [ -f ~/.config/nd-rl/pods/$n ] || continue
  echo "== $n"; podrun $n 'for f in artifacts/lo/logs/*.log; do j=$(basename $f .log); [ $j = setup ] && continue; s=run; [ -f artifacts/lo/$j.done ] && s=DONE; [ -f artifacts/lo/$j.failed ] && s=FAILED; echo "$j [$s] $(grep -v "^\[lean_gate\]" $f | tail -n 1 | cut -c1-150)"; done; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader' < /dev/null 2>&1 | grep -v "^Warning"
done
