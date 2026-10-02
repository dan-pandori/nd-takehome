#!/bin/sh
# fetch per-step scores + r0/r8 reads for trajectory (tj) and trajectory-cap6 (tj6)
set -e
B=hf://buckets/dan-pandori/nd-rl
OUT=/home/dan/review/claim-audit/rv/C567_raw
get() { mkdir -p "$(dirname "$OUT/$1")"; [ -s "$OUT/$1" ] || flock /tmp/ca_hf.lock nice -n 10 hf buckets cp "$B/$1" "$OUT/$1" >/dev/null; }
for run in trajectory:tj trajectory-cap6:tj6; do
  r=${run%%:*}; a=${run##*:}
  for s in 0 1 2; do
    get $r/artifacts/$a/score/s$s/targets.jsonl
    for c in p0 p50 p100 p200 p400 p800 p1600 p3000 p5000 p8000 p12000 p16000 p20000 pend r1 r2 r3 r4 r5 r6 r7 r8; do
      get $r/artifacts/$a/score/s$s/s${s}_$c.jsonl
    done
    for c in pend r8; do for p in h250 tb72; do for x in x0 x1; do
      get $r/artifacts/$a/eval/s${s}_${c}__${p}_${x}.jsonl
    done; done; done
  done
done
get trajectory/data/tj/ref_targets.jsonl
echo done
