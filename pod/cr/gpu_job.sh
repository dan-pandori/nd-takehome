#!/bin/bash
# compute-record GPU check (one pod, <= 15 min).  Run from /workspace/nd-takehome:  bash pod/cr/gpu_job.sh
# Every job's own wall-clock (date before / after the python process) goes to walls.jsonl; the registry rows the
# scripts write (record.compute) go to artifacts/compute-record/registry/.  pod/cr/analyze.py compares them.
export ND_RUN_ID=compute-record ND_REGISTRY_DIR=artifacts/compute-record/registry PYTHONUNBUFFERED=1
O=artifacts/compute-record/gpu; mkdir -p $O ckpts/cr
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv > $O/gpu.txt
w() { name=$1; shift; t0=$(date +%s.%N); "$@" > $O/$name.log 2>&1; rc=$?; t1=$(date +%s.%N)
      echo "{\"job\": \"$name\", \"t0\": $t0, \"t1\": $t1, \"rc\": $rc}" >> $O/walls.jsonl; }
D="--data data/lj/train_retain.jsonl --mode lean_seq --cap 0 --bs 500 --seed 0"
# 1. Stage-1 training, fast path (3,000 records, bs 500: 6 steps an epoch; 6,000 steps = 1,000 epochs)
w train_fast python3 train.py $D --heldout data/lj/heldout200.jsonl --steps 6000 --log_every 1000 \
  --out ckpts/cr/fast_s0.pt --metrics $O/train_fast.metrics.jsonl
# 2. overhead A/B on the legacy path (per-step counter): 600 steps each, compute recording off / on, alternated
for i in 1 2; do
  ND_COMPUTE=0 w legacy_off_$i python3 train.py $D --impl legacy --steps 600 --log_every 600 --out ckpts/cr/leg_off_$i.pt
  w legacy_on_$i python3 train.py $D --impl legacy --steps 600 --log_every 600 --out ckpts/cr/leg_on_$i.pt
done
# 3. sampling: 4,000 prompts, batch 4,096, max_new 288, inside a record.compute block; counters vs the raw ids
LEAN_GATE_LOG=$O/sample_gate.jsonl w sample python3 pod/cr/gpu_check.py sample --ckpt ckpts/cr/fast_s0.pt --out $O/sample_check.json
# 4. one EI round of ladder_ei.py (sample -> Lean -> fine-tune child process): per-phase rows vs the job's wall-clock
LEAN_GATE_LOG=$O/ladder_gate.jsonl w ladder python3 ladder_ei.py --init ckpts/cr/fast_s0.pt --name cr_ladder \
  --outdir artifacts/compute-record/ladder --targets data/lj/targets200.jsonl --transfer data/lj/transfer50.jsonl \
  --heldout data/lj/heldout200.jsonl --train data/lj/train_retain.jsonl --rounds 1 --k 32 --max_new 288 \
  --ft_steps 300 --retain 2000 --batch 4096
# 5. expected token counts and the per-step counter's cost, from the data (independent of the counters)
w expect python3 pod/cr/gpu_check.py expect --out $O/expect.json
# 6. the CPU tests, GPU hidden
CUDA_VISIBLE_DEVICES= ND_OFFLINE=1 ND_REGISTRY_SYNC=0 ND_RUN_ID= w test_registry python3 tests/test_registry.py
CUDA_VISIBLE_DEVICES= ND_OFFLINE=1 ND_REGISTRY_SYNC=0 ND_RUN_ID= w test_smoke python3 tests/test_smoke_train_sample.py
echo JOB DONE > $O/DONE
