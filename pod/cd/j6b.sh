#!/usr/bin/env bash
# J6b (pre-registered in log.md before launch; the elicit-finetune critic's corrected design): from pend_S and from the
# no-DN knockout of seed S (J6), one ladder-style fine-tune on A16n (16 excluded-middle demonstrations x 4 + 20,000
# replay records drawn from the knockout corpus K12 minus DN) and on C16n (16 L_true-matched non-LEM proofs x 4 + the
# same replay), two fine-tune seeds each; plain reads (k 256, T 0.8, seed 1) on the 40 held-out transfer A v ~A.
. pod/cd/env.sh
S=$1; mkdir -p ckpts/cd/j6b artifacts/cd/j6b
for M in pend nodn; do
  if [ $M = pend ]; then I=$CK/s${S}_pend.pt; else I=ckpts/cd/j6/stage1_nodn_s${S}.pt; fi
  [ -s $I ] || { echo "missing $I"; continue; }
  for A in A16n C16n; do
    for FS in 0 1; do
      F=ckpts/cd/j6b/${M}_s${S}_${A}_f${FS}.pt; O=artifacts/cd/j6b/s${S}_${M}_${A}_f${FS}__lem40_x1
      [ -s $F ] || ND_ARM=j6b_${M}_${A} python3 state_train.py --data data/cd/j4/mix_${A}.jsonl --init $I --steps 600 --lr 0.0003 \
          --min_lr 3e-05 --warmup 50 --cap 0 --out $F --seed $((1000 * S + 199 + FS)) --log_every 200 --recs 128
      [ -s $O.json ] || ND_ARM=j6b_read python3 state_eval.py --ckpt $F --in data/cd/j4/lem_transfer40.jsonl --out $O.jsonl \
          --summary $O.json --k 256 --temperature 0.8 --seed 1 --batch 2048 --max_action 512 --max_steps 96 --lenfield n_lines
    done
  done
done
echo "$(date -u +%FT%TZ) J6b s$S done"
