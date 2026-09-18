#!/usr/bin/env bash
# Local: compact status, one line per unfinished log on each r34b pod.
for f in ~/.config/nd-rl/pods/r34b-*; do P=$(basename $f)
  echo "== $P $(timeout 50 podrun $P 'cd artifacts/r3_4b/q; echo "done: $(ls *.done *.skipped 2>/dev/null | sed "s/.done//" | tr "\n" " ")"; for l in *.log; do b=${l%.log}; [ -f $b.done ] && continue; case $l in draw_*|post*|retry_*|chain_*|*oom*|*nofile*) continue;; esac; echo "  $b: $(grep -E "round [0-9] done|n_ok|FAILED|Error" $l | tail -n 1 | cut -c1-100) $(grep -E "^step" $l | tail -n 1 | cut -c1-45)"; done; nvidia-smi --query-gpu=memory.used --format=csv,noheader' 2>&1)"
done
