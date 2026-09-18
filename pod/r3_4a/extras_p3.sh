#!/usr/bin/env bash
# round3-run4a EXPLORATORY extras (not pre-registered; labelled as such everywhere):
#  C: 85M-A s0 EI at the brief's suggested ft_lr 3e-5 (sensitivity of the ignition / wall result to my ft_lr 1e-4 choice)
#  B: 85M-A s2 (non-zero base rate 1e-5, 0 / 300 after 8 rounds) continued for rounds 9-16 from its found files
set -e
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
A=artifacts/r3_4a; T=data/p2/targets_reductio_req.jsonl; TR=data/p2/transfer_reductio_req.jsonl
COMMON="--targets $T --transfer $TR --heldout data/p2/heldout.jsonl --train data/r3_4a/train_reductio_f0_b1.jsonl --k 32 --temperature 0.8 --retain 20000 --max_per_thm 4 --ft_steps 600 --batch 1024"
[ -f ckpts/r3_4a/stage1_reductio_f0_b1_m85_s0.pt ] || hf buckets cp hf://buckets/dan-pandori/nd-rl/round3-run4a/ckpts/r3_4a/stage1_reductio_f0_b1_m85_s0.pt ckpts/r3_4a/stage1_reductio_f0_b1_m85_s0.pt
if [ ! -f $A/x_lr3e-5_m85_s0.done ]; then
  python3 expert_iter.py --init ckpts/r3_4a/stage1_reductio_f0_b1_m85_s0.pt --name r3_4a/x_ei_m85_s0_lr3e-5 $COMMON --rounds 8 --ft_lr 3e-5 --seed 0 > $A/x_ei_m85_s0_lr3e-5.log 2>&1
  ls ckpts/r3_4a/x_ei_m85_s0_lr3e-5_r*.pt 2>/dev/null | sort -V | head -n -1 | xargs -r rm -f; touch $A/x_lr3e-5_m85_s0.done
fi
if [ ! -f $A/x_r16_m85_s2.done ]; then
  python3 expert_iter.py --init ckpts/r3_4a/stage1_reductio_f0_b1_m85_s2.pt --name r3_4a/x_ei_m85_s2_r9-16 $COMMON --rounds 8 --start_round 9 --resume_found $A/ei_m85_s2 --ft_lr 1e-4 --seed 2 > $A/x_ei_m85_s2_r9-16.log 2>&1
  ls ckpts/r3_4a/x_ei_m85_s2_r9-16_r*.pt 2>/dev/null | sort -V | head -n -1 | xargs -r rm -f; touch $A/x_r16_m85_s2.done
fi
