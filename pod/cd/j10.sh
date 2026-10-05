#!/usr/bin/env bash
# J10 (pre-registered in log.md before launch): large-k plain sampling of pend_S on the long-pool theorems
# (data/ladder/transfer_long2.jsonl, 21 theorems with long proofs) that r8 or r16 solves (x0, k 256) and pend fails
# (x2, 0 / 256): 16,384 attempts per theorem, chunks of <= 8 theorems, chunk seed 7600 + chunk; standard caps, T 0.8,
# batch 1,024.  Resumable per chunk.
. pod/cd/env.sh
S=$1
for C in data/cd/j10/s${S}_c*.jsonl; do
  B=$(basename $C .jsonl); O=artifacts/cd/j10/${B}; mkdir -p artifacts/cd/j10
  [ -s $O.json ] && { echo "skip $O"; continue; }
  N=$((10#${B##*_c}))
  echo "$(date -u +%FT%TZ) start $B k 16384 seed $((7600 + N))"
  ND_ARM=j10_pend_s${S} python3 state_eval.py --ckpt $CK/s${S}_pend.pt --in $C --out $O.jsonl --summary $O.json --k 16384 \
    --temperature 0.8 --seed $((7600 + N)) --batch 1024 --max_action 512 --max_steps 96 --lenfield L_true_lb
  echo "$(date -u +%FT%TZ) end $B rc=$?"
done
echo "$(date -u +%FT%TZ) J10 s$S done"
