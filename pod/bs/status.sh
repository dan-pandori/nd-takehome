#!/usr/bin/env bash
# One-line-per-pod status of the best-state pods (VPS side).
for p in bs-p0 bs-p1 bs-p2 bs-p3 bs-p4 bs-p5 bs-r0 bs-r1 bs-r2; do
  [ -f ~/.config/nd-rl/pods/$p ] || continue
  timeout 40 podrun $p "cd /workspace/nd-takehome; g=\$(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader | tr -d ' '); \
    l=\$(ls -t artifacts/bs/logs/*.log 2>/dev/null | grep -v setup | head -1); \
    r=\$(ls artifacts/bs/la_T1_*/round_*.json 2>/dev/null | wc -l); \
    echo \"$p gpu=\$g rounds=\$r \$(basename \$l): \$(grep -v Warn \$l | grep -E '===|round|FAIL|Error|done' | tail -n 1 | cut -c1-140)\"" 2>&1 | tail -n 1
done
