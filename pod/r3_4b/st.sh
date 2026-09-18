#!/usr/bin/env bash
# Local: compact status. One line per log on each r34b pod.
for f in ~/.config/nd-rl/pods/r34b-*; do P=$(basename $f)
  echo "== $P"; timeout 50 podrun $P 'cd artifacts/r3_4b/q; for l in *.log; do b=${l%.log}; [ -f $b.done ] && { echo "  $b DONE"; continue; }; case $l in draw_*|post_*|retry_*|*oom*) continue;; esac; echo "  $b: $(grep -E "round [0-9] done|^step|n_ok|FAILED|Error" $l | tail -n 1 | cut -c1-110)"; done; ls *.done 2>/dev/null | wc -l' 2>&1
done
