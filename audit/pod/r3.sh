#!/usr/bin/env bash
# R3: WP base s1 on the 29 survivors, T 0.8, k 200,000, stop_at 1, two shards on one card.
cd /workspace/nd-takehome
export PATH=$HOME/.elan/bin:$PATH OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True LEAN_GATE_WORKERS=32 ND_SAMPLE_PATH=fast
mkdir -p ckpts/lf
hf buckets cp hf://buckets/dan-pandori/nd-rl/lean-format/ckpts/lf/stage1_a1_seq_s1.pt ckpts/lf/stage1_a1_seq_s1.pt
md5sum ckpts/lf/stage1_a1_seq_s1.pt > artifacts/ca/R3.md5
for SH in 0 1; do
 (LEAN_GATE_DUMP=artifacts/ca/dump/R3_sh$SH.jsonl python3 support.py --ckpt ckpts/lf/stage1_a1_seq_s1.pt --model base --stage CA \
  --in artifacts/ca/surv.jsonl --k 200000 --stop_at 1 --temperature 0.8 --seed 9003 --batch 4096 --max_new 400 \
  --shard $SH/2 --out artifacts/ca/R3_base_s1_T08 > artifacts/ca/R3_sh$SH.log 2>&1; echo "EXIT $? $(date -u +%FT%TZ)" >> artifacts/ca/R3_sh$SH.log) &
done
wait
