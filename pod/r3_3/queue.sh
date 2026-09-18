#!/usr/bin/env bash
# round3-run3 pod queue.  Usage: bash pod/r3_3/queue.sh <set> [seeds...]     set ∈ depth3 | reductio | derived_ore
# Stage-1 for every seed (2 concurrent), then pass@2000 coverage over the set's pool(s), one job at a time.
# Every job is skipped if its output already exists (resumable).  Logs under artifacts/r3_3/.
# Env overrides: POOLS_OVERRIDE="p2" (only these pool tags), SKIP_TRAIN=1 (checkpoints already present).
cd /workspace/nd-takehome; mkdir -p artifacts/r3_3 ckpts/r3_3
SET=$1; shift; SEEDS=${*:-$(seq 30 53)}
case $SET in
  depth3)      DATA=data/p2/train_depth3_f0_a1.jsonl; TAG=depth3_f0_a1; POOLS="p1:data/r3_3/targets_depth3_p1.jsonl p2:data/r3_3/targets_depth3_p2.jsonl";;
  reductio)    DATA=data/p2/train_reductio_f0.jsonl;  TAG=reductio_f0;  POOLS="req:data/p2/targets_reductio_req.jsonl";;
  derived_ore) DATA=data/p2/train_derived_ore_f0.jsonl; TAG=derived_ore_f0; POOLS="dos6:data/r3_3/targets_derived_ore_strict_c6.jsonl";;
  *) echo "bad set $SET"; exit 1;;
esac
if [ -n "$POOLS_OVERRIDE" ]; then NP=""; for pool in $POOLS; do for t in $POOLS_OVERRIDE; do [ "${pool%%:*}" = "$t" ] && NP="$NP $pool"; done; done; POOLS=$NP; fi
train_one() { s=$1; CK=ckpts/r3_3/stage1_${TAG}_s$s.pt; L=artifacts/r3_3/train_${TAG}_s$s.log
  if [ -f "$CK" ] && grep -q '^saved' "$L" 2>/dev/null; then echo "skip train $s"; return; fi
  echo "$(date -u +%FT%TZ) train $TAG s$s start"
  python -u train.py --data $DATA --heldout data/p2/heldout.jsonl --mode abs --steps 6000 --bs 128 --cap 6 --seed $s --out $CK > $L 2>&1; rc=$?
  echo "$(date -u +%FT%TZ) train $TAG s$s rc=$rc $(grep -o 'val [0-9.]*' $L | tail -1)"; }
train_worker() { for s in $*; do train_one $s; done; }
A=""; B=""; i=0; for s in $SEEDS; do if [ $((i%2)) = 0 ]; then A="$A $s"; else B="$B $s"; fi; i=$((i+1)); done
if [ -z "$SKIP_TRAIN" ]; then train_worker $A & train_worker $B & wait; fi
echo "$(date -u +%FT%TZ) all Stage-1 done for $TAG"
for pool in $POOLS; do P=${pool%%:*}; F=${pool#*:}
  for s in $SEEDS; do CK=ckpts/r3_3/stage1_${TAG}_s$s.pt; OUT=artifacts/r3_3/cov_${TAG}_s${s}_$P
    N=$(wc -l < $F); [ -f "$CK" ] || { echo "MISSING $CK"; continue; }
    if [ -f "$OUT.s0.jsonl" ] && [ "$(wc -l < $OUT.s0.jsonl)" = "$N" ]; then echo "skip cov $s $P"; continue; fi
    echo "$(date -u +%FT%TZ) cov $TAG s$s $P start"
    python -u coverage.py --ckpt $CK --in $F --k 2000 --temperature 0.8 --batch 2000 --procs 4 --seed 0 --out $OUT > artifacts/r3_3/cov_${TAG}_s${s}_$P.log 2>&1; rc=$?
    echo "$(date -u +%FT%TZ) cov $TAG s$s $P rc=$rc records $(wc -l < $OUT.s0.jsonl)"
  done
done
echo "$(date -u +%FT%TZ) QUEUE DONE $TAG"; touch artifacts/r3_3/QUEUE_DONE_$TAG
