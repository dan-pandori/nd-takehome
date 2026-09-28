#!/usr/bin/env bash
# C seed 1 (addendum fe0a939): identical protocol to c_sample.sh with the seed-1 model and fresh sampling seeds 4xx.
# T 0.8 up to 190,000 more (200,000 total), stop 5; then T 1.0 up to 200,000, stop 5, only on those still unsolved.
# Usage: SH=i NSH=n BATCH=b bash pod/sf/c_sample.sh
cd /workspace/nd-takehome; export PATH=$HOME/.elan/bin:$PATH LEAN_GATE_WORKERS=${LGW:-8}
SH=${SH:-0}; NSH=${NSH:-1}; B=${BATCH:-1024}; CK=ckpts/sf/stage1_big_seq_s1.pt
python3 support.py --ckpt $CK --model big --stage c1 --names data/sc/crux_forward.txt --k 10000 --stop_at 50 --temperature 0.8 \
  --seed 401 --model_seed 1 --batch $B --max_new 512 --shard $SH/$NSH --out artifacts/sf/c1_big_T08_s1 > artifacts/sf/logs/c1s1_sh$SH.log 2>&1
python3 - <<PY
import json
surv = {l.strip() for l in open('data/sc/falsifier_survivors.txt') if l.strip()}
rs = [json.loads(l) for l in open('artifacts/sf/c1_big_T08_s1.s$SH.jsonl')]
open('artifacts/sf/c2s1_names_sh$SH.txt', 'w').write(''.join(r['name'] + '\n' for r in rs if r['name'] in surv and r['n_ok'] == 0))
PY
python3 support.py --ckpt $CK --model big --stage c2 --names artifacts/sf/c2s1_names_sh$SH.txt --k 190000 --stop_at 5 --temperature 0.8 \
  --seed $((411+SH)) --model_seed 1 --batch $B --max_new 512 --shard 0/1 --out artifacts/sf/c2_big_T08_s1_sh$SH > artifacts/sf/logs/c2s1_T08_sh$SH.log 2>&1
python3 - <<PY
import json
rs = [json.loads(l) for l in open('artifacts/sf/c2_big_T08_s1_sh$SH.s0.jsonl')]
open('artifacts/sf/c3s1_names_sh$SH.txt', 'w').write(''.join(r['name'] + '\n' for r in rs if r['n_ok'] == 0))
PY
python3 support.py --ckpt $CK --model big --stage c2 --names artifacts/sf/c3s1_names_sh$SH.txt --k 200000 --stop_at 5 --temperature 1.0 \
  --seed $((421+SH)) --model_seed 1 --batch $B --max_new 512 --shard 0/1 --out artifacts/sf/c2_big_T10_s1_sh$SH > artifacts/sf/logs/c2s1_T10_sh$SH.log 2>&1
echo C_SAMPLE_DONE $SH
