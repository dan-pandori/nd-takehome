#!/usr/bin/env bash
# One line per ladder: last progress line.  Usage: bash pod/gb/mon.sh [pods...]
P=${*:-gb-p0 gb-p1 gb-p2 gb-p3 gb-p4 gb-p5}
for p in $P; do
  podrun $p "cd /workspace/nd-takehome; for f in artifacts/gb/logs/gb_*.log; do echo \"\$f: \$(grep -E '^step|cumulative|Error|Traceback|=== ' \$f | tail -n 1 | cut -c1-150)\"; done; ls artifacts/gb/*.done artifacts/gb/*.fail 2>/dev/null | tr '\n' ' '; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader" 2>&1 | sed "s/^/$p /"
done
