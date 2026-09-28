#!/usr/bin/env bash
# Speed on one GPU class (run fast-stage1): one --impl fast model (2,000 steps, --val_bins), the same at bs 512
# (500 steps, same tokens; speed only), N=2 fast concurrently (2,000 steps), and legacy (500 steps).  TAG = GPU tag.
cd /workspace/nd-takehome; export OMP_NUM_THREADS=4; T=${TAG:?}
D=data/p2/train_depth3_f0_a1.jsonl; H=data/p2/heldout.jsonl
C="--mode lean_seq --lr 1e-3 --min_lr 1e-4 --warmup 200 --cap 6 --val_bins --log_every 200"
W=artifacts/fs/waves_$T.jsonl
run() { local name=$1 impl=$2 steps=$3 bs=$4; shift 4; local t=$(date +%s.%N) pids=""
  for s in "$@"; do rm -f artifacts/fs/m_${name}_s$s.jsonl
    python3 train.py --data $D --heldout $H $C --bs $bs --steps $steps --seed $s --impl $impl --out ckpts/fs/${name}_s$s.pt \
      --metrics artifacts/fs/m_${name}_s$s.jsonl > artifacts/fs/logs/${name}_s$s.log 2>&1 & pids="$pids $!"; done
  wait $pids
  echo "{\"wave\": \"$name\", \"impl\": \"$impl\", \"steps\": $steps, \"bs\": $bs, \"seeds\": \"$*\", \"n\": $#, \"gpu\": \"$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)\", \"wall_s\": $(python3 -c "import time; print(round(time.time() - $t, 2))")}" >> $W; }
run ${T}_warm fast 50 128 900          # builds the tokenised cache and warms the inductor cache; not reported
run ${T}_fast1 fast 2000 128 300
run ${T}_bs512 fast 500 512 301
run ${T}_fast2 fast 2000 128 302 303
run ${T}_leg1 legacy 500 128 304
touch artifacts/fs/gpubench_$T.done
