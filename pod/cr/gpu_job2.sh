#!/bin/bash
# compute-record GPU check, part 2: the job block's clock starts at process creation (record._proc_age); an EI round
# that fine-tunes (targets = data/lj/heldout200, which the 6-minute model solves), so the child train.py path runs.
export ND_RUN_ID=compute-record ND_REGISTRY_DIR=artifacts/compute-record/registry PYTHONUNBUFFERED=1
O=artifacts/compute-record/gpu; mkdir -p $O
w() { name=$1; shift; t0=$(date +%s.%N); "$@" > $O/$name.log 2>&1; rc=$?; t1=$(date +%s.%N)
      echo "{\"job\": \"$name\", \"t0\": $t0, \"t1\": $t1, \"rc\": $rc}" >> $O/walls.jsonl; }
w train_fast_short python3 train.py --data data/lj/train_retain.jsonl --mode lean_seq --cap 0 --bs 500 --seed 1 --steps 600 \
  --log_every 600 --out ckpts/cr/fast_s1.pt
LEAN_GATE_LOG=$O/ladder2_gate.jsonl w ladder2 python3 ladder_ei.py --init ckpts/cr/fast_s0.pt --name cr_ladder2 \
  --outdir artifacts/compute-record/ladder2 --targets data/lj/heldout200.jsonl --transfer data/lj/transfer50.jsonl \
  --heldout data/lj/targets200.jsonl --train data/lj/train_retain.jsonl --rounds 2 --k 32 --max_new 288 \
  --ft_steps 300 --retain 2000 --batch 4096
w expect2 python3 pod/cr/gpu_check.py expect --out $O/expect2.json
echo JOB DONE > $O/DONE2
