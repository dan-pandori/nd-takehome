#!/usr/bin/env python3
"""Job lines for round3-run1 (pod/r3_1/runq.sh format).

  python pod/r3_1/make_jobs.py cov depth3 20 21 ...     # pre-RL sample: coverage k=2000 over all 300 required targets of the pattern
  python pod/r3_1/make_jobs.py arms depth3 req|mix|drift 20 21 ...   # EI arms
  python pod/r3_1/make_jobs.py drift_cov depth3 20 ...  # coverage k=1000 on the required pool from drift checkpoints r2 r4 r6 r8
"""
import sys
pat = sys.argv[2]
CK = {'depth3': 'ckpts/r3_1/stage1_depth3_f0_a1_s{s}.pt', 'reductio': 'ckpts/r3_1/stage1_reductio_f0_s{s}.pt'}
TRAIN = {'depth3': 'data/p2/train_depth3_f0_a1.jsonl', 'reductio': 'data/p2/train_reductio_f0.jsonl'}
REQ = {'depth3': 'data/r3_1/depth3_req.jsonl', 'reductio': 'data/r3_1/reductio_req.jsonl'}
TR = {'depth3': 'data/r3_1/depth3_req_transfer.jsonl', 'reductio': 'data/r3_1/reductio_req_transfer.jsonl'}
POOL = {'req': REQ, 'mix': {'depth3': 'data/r3_1/depth3_mix.jsonl', 'reductio': 'data/r3_1/reductio_mix.jsonl'},
        'drift': {'depth3': 'data/r3_1/depth3_nb.jsonl', 'reductio': 'data/r3_1/reductio_nb.jsonl'}}
cmd = sys.argv[1]
if cmd == 'cov':
    for s in sys.argv[3:]:
        ck = CK[pat].format(s=s)
        print(f'cov_{pat}_s{s} until [ -f {ck} ]; do sleep 60; done; sleep 30; python3 coverage.py --ckpt {ck} --in {REQ[pat]} --out artifacts/r3_1/cov_{pat}_s{s} --k 2000 --temperature 0.8 --batch 2000 --seed 0 --procs 2')
elif cmd == 'arms':
    arm = sys.argv[3]
    for s in sys.argv[4:]:
        ck = CK[pat].format(s=s)
        extra = f' --exclude_pattern {pat}' if arm == 'drift' else ''
        print(f'ei_{pat}_s{s}_{arm} python3 expert_iter.py --init {ck} --name r3_1/ei_{pat}_s{s}_{arm} --targets {POOL[arm][pat]} --transfer {TR[pat]} '
              f'--heldout data/p2/heldout.jsonl --train {TRAIN[pat]} --rounds 8 --k 32 --temperature 0.8 --seed {s} --batch 768{extra}')
elif cmd == 'drift_cov':
    for s in sys.argv[3:]:
        for r in (2, 4, 6, 8):
            ck = f'ckpts/r3_1/ei_{pat}_s{s}_drift_r{r}.pt'
            print(f'dcov_{pat}_s{s}_r{r} until [ -f {ck} ]; do sleep 60; done; sleep 20; python3 coverage.py --ckpt {ck} --in {REQ[pat]} --out artifacts/r3_1/dcov_{pat}_s{s}_r{r} --k 1000 --temperature 0.8 --batch 1000 --seed 0 --procs 2')
