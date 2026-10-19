#!/usr/bin/env bash
# One-line-per-job status of every kal-* pod.  Usage: pod/kal/status.sh
for F in ~/.config/nd-rl/pods/kal-*; do
  P=$(basename $F)
  timeout 25 podrun $P "cd /workspace/nd-takehome; G=\$(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | tr -d ' ');
    T=\$(for f in artifacts/kalmar/logs/train_kal*_s*.log; do [ -f \$f ] && echo \"\$(basename \$f .log):\$(grep -E '^step ' \$f | tail -n 1 | awk '{print \$2\"@\"\$11}')\$( [ -f \${f%.log}.done ] && echo ' DONE')\"; done | tr '\n' ' ');
    E=\$(for f in artifacts/kalmar/logs/eval_*.log; do [ -f \$f ] && tail -n 1 \$f | awk '{print \$1, \$2}'; done | tr '\n' ';');
    echo \"$P gpu[\$G] train[\$T] eval[\$E]\"" 2>/dev/null || echo "$P unreachable"
done
