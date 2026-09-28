#!/usr/bin/env bash
# fast-stage1 main job on one A40: the 8-seed --impl fast equivalence arm, laid out as the seeds-per-GPU test
# (N=1: s0; N=2: s1,s2; N=4: s3..s6; N=1: s7), then N=8 throughput (seeds 100..107, 2,000 steps, no eval),
# then legacy concurrency timing (N=1,2,4; 1,000 steps), then held-out greedy of s0..s7 with sd_eval.py
# (arm C's settings: batch 512, max_new 400).  Each wave is timed; logs in artifacts/fs/logs/.
cd /workspace/nd-takehome; export OMP_NUM_THREADS=4 PATH=$HOME/.elan/bin:$PATH
D=data/p2/train_depth3_f0_a1.jsonl; H=data/p2/heldout.jsonl
C="--mode lean_seq --bs 128 --lr 1e-3 --min_lr 1e-4 --warmup 200 --cap 6 --val_bins --log_every 200"
W=artifacts/fs/waves.jsonl
wave() {   # wave <name> <impl> <steps> <seed...>
  local name=$1 impl=$2 steps=$3; shift 3; local t=$(date +%s.%N); local pids=""
  for s in "$@"; do
    rm -f artifacts/fs/m_${name}_s$s.jsonl
    python3 train.py --data $D --heldout $H $C --steps $steps --seed $s --impl $impl --out ckpts/fs/${name}_s$s.pt \
      --metrics artifacts/fs/m_${name}_s$s.jsonl > artifacts/fs/logs/${name}_s$s.log 2>&1 & pids="$pids $!"
  done
  local peak=0
  while kill -0 $pids 2>/dev/null; do m=$(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits | head -1); echo "$(date +%s) $m" >> artifacts/fs/logs/${name}_smi.txt; sleep 2; done
  wait $pids
  echo "{\"wave\": \"$name\", \"impl\": \"$impl\", \"steps\": $steps, \"seeds\": \"$*\", \"n\": $#, \"wall_s\": $(python3 -c "import time; print(round(time.time() - $t, 2))")}" >> $W
}
wave fast1 fast 6000 0
wave fast2 fast 6000 1 2
wave fast4 fast 6000 3 4 5 6
wave fast1b fast 6000 7
wave thr8 fast 2000 100 101 102 103 104 105 106 107
wave leg1 legacy 1000 200
wave leg2 legacy 1000 201 202
wave leg4 legacy 1000 203 204 205 206
for s in 0 1 2 3 4 5 6 7; do ls ckpts/fs/fast*_s$s.pt; done > artifacts/fs/eval_list.txt
python3 sd_eval.py --ckpts $(cat artifacts/fs/eval_list.txt) --in $H --outdir artifacts/fs/ev --batch 512 --max_new 400 > artifacts/fs/logs/eval.log 2>&1
touch artifacts/fs/main.done
