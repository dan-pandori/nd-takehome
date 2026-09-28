#!/usr/bin/env bash
# C deep pass, T 1.0 only, explicit list (rebalancing shard 1's T 1.0 list across two pods). Usage: NAMES=f TAG=t SEED=s WAIT=pattern bash pod/sf/c3_only.sh
cd /workspace/nd-takehome; export PATH=$HOME/.elan/bin:$PATH LEAN_GATE_WORKERS=${LGW:-8}
[ -n "$WAIT" ] && while pgrep -f "$WAIT" >/dev/null; do sleep 30; done
python3 support.py --ckpt ckpts/sf/stage1_big_seq_s0.pt --model big --stage c2 --names $NAMES --k 200000 --stop_at 5 --temperature 1.0 \
  --seed $SEED --model_seed 0 --batch ${BATCH:-1024} --max_new 512 --shard 0/1 --out artifacts/sf/c2_big_T10_s0_$TAG > artifacts/sf/logs/c2_T10_$TAG.log 2>&1
echo C3_DONE $TAG
