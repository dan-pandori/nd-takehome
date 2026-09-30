#!/usr/bin/env bash
# One-line-per-job progress for the run's pods. Usage: pod/sr/st.sh [pods...]
for p in ${@:-sr-1 sr-2 sr-3}; do
  [ -f ~/.config/nd-rl/pods/$p ] || continue
  podrun $p "cd /workspace/nd-takehome/artifacts/state-readouts; for f in logs/A_*.log logs/B_*.log; do [ -f \$f ] && echo $p \$f \$(grep -E '^\s+\[|===|DONE|rror' \$f | tail -n 1 | cut -c1-120); done; ls *.done *.fail 2>/dev/null | tr '\n' ' '; echo" 2>&1 | grep -v '^$'
done
