#!/usr/bin/env python3
import sys
POOLS = '--targets data/p2/targets_depth3.jsonl --transfer data/p2/transfer_depth3.jsonl --heldout data/p2/heldout.jsonl'
for s in [int(x) for x in sys.argv[1:]]:
    ck = f'ckpts/r4/stage1_depth3_f0_a1_s{s}.pt'; tag = f'depth3_f0_a1_s{s}'
    wait = f'until [ -f {ck} ]; do sleep 30; done; sleep 20;'
    for lr in ('1e-4', '1e-5'):
        print(f'grpo_sprint_{tag}_lr{lr} {wait} python3 grpo.py {POOLS} --init {ck} --name r4/grpo_sprint_{tag}_lr{lr} --group 8 --batch 32 --updates_per_round 100 --rounds 1 --lr {lr} --temperature 0.8 --seed {s} --k_eval 32')
