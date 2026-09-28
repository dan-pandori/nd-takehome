#!/usr/bin/env bash
# C sampling, one shard: c1 = forward crux (82) at k 10,000, T 0.8, stop 50; then c2 = this shard's survivors unsolved in c1:
# T 0.8 up to 190,000 more (200,000 total), stop 5; then T 1.0 up to 200,000, stop 5, only on those still unsolved.
# Usage: SH=i NSH=n BATCH=b bash pod/sf/c_sample.sh
cd /workspace/nd-takehome; export PATH=$HOME/.elan/bin:$PATH LEAN_GATE_WORKERS=${LGW:-8}
SH=${SH:-0}; NSH=${NSH:-1}; B=${BATCH:-1024}; CK=ckpts/sf/stage1_big_seq_s0.pt
python3 support.py --ckpt $CK --model big --stage c1 --names data/sc/crux_forward.txt --k 10000 --stop_at 50 --temperature 0.8 \
  --seed 301 --model_seed 0 --batch $B --max_new 512 --shard $SH/$NSH --out artifacts/sf/c1_big_T08_s0 > artifacts/sf/logs/c1_sh$SH.log 2>&1
python3 - <<PY
import json
surv = {l.strip() for l in open('data/sc/falsifier_survivors.txt') if l.strip()}
rs = [json.loads(l) for l in open('artifacts/sf/c1_big_T08_s0.s$SH.jsonl')]
open('artifacts/sf/c2_names_sh$SH.txt', 'w').write(''.join(r['name'] + '\n' for r in rs if r['name'] in surv and r['n_ok'] == 0))
PY
python3 support.py --ckpt $CK --model big --stage c2 --names artifacts/sf/c2_names_sh$SH.txt --k 190000 --stop_at 5 --temperature 0.8 \
  --seed $((311+SH)) --model_seed 0 --batch $B --max_new 512 --shard 0/1 --out artifacts/sf/c2_big_T08_s0_sh$SH > artifacts/sf/logs/c2_T08_sh$SH.log 2>&1
python3 - <<PY
import json
rs = [json.loads(l) for l in open('artifacts/sf/c2_big_T08_s0_sh$SH.s0.jsonl')]
open('artifacts/sf/c3_names_sh$SH.txt', 'w').write(''.join(r['name'] + '\n' for r in rs if r['n_ok'] == 0))
PY
python3 support.py --ckpt $CK --model big --stage c2 --names artifacts/sf/c3_names_sh$SH.txt --k 200000 --stop_at 5 --temperature 1.0 \
  --seed $((321+SH)) --model_seed 0 --batch $B --max_new 512 --shard 0/1 --out artifacts/sf/c2_big_T10_s0_sh$SH > artifacts/sf/logs/c2_T10_sh$SH.log 2>&1
echo C_SAMPLE_DONE $SH
