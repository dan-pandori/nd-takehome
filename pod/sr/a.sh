#!/usr/bin/env bash
# Part A: support-state's H protocol for a state base (arm S or SH), seed $2, on the 29 survivors:
# T 0.8 up to 200,000 attempts per theorem (stop at 5 successes), then T 1.0 up to 200,000 on rows with < 5 successes.
# Sampling seeds = support-state's (10*seed+1 at T 0.8, 10*seed+2 at T 1.0). Resumable. Usage: a.sh <S|SH> <seed> [batch]
M=$1; S=$2; B=${3:-4096}; CK=ckpts/sr/stage1_${M}_s$S.pt; D=artifacts/state-readouts
run() {  # $1 T tag, $2 T, $3 sampling seed, $4 names file
  LEAN_GATE_DUMP=$D/dump/H_${M}_$1_s$S.jsonl LEAN_GATE_LOG=$D/logs/gate_H_${M}_$1_s$S.jsonl \
  python3 ss_support.py --ckpt $CK --model ${M}_base --stage H --names $4 --k 200000 --stop_at 5 --temperature $2 \
    --seed $3 --model_seed $S --batch $B --out $D/H_${M}_$1_s$S
}
run T08 0.8 $((S * 10 + 1)) data/sc/falsifier_survivors.txt || exit 1
python3 -c "
import json; r=[json.loads(l) for l in open('$D/H_${M}_T08_s$S.s0.jsonl')]
assert len(r) == 29, len(r)
open('$D/H_T10_names_${M}_s$S.txt','w').write(''.join(x['name']+'\n' for x in r if x['n_ok'] < 5))"
[ -f $D/H_${M}_T08_s$S.t08only ] && exit 0      # budget stop: skip the T 1.0 phase (touch this marker)
run T10 1.0 $((S * 10 + 2)) $D/H_T10_names_${M}_s$S.txt
