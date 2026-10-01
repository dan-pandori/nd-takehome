#!/usr/bin/env bash
# One-line status per pod.  Usage: bash pod/tj6/mon.sh
cd /home/dan/work/trajectory-cap6
for p in 0 1 2; do echo "tj6-p$p: $(TO=30 pod/tj6/sh.sh tj6-p$p "grep -v W1001 artifacts/tj6/logs/seed$p.log | grep -o '^=== .*\|round [0-9] done in [0-9]*s.*\|^step [0-9]* ' | tail -n1; ls artifacts/tj6/seed$p.{done,fail} 2>/dev/null" 2>&1 | tr '\n' ' ')"; done
for r in 0 1 2 3; do echo "tj6-r$r: $(TO=30 pod/tj6/sh.sh tj6-r$r "echo done \$(ls artifacts/tj6/eval/.done_* 2>/dev/null | wc -l); grep '^=== \|FAIL' artifacts/tj6/logs/read$r.log | tail -n1" 2>&1 | tr '\n' ' ')"; done
