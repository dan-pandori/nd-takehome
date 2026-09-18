#!/usr/bin/env bash
# Local: one-line-per-stage status of every r34b pod. Usage: bash pod/r3_4b/status.sh [sleep-seconds-on-first-pod]
for f in ~/.config/nd-rl/pods/r34b-*; do P=$(basename $f)
  echo "== $P $(timeout 50 podrun $P "cat draw_*.log | grep -E 'start|done|FAILED|DONE' | tail -n 3 | tr '\n' ';'; for l in \$(ls -t artifacts/r3_4b/q/*.log | head -n 2); do echo; echo -n \"\$l: \"; tail -n 1 \$l | cut -c1-200; done; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader" 2>&1)"
done
