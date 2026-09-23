#!/usr/bin/env python3
"""Emit one pod's job plan for run ds-rendering.  One arm per pod; the plan is a list of groups separated by `--`
barriers, with at most two sampling jobs per group (efficiency run: peak memory ~6 GB per job at batch 2048, and
>2--3 co-tenant sampling jobs per 24 GB GPU is counterproductive).

  python3 pod/dsr/plan.py <arm>          # writes pod/dsr/plan_<arm>.txt and pod/dsr/mode_<arm>.txt

Held fixed in every arm: batch 2048, max_new 400, temperature 0.8, sampler path=fast/early=eos/compact/rowrng,
reward Lean AND nd_verify through lean_gate.py.  Stage order is base rates before dials before ladders, so that a
budget cut loses a ladder and never a base rate.
"""
import os, sys

MODE = {'c0': 'lean_seq', 'r1': 'lean_seq_noprem', 'r3': 'lean_seq_nofml', 'r2': 'lean_seq_intro'}
TRAIN = 'data/p2/train_depth3_f0_a1.jsonl'
HELD = 'data/p2/heldout.jsonl'
B = 2048          # THE batch, identical in every arm and every stage (efficiency run's caveat)
MN = 400          # max_new, identical everywhere
POOLS = [('d3', 'data/p2/targets_depth3.jsonl'), ('d3req', 'data/r3_1/depth3_req.jsonl'),
         ('red', 'data/p2/targets_reductio_req.jsonl')]


def ck(arm, s):
    return f'ckpts/dsr/stage1_a1_seq_s{s}.pt' if arm == 'c0' else f'ckpts/dsr/stage1_{arm}_s{s}.pt'


def plan(arm):
    m = MODE[arm]
    G = []
    if arm != 'c0':
        G.append([(f'stage1_{arm}_s{s}',
                   f'python3 train.py --data {TRAIN} --heldout {HELD} --mode {m} --steps 6000 --bs 128 --cap 6 '
                   f'--seed {s} --out {ck(arm, s)}') for s in (0, 1)])
    G.append([(f'held_{arm}_s{s}',
               f'python3 eval_set.py --ckpt {ck(arm, s)} --in {HELD} --k 1 --temperature 0 --batch {B} '
               f'--out artifacts/dsr/held_{arm}_s{s}.jsonl --summary artifacts/dsr/held_{arm}_s{s}.json') for s in (0, 1)])
    G.append([(f'mech_{arm}_s{s}',
               f'python3 eval_set.py --ckpt {ck(arm, s)} --in data/transfer.jsonl --k 16 --temperature 0.8 --seed 0 '
               f'--batch {B} --out artifacts/dsr/mech_{arm}_s{s}.jsonl --summary artifacts/dsr/mech_{arm}_s{s}.json')
              for s in (0, 1)])
    for tag, fn in POOLS:
        G.append([(f'cov_{tag}_{arm}_s{s}',
                   f'python3 coverage.py --ckpt {ck(arm, s)} --in {fn} --k 2000 --temperature 0.8 --seed 0 '
                   f'--batch {B} --max_new {MN} --procs 12 --lenfield min_lines_ub --path fast '
                   f'--out artifacts/dsr/cov_{tag}_{arm}_s{s}') for s in (0, 1)])
    ei = (f'python3 expert_iter.py --init {{ck}} --name dsr/{{nm}} --targets data/p2/targets_depth3.jsonl '
          f'--transfer data/p2/transfer_depth3.jsonl --heldout {HELD} --train {TRAIN} --rounds 4 --k 32 '
          f'--temperature 0.8 --batch {B} --seed {{s}} {{extra}}')
    G.append([(f'ei_d3_{arm}_s{s}', ei.format(ck=ck(arm, s), nm=f'ei_d3_{arm}_s{s}', s=s, extra='')) for s in (0, 1)])
    G.append([(f'frz_d3_{arm}_s{s}', ei.format(ck=ck(arm, s), nm=f'frz_d3_{arm}_s{s}', s=s, extra='--no_train')) for s in (0, 1)])
    la = (f'python3 ladder_ei.py --init {{ck}} --name {{nm}} --outdir artifacts/dsr --heldout {HELD} --train {TRAIN} '
          f'--rounds 8 --k 32 --temperature 0.8 --batch {B} --max_new {MN} --seed {{s}} {{extra}}')
    G.append([(f'la_T1_{arm}_s{s}', la.format(ck=ck(arm, s), nm=f'la_T1_{arm}_s{s}', s=s, extra='')) for s in (0, 1)])
    G.append([(f'la_frz_{arm}_s{s}', la.format(ck=ck(arm, s), nm=f'la_frz_{arm}_s{s}', s=s, extra='--no_train')) for s in (0, 1)])
    return G


def main():
    arm = sys.argv[1]
    d = os.path.dirname(os.path.abspath(__file__))
    with open(f'{d}/plan_{arm}.txt', 'w') as f:
        for gi, g in enumerate(plan(arm)):
            if gi:
                f.write('--\n')
            for name, cmd in g:
                f.write(f'{name}\t{cmd}\n')
    open(f'{d}/mode_{arm}.txt', 'w').write(MODE[arm] + '\n')
    print(f'wrote plan_{arm}.txt ({sum(len(g) for g in plan(arm))} jobs in {len(plan(arm))} groups), mode {MODE[arm]}')


if __name__ == '__main__':
    main()
