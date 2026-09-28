#!/usr/bin/env bash
# H (headline): SN base seed $1 on the 29 survivors: T 0.8 up to 200,000, then T 1.0 up to 200,000 on those < 5 successes.
S=$1; B=${2:-4096}; CK=ckpts/se/stage1_SN_s$S.pt
run() {  # $1 T tag, $2 T, $3 sampling seed, $4 names file
  LEAN_GATE_DUMP=artifacts/ss/dump/H_base_$1_s$S.jsonl LEAN_GATE_LOG=artifacts/ss/logs/gate_H_base_$1_s$S.jsonl \
  python3 ss_support.py --ckpt $CK --model base --stage H --names $4 --k 200000 --stop_at 5 --temperature $2 \
    --seed $3 --model_seed $S --batch $B --out artifacts/ss/H_base_$1_s$S
}
run T08 0.8 $((S * 10 + 1)) data/sc/falsifier_survivors.txt || exit 1
python3 -c "
import json; r=[json.loads(l) for l in open('artifacts/ss/H_base_T08_s$S.s0.jsonl')]
open('artifacts/ss/H_T10_names_s$S.txt','w').write(''.join(x['name']+'\n' for x in r if x['n_ok'] < 5))"
run T10 1.0 $((S * 10 + 2)) artifacts/ss/H_T10_names_s$S.txt
