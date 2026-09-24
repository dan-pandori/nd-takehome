#!/usr/bin/env bash
# cap-horizon: pull the two INHERITED arms' measurement files from the ds-composition bucket, so
# this run re-derives their max accepted length, >=8/10/12-line counts, L* and TERM SIZES with its
# own tooling (term size was never reported).  K6 = ds-composition's C0; K8flat = its A3.
# Usage: bash kh_pull_inherited.sh
set -u
B=hf://buckets/dan-pandori/nd-rl/ds-composition/artifacts/dsc
D=artifacts/dsc_inherited
mkdir -p $D
get() { [ -s "$D/$1" ] && { echo "have $1"; return; }; mkdir -p "$D/$(dirname "$1")"; hf buckets cp "$B/$1" "$D/$1" >/dev/null 2>&1 && echo "got $1" || echo "MISSING $1"; }
for arm in c0 a3; do
  for s in 0 1; do
    get heldout_${arm}_s${s}.json
    for pool in redreq d3req; do get cov_${arm}_s${s}_${pool}.s0.jsonl; get cov_${arm}_s${s}_${pool}.s0.gate.json; done
  done
  get record_${arm}.json
  for k in T1 frozen; do
    d=la_${k}_${arm}_s0
    get $d/args.json; get $d/alloc_8.json; get $d/found_8.jsonl; get $d/found_transfer_8.jsonl
    for r in 1 2 3 4 5 6 7 8; do get $d/round_$r.json; done
  done
done
du -sh $D
