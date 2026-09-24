#!/usr/bin/env bash
# VPS side: pull one arm's finished artifacts into the worktree. Usage: bash pod/kh/pull.sh <arm> heldout|cov|ladder|gate|ckpt|all
cd /home/dan/work/cap-horizon; arm=$1; what=${2:-all}; P=kh-$arm
pull() { bash pod/kh/w.sh $P pull "$1" 2>&1 | grep -v "^Warning\|^rsync" ; }
if [ $what = heldout ] || [ $what = all ]; then
  for s in 0 1; do pull artifacts/kh/heldout_${arm}_s$s.json; done
fi
if [ $what = cov ] || [ $what = all ]; then
  for s in 0 1; do for pool in redreq d3req; do pull artifacts/kh/cov_${arm}_s${s}_${pool}.s0.jsonl; pull artifacts/kh/cov_${arm}_s${s}_${pool}.s0.gate.json; done; done
fi
if [ $what = ladder ] || [ $what = all ]; then
  for k in T1 frozen; do d=artifacts/kh/la_${k}_${arm}_s0; mkdir -p $d; for r in 1 2 3 4 5 6 7 8; do pull $d/round_$r.json; done; pull $d/args.json; pull $d/alloc_8.json; pull $d/found_8.jsonl; pull $d/found_transfer_8.jsonl; done
fi
if [ $what = gate ] || [ $what = all ]; then
  bash pod/kh/w.sh $P sh "ls artifacts/kh/gate_*.jsonl artifacts/kh/record_*.json artifacts/kh/*.record.jsonl artifacts/kh/*/record_*.jsonl 2>/dev/null" 2>/dev/null | grep -v "^Warning" | while read f; do pull "$f"; done
  pull artifacts/kh/logs
fi
if [ $what = ckpt ]; then for s in 0 1; do pull ckpts/kh/stage1_${arm}_s$s.pt; done; fi
ls artifacts/kh | grep -c "$arm"
