#!/usr/bin/env bash
# Truncation diagnostic (added after seeing S s1's action-cap hits on la_transfer_100): re-run an arm's missed survivors
# at max_action 1024 (else as a.sh's T 0.8 phase, same sampling seed). Usage: diag.sh <S|SH> <seed> <names file>
M=$1; S=$2; N=$3; D=artifacts/state-readouts
LEAN_GATE_DUMP=$D/dump/Hdiag_${M}_T08_ma1024_s$S.jsonl LEAN_GATE_LOG=$D/logs/gate_Hdiag_${M}_T08_ma1024_s$S.jsonl \
python3 ss_support.py --ckpt ckpts/sr/stage1_${M}_s$S.pt --model ${M}_base_ma1024 --stage Hdiag --names $N --k 200000 \
  --stop_at 5 --temperature 0.8 --seed $((S * 10 + 1)) --model_seed $S --batch 4096 --max_action 1024 --out $D/Hdiag_${M}_T08_ma1024_s$S
