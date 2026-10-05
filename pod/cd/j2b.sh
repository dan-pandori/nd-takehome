#!/usr/bin/env bash
# J2 stage A' and stage B (pre-registered in log.md before launch).  A': each seed's hard theorems that no RL read
# solved (H minus J2) at k 16,384 (chunk seed 7200 + chunk), so the base gets the compute-matched budget on every hard
# theorem.  B: J2 theorems with 0 successes after stage A get 49,152 more attempts (65,536 in all; seed 7300 + chunk),
# files data/cd/j2/s<S>_b*.jsonl written on the VPS from stage A's results.  Same read settings as J2.  Resumable.
. pod/cd/env.sh
S=$1
for C in data/cd/j2/s${S}_d*.jsonl data/cd/j2/s${S}_b*.jsonl; do
  [ -e "$C" ] || continue
  B=$(basename $C .jsonl); O=artifacts/cd/j2/${B}
  [ -s $O.json ] && { echo "skip $O"; continue; }
  T=${B##*_}; N=$((10#${T:1}))
  if [ "${T:0:1}" = d ]; then K=16384; SEED=$((7200 + N)); else K=49152; SEED=$((7300 + N)); fi
  echo "$(date -u +%FT%TZ) start $B k $K seed $SEED"
  ND_ARM=j2b_pend_s${S} python3 state_eval.py --ckpt $CK/s${S}_pend.pt --in $C --out $O.jsonl --summary $O.json --k $K \
    --temperature 0.8 --seed $SEED --batch 2048 --max_action 512 --max_steps 96 --lenfield n_lines
  echo "$(date -u +%FT%TZ) end $B rc=$?"
done
