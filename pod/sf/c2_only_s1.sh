#!/usr/bin/env bash
# C seed 1 deep pass on an explicit survivor list (redistribution across pods). Usage: NAMES=f TAG=t SEED=s bash pod/sf/c2_only_s1.sh
cd /workspace/nd-takehome; export PATH=$HOME/.elan/bin:$PATH LEAN_GATE_WORKERS=${LGW:-8}
B=${BATCH:-1024}; CK=ckpts/sf/stage1_big_seq_s1.pt
python3 support.py --ckpt $CK --model big --stage c2 --names $NAMES --k 190000 --stop_at 5 --temperature 0.8 \
  --seed $SEED --model_seed 1 --batch $B --max_new 512 --shard 0/1 --out artifacts/sf/c2_big_T08_s1_$TAG > artifacts/sf/logs/c2s1_T08_$TAG.log 2>&1
python3 - <<PY
import json
rs = [json.loads(l) for l in open('artifacts/sf/c2_big_T08_s1_$TAG.s0.jsonl')]
open('artifacts/sf/c3s1_names_$TAG.txt', 'w').write(''.join(r['name'] + '\n' for r in rs if r['n_ok'] == 0))
PY
python3 support.py --ckpt $CK --model big --stage c2 --names artifacts/sf/c3s1_names_$TAG.txt --k 200000 --stop_at 5 --temperature 1.0 \
  --seed $((SEED+10)) --model_seed 1 --batch $B --max_new 512 --shard 0/1 --out artifacts/sf/c2_big_T10_s1_$TAG > artifacts/sf/logs/c2s1_T10_$TAG.log 2>&1
echo C2_DONE $TAG
