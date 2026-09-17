#!/usr/bin/env python3
"""Emit run-4 job lines (pod/r4/runq.sh format) for a list of Stage-1 draws.  python3 pod/r4/make_jobs.py 20 21 [--lrgrid]"""
import sys
POOLS = '--targets data/p2/targets_depth3.jsonl --transfer data/p2/transfer_depth3.jsonl --heldout data/p2/heldout.jsonl'
GRPO = f'python3 grpo.py {POOLS} --batch 800 --updates_per_round 40 --rounds 8 --temperature 0.8 --micro 200'
EI = f'python3 expert_iter.py {POOLS} --train data/p2/train_depth3_f0_a1.jsonl --rounds 8 --k 32 --temperature 0.8 --batch 768'
COV = 'python3 coverage.py --in data/p2/targets_depth3.jsonl --k 2000 --temperature 0.8 --limit 300 --batch 2000 --seed 0 --procs 2'
draws = [int(x) for x in sys.argv[1:] if x.isdigit()]
lrgrid = '--lrgrid' in sys.argv
lines = []
for s in draws:
    ck = f'ckpts/r4/stage1_depth3_f0_a1_s{s}.pt'
    wait = f'until [ -f {ck} ]; do sleep 30; done; sleep 20;'
    tag = f'depth3_f0_a1_s{s}'
    for e, seed in (('', s), ('_e2', s + 100)):
        for G in (8, 32):
            for lr, lt in (('1e-4', ''), ('3e-5', '_lr3e-5')):
                lines.append(f'grpo_g{G}_{tag}{lt}{e} {wait} {GRPO} --init {ck} --name r4/grpo_g{G}_{tag}{lt}{e} --group {G} --lr {lr} --seed {seed}')
        lines.append(f'ei_{tag}{e} {wait} {EI} --init {ck} --name r4/ei_{tag}{e} --seed {seed}')
    lines.append(f'frozen_{tag} {wait} {EI} --init {ck} --name r4/frozen_{tag} --seed {s} --no_train')
    lines.append(f'cov_{tag} {wait} {COV} --ckpt {ck} --out artifacts/r4/cov_{tag}')
    if lrgrid:
        for lr in ('1e-5', '3e-4'):
            for G in (8, 32):
                lines.append(f'grpo_g{G}_{tag}_lr{lr} {wait} {GRPO} --init {ck} --name r4/grpo_g{G}_{tag}_lr{lr} --group {G} --lr {lr} --seed {s}')
# order: primary arms first (seed 1 grpo + ei for every draw), then frozen/cov, then second seeds, then lr grid
prio = lambda l: (0 if (l.startswith('grpo') and '_e2' not in l and ('_lr' not in l or '_lr3e-5' in l)) else 1 if (l.startswith('ei') and '_e2' not in l) else 2 if l.startswith(('frozen', 'cov')) else 3 if '_e2' in l else 4)
for l in sorted(lines, key=prio):
    print(l)
