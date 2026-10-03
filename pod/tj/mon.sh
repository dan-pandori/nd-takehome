#!/usr/bin/env bash
# One-line status per pod.  Usage: bash pod/tj/mon.sh
cd /home/dan/work/trajectory
for p in 1 2 3; do s=$((p-1)); echo "tj-p$p s$s: $(pod/tj/sh.sh tj-p$p "grep -o '=== round [0-9] done in [0-9]*s; new proofs [0-9]*; cum targets solved [0-9]*' artifacts/tj/logs/ladder$s*.log | tail -n1 | cut -d: -f2-; ls artifacts/tj/ladder$s*.{done,fail} 2>/dev/null" 2>&1 | tr '\n' ' ')"; done
for r in "tj-r0 readD0" "tj-p0 readD1" "tj-r1 readD5" "tj-r2 readD2" "tj-r3 readD3" "tj-r4 readD4"; do set -- $r; echo "$1: $(pod/tj/sh.sh $1 "echo done \$(ls artifacts/tj/eval/.done_* 2>/dev/null | wc -l); grep '^=== ' artifacts/tj/logs/$2.log | tail -n1" 2>&1 | tr '\n' ' ')"; done
