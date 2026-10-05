#!/usr/bin/env bash
# J4 (pre-registered): one ladder-style fine-tune step from pend_S on each mix (A0 replay only, A4 / A16 excluded-middle
# demonstrations, C16 matched non-LEM control; the ladder's exact state_train flags), then plain reads (k 256, T 0.8,
# seed 1) of every fine-tuned model, pend_S and r16_S on the 40 held-out transfer A v ~A instances; A0 / A16 also on
# holdout250 at k 64.  Resumable.
. pod/cd/env.sh
S=$1
rd() {  # ckpt label in k
  local O=artifacts/cd/j4/s${S}_$2__$3_x1
  [ -s $O.json ] && { echo "skip $O"; return; }
  ND_ARM=j4_read python3 state_eval.py --ckpt $1 --in $4 --out $O.jsonl --summary $O.json --k $5 --temperature 0.8 --seed 1 \
    --batch 2048 --max_action 512 --max_steps 96 --lenfield n_lines
}
L40=data/cd/j4/lem_transfer40.jsonl
rd $CK/s${S}_pend.pt pend lem40 $L40 256
rd $CK/s${S}_r16.pt r16 lem40 $L40 256
for A in A0 A4 A16 C16; do
  M=$CK/j4/s${S}_${A}.pt
  if [ ! -s $M ]; then
    echo "$(date -u +%FT%TZ) train $A"
    ND_ARM=j4_${A} python3 state_train.py --data data/cd/j4/mix_${A}.jsonl --init $CK/s${S}_pend.pt --steps 600 --lr 0.0003 \
      --min_lr 3e-05 --warmup 50 --cap 0 --out $M --seed $((1000 * S + 99)) --log_every 200 --recs 128
  fi
  rd $M $A lem40 $L40 256
done
rd $CK/j4/s${S}_A0.pt A0 h250 data/cd/h250_gt.jsonl 64
rd $CK/j4/s${S}_A16.pt A16 h250 data/cd/h250_gt.jsonl 64
echo "$(date -u +%FT%TZ) J4 s$S done"
