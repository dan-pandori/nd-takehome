#!/usr/bin/env bash
# Smoke tests of the fast path's other modes (run fast-stage1): --state_at/--resume continuation, --impl auto
# choices, --no_graph, --no_pack, lean_rand.  400 steps each; log artifacts/fs/logs/smoke.log.
cd /workspace/nd-takehome; export OMP_NUM_THREADS=4
D=data/p2/train_depth3_f0_a1.jsonl; H=data/p2/heldout.jsonl
C="--mode lean_seq --bs 128 --cap 6 --steps 400 --warmup 50 --log_every 100 --heldout $H"
{
python3 train.py --data $D $C --seed 5 --state_at 200 --out ckpts/fs/sm_full.pt | grep -E "impl|^step 400|saved state"
python3 train.py --data $D $C --seed 5 --resume ckpts/fs/sm_full.state00200.pt --out ckpts/fs/sm_res.pt | grep -E "impl|resumed|^step 400"
python3 train.py --data $D $C --seed 5 --no_graph --out ckpts/fs/sm_nog.pt | grep -E "impl|^step 400"
python3 train.py --data $D $C --seed 5 --no_pack --out ckpts/fs/sm_nop.pt | grep -E "impl|^step 400"
python3 train.py --data $D --heldout $H --mode lean_rand --bs 128 --cap 6 --steps 400 --warmup 50 --log_every 100 --seed 5 --out ckpts/fs/sm_rand.pt | grep -E "impl|^step 400"
python3 train.py --data $D $C --seed 5 --steps 50 --init ckpts/fs/sm_full.pt --out ckpts/fs/sm_init.pt | grep -E "^params|^step 50"
echo SMOKE_DONE
} > artifacts/fs/logs/smoke.log 2>&1
