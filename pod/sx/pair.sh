#!/usr/bin/env bash
# One seed of search-expert: [Stage-1 SN-cap12 for seeds >= 4] -> a sampling ladder and a coupled search/resume ladder,
# concurrently on one GPU (the second takes its round-r per-theorem action budgets from the first's alloc_r.json)
# -> k 256 read-outs of both final checkpoints.
# Usage: bash pod/sx/pair.sh <seed> <second expert: search|resume> [sampling seed offset: 0 = arm A, 50 = arm A2]
source pod/sx/env.sh
S=$1; X=$2; OFF=${3:-0}; B=2048; CK=ckpts/sx/stage1_SN12_s$S.pt
if [ ! -s $CK ]; then     # the state-cap12 recipe (pod/sc12/sn_seed.sh)
  echo "=== stage1 s$S $(date -u +%FT%TZ)"
  ND_ARM=SN12 ND_SEED=$S python3 state_train.py --data data/kh/train_k12.jsonl --heldout data/p2/heldout.jsonl --mode lean_staten \
    --steps 6000 --recs 128 --cap 12 --seed $S --out $CK || exit 1
  python3 state_eval.py --ckpt $CK --in data/p2/heldout.jsonl --k 1 --temperature 0 --batch $B \
    --out artifacts/sx/heldout_SN12_s$S.jsonl --summary artifacts/sx/heldout_SN12_s$S.json
  up ckpts/sx; up artifacts/sx
fi
if [ "$OFF" = 0 ]; then NA=A_s$S; else NA=A2_s$S; fi
case $X in search) NX=B_s$S;; resume) NX=C_s$S;; esac
COMMON="--seed $S --batch $B --train data/kh/train_k12.jsonl --heldout data/p2/heldout.jsonl --outdir artifacts/sx --ckptdir ckpts/sx/ladder \
  --step_filter --no_eval --select shortest --max_per_thm 1 --rl_weight 4"
run() {  # name, extra args
  local N=$1; shift
  [ -s ckpts/sx/ladder/${N}_r8.pt ] && { echo "$N already done"; return 0; }
  echo "=== ladder $N $(date -u +%FT%TZ)"
  ND_ARM=$N ND_SEED=$S LEAN_GATE_DUMP=artifacts/sx/dump/la_$N.jsonl LEAN_GATE_LOG=artifacts/sx/gate_$N.jsonl \
    python3 state_ladder_ei.py --init $CK --name $N $COMMON "$@" > artifacts/sx/logs/la_$N.log 2>&1 || { echo "LADDER FAILED $N"; return 1; }
  echo "=== ladder $N done $(date -u +%FT%TZ)"
}
run $NA --expert sample --seed_offset $OFF &
PA=$!
sleep 60
run $NX --expert $X --chains 4 --resume_max 4 --width 4 --alpha 1.0 --budget_from artifacts/sx/$NA --seed_offset $OFF &
PX=$!
wait $PA; RA=$?; wait $PX; RX=$?
up artifacts/sx; up ckpts/sx
[ $RA = 0 ] && bash pod/sx/reread.sh ckpts/sx/ladder/${NA}_r8.pt $NA &
[ $RX = 0 ] && bash pod/sx/reread.sh ckpts/sx/ladder/${NX}_r8.pt $NX &
wait
up artifacts/sx
echo "=== pair done $(date -u +%FT%TZ) A=$RA X=$RX"
