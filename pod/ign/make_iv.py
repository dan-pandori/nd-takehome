#!/usr/bin/env python3
"""Emit runq job lines for the three interventions on one non-ignited arm.
  python pod/ign/make_iv.py <set: depth3|reductio> <seed> <sibling seed> <r4 init ckpt>
"""
import sys
S, seed, sib, init = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
if S == 'depth3':
    arm = f'ei_depth3_f0_a1_s{seed}'; sibarm = f'ei_depth3_f0_a1_s{sib}'
    common = '--targets data/p2/targets_depth3.jsonl --transfer data/p2/transfer_depth3.jsonl --heldout data/p2/heldout.jsonl --train data/p2/train_depth3_f0_a1.jsonl'
    train = 'data/p2/train_depth3_f0_a1.jsonl'
else:
    arm = f'ei_reductio_f0_s{seed}_t2'; sibarm = f'ei_reductio_f0_s{sib}_t2'
    common = '--targets data/p2/targets_reductio2.jsonl --transfer data/p2/transfer_reductio2.jsonl --heldout data/p2/heldout.jsonl --train data/p2/train_reductio_f0.jsonl'
    train = 'data/p2/train_reductio_f0.jsonl'
ei = f'python3 expert_iter.py {common} --seed {seed} --batch 768'
print(f'{arm}_ivK {ei} --init {init} --name p2/{arm}_ivK --start_round 5 --rounds 1 --k 128 --temperature 0.8 --resume_found artifacts/p2/{arm} && {ei} --init ckpts/p2/{arm}_ivK_r5.pt --name p2/{arm}_ivK --start_round 6 --rounds 3 --k 32 --temperature 0.8 --resume_found artifacts/p2/{arm}_ivK')
print(f'{arm}_ivT {ei} --init {init} --name p2/{arm}_ivT --start_round 5 --rounds 1 --k 32 --temperature 1.0 --resume_found artifacts/p2/{arm} && {ei} --init ckpts/p2/{arm}_ivT_r5.pt --name p2/{arm}_ivT --start_round 6 --rounds 3 --k 32 --temperature 0.8 --resume_found artifacts/p2/{arm}_ivT')
print(f'{arm}_ivS python3 ignition_transfer_mix.py --own artifacts/p2/{arm} --sibling artifacts/p2/{sibarm} --train {train} --init {init} --out ckpts/p2/{arm}_ivS_r4t.pt --seed {seed} && {ei} --init ckpts/p2/{arm}_ivS_r4t.pt --name p2/{arm}_ivS --start_round 5 --rounds 4 --k 32 --temperature 0.8 --resume_found artifacts/p2/{arm}')
