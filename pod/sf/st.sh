#!/usr/bin/env bash
# One status line per pod: finished jobs, the running job's last log line.
for i in ${@:-1 2 3 4}; do
  echo "== sf-$i $(timeout 40 podrun sf-$i "cd /workspace/nd-takehome; ls artifacts/sf2/*.done artifacts/sf2/*.fail 2>/dev/null | xargs -n1 basename | grep -v setup | tr '\n' ' '; f=\$(ls -t artifacts/sf2/logs/*.log | grep -v -e gate -e queue | head -1); echo; echo \$f: \$(tail -n 1 \$f | cut -c1-160)" 2>&1 | tail -2 | tr '\n' ' ')"
done
