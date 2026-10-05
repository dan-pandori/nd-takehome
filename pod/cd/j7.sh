#!/usr/bin/env bash
# J7 (pre-registered in log.md before launch; the compute-equivalent critic's measured counterfactual): continue
# training pend_S on the full K12 pretraining set (no RL proofs) with the ladder's own fine-tune recipe (state_train.py
# control recipe: lr 3e-4 -> 3e-5 cosine, warmup 50, 128 proofs / step, cap 0) for as many steps as fit in the r8 ladder's
# GPU-seconds for seed S (trajectory: 22,350 / 24,467 / 27,021 s); step rate from a 300-step probe on this GPU.  Then
# plain reads, trajectory's settings, textbook72 + holdout250 at sample seeds 0 and 1 (k 256).  Resumable.
. pod/cd/env.sh
S=$1; mkdir -p ckpts/cd/j7 artifacts/cd/j7
B=(22350 24467 27021); BUD=${B[$S]}
M=ckpts/cd/j7/cont_s${S}.pt
if [ ! -s $M ]; then
  P=ckpts/cd/j7/probe_s${S}.pt
  if [ ! -s artifacts/cd/j7/probe_s${S}.secs ]; then
    T0=$(date +%s.%N)
    ND_ARM=j7_probe python3 state_train.py --data data/kh/train_k12.jsonl --init $CK/s${S}_pend.pt --steps 300 --lr 0.0003 \
      --min_lr 3e-05 --warmup 50 --cap 0 --out $P --seed $((1000 * S + 77)) --log_every 100 --recs 128 > artifacts/cd/logs/j7_probe_s$S.log 2>&1
    T1=$(date +%s.%N); echo "$T0 $T1" > artifacts/cd/j7/probe_s${S}.secs
  fi
  read T0 T1 < artifacts/cd/j7/probe_s${S}.secs
  STEPS=$(python3 -c "t=$T1-$T0; print(int(300 * ($BUD - 60) / max(t - 40, 1)))")   # ~40 s of the probe is load / compile
  echo "$(date -u +%FT%TZ) probe $(python3 -c "print(round($T1-$T0,1))") s for 300 steps -> $STEPS steps for $BUD GPU-s"
  echo $STEPS > artifacts/cd/j7/steps_s${S}.txt
  ND_ARM=j7_cont python3 state_train.py --data data/kh/train_k12.jsonl --init $CK/s${S}_pend.pt --steps $STEPS --lr 0.0003 \
    --min_lr 3e-05 --warmup 50 --cap 0 --out $M --seed $((1000 * S + 78)) --log_every 2000 --recs 128 || exit 1
fi
for X in 0 1; do
  for P in tb72 h250; do
    IN=$([ $P = tb72 ] && echo data/bs/textbook72.jsonl || echo data/bs/holdout250.jsonl)
    LF=$([ $P = tb72 ] && echo reference_lines || echo n_lines)
    O=artifacts/cd/j7/s${S}_cont__${P}_x${X}
    [ -s $O.json ] || ND_ARM=j7_read python3 state_eval.py --ckpt $M --in $IN --out $O.jsonl --summary $O.json --k 256 \
      --temperature 0.8 --seed $X --batch 2048 --max_action 512 --max_steps 96 --lenfield $LF
  done
done
echo "$(date -u +%FT%TZ) J7 s$S done"
