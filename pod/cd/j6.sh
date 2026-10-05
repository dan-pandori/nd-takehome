#!/usr/bin/env bash
# J6 (pre-registered in log.md before launch): the "never-had-it" control for J4.  Best-recipe Stage-1 (as trajectory /
# best-state: --recipe best, 1,200 s on an A40, cap 12) on K12 with every record containing a DN (classical double
# negation) line removed (data/cd/k12_nodn.jsonl, 133,726 records), then: held-out greedy; plain reads (k 256, seed 1)
# on the 40 held-out transfer A v ~A instances and on holdout250; J4's A0 / A16 fine-tunes from it; reads of those on
# lem40 (k 256) and A16 on holdout250 (k 64).  Resumable.
. pod/cd/env.sh
S=$1; mkdir -p ckpts/cd/j6 artifacts/cd/j6
M=ckpts/cd/j6/stage1_nodn_s${S}.pt
if [ ! -s $M ]; then
  echo "$(date -u +%FT%TZ) stage1 nodn s$S"
  ND_ARM=j6_nodn ND_SEED=$S python3 state_train.py --recipe best --data data/cd/k12_nodn.jsonl --heldout data/p2/heldout.jsonl \
    --mode lean_staten --cap 12 --seed $S --budget_secs 1200 --out $M || exit 1
fi
rd() {  # ckpt label in k lenfield seed temperature
  local O=artifacts/cd/j6/s${S}_$2__$(basename $3 .jsonl)_k$4
  [ -s $O.json ] && { echo "skip $O"; return; }
  ND_ARM=j6_read python3 state_eval.py --ckpt $1 --in $3 --out $O.jsonl --summary $O.json --k $4 --temperature ${7:-0.8} \
    --seed ${6:-1} --batch 2048 --max_action 512 --max_steps 96 --lenfield $5
}
rd $M nodn data/p2/heldout.jsonl 1 n_lines 0 0
rd $M nodn data/cd/j4/lem_transfer40.jsonl 256 n_lines
rd $M nodn data/bs/holdout250.jsonl 256 n_lines
for A in A0 A16; do
  F=ckpts/cd/j6/nodn_s${S}_${A}.pt
  [ -s $F ] || ND_ARM=j6_${A} python3 state_train.py --data data/cd/j4/mix_${A}.jsonl --init $M --steps 600 --lr 0.0003 \
      --min_lr 3e-05 --warmup 50 --cap 0 --out $F --seed $((1000 * S + 99)) --log_every 200 --recs 128
  rd $F nodn_${A} data/cd/j4/lem_transfer40.jsonl 256 n_lines
done
rd ckpts/cd/j6/nodn_s${S}_A16.pt nodn_A16 data/bs/holdout250.jsonl 64 n_lines
echo "$(date -u +%FT%TZ) J6 s$S done"
