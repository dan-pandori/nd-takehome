#!/usr/bin/env bash
# VPS side: pull one arm's finished artifacts into the worktree. Usage: bash pod/dsc/pull.sh <arm> dial|cov|ladder|gate|all
cd /home/dan/work/ds-composition; arm=$1; what=${2:-all}; P=dsc-$arm
pull() { bash pod/dsc/w.sh $P pull "$1" 2>&1 | grep -v "^Warning\|^rsync" ; }
if [ $what = dial ] || [ $what = all ]; then
  for k in ei frozen; do for s in 0 1; do d=artifacts/dsc/${k}_${arm}_s$s; mkdir -p $d; for f in args.json round_1.json round_2.json round_3.json round_4.json found_4.jsonl found_transfer_4.jsonl; do pull $d/$f; done; done; done
fi
if [ $what = cov ] || [ $what = all ]; then
  for s in 0 1; do for pool in redreq d3req d3sub; do pull artifacts/dsc/cov_${arm}_s${s}_${pool}.s0.jsonl; pull artifacts/dsc/cov_${arm}_s${s}_${pool}.s0.gate.json; done; done
fi
if [ $what = ladder ] || [ $what = all ]; then
  for k in T1 frozen; do for s in 0 1; do d=artifacts/dsc/la_${k}_${arm}_s$s; mkdir -p $d; for r in 1 2 3 4 5 6 7 8; do pull $d/round_$r.json; done; pull $d/args.json; pull $d/alloc_8.json; pull $d/found_8.jsonl; pull $d/found_transfer_8.jsonl; done; done
fi
if [ $what = gate ] || [ $what = all ]; then
  bash pod/dsc/w.sh $P sh "ls artifacts/dsc/gate_*.jsonl artifacts/dsc/record_*.json artifacts/dsc/*.record.jsonl artifacts/dsc/*/record_*.jsonl 2>/dev/null" 2>/dev/null | grep -v "^Warning" | while read f; do pull "$f"; done
  pull artifacts/dsc/logs
fi
ls artifacts/dsc | grep -c "$arm"
