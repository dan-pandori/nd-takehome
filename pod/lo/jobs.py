#!/usr/bin/env python3
"""Job list of one pod role for run lean-only phase 2, lines '<jobname>\t<command>'.  python3 pod/lo/jobs.py <role>
Roles (fmt = seq | free, s = Stage-1 seed):
  la_<fmt>_s<s> : Stage-1 on the full cap-6 set (mode lean_<fmt>, seed s) -> held-out greedy + transfer pass@16 (mechanism test)
                  -> ladder rung T1 (EI seed s) + frozen control (seed s), then the checker of record on the counted proofs.
  d3_<fmt>      : Stage-1 on the depth-3 f=0 set a1, seeds 0 and 1 -> solo timing round -> EI + frozen (8 x 32) for both seeds
                  -> pre-RL base rates at pass@2,000 on the depth-3 targets for both seeds.
All arms sample with the Lean tokenizer; reward = lean_check (lean_gate.py); pools are the relabelled copies under data/lo/."""
import sys
role = sys.argv[1]
W = lambda f: f'until [ -f {f} ]; do sleep 30; done; '
J = []
LA = '--targets data/lo/la_rl_targets.jsonl --transfer data/lo/la_transfer.jsonl --outdir artifacts/lo --batch 512'
if role.startswith('la_'):
    _, fmt, s = role.split('_'); s = int(s[1:])
    ck = f'ckpts/lo/stage1_full_{fmt}_s{s}.pt'; tag = f'stage1_full_{fmt}_s{s}'
    J.append((tag, f'python3 train.py --data data/train.jsonl --heldout data/heldout.jsonl --mode lean_{fmt} --steps 6000 --bs 128 --out {ck} --cap 6 --seed {s}'))
    J.append((f'mech_full_{fmt}_s{s}', W(ck) + f'python3 eval_set.py --ckpt {ck} --in data/heldout.jsonl --out artifacts/lo/{tag}_heldout_greedy.jsonl --temperature 0 --batch 512 --summary artifacts/lo/{tag}_heldout_greedy.json && '
                                       f'python3 eval_set.py --ckpt {ck} --in data/transfer.jsonl --out artifacts/lo/{tag}_transfer2_k16.jsonl --k 16 --temperature 0.8 --seed 0 --batch 512 --summary artifacts/lo/{tag}_transfer2_k16.json'))
    J.append((f'la_T1_{fmt}_s{s}', W(ck) + f'python3 ladder_ei.py --init {ck} --name la_T1_{fmt}_s{s} {LA} --seed {s}'))
    J.append((f'la_frozen_{fmt}_s{s}', W(ck) + f'python3 ladder_ei.py --init {ck} --name la_frozen_{fmt}_s{s} {LA} --seed {s} --no_train'))
    J.append((f'record_la_{fmt}_s{s}', W(f'artifacts/lo/la_T1_{fmt}_s{s}.done') + W(f'artifacts/lo/la_frozen_{fmt}_s{s}.done') + f'python3 pod/lo/record.py artifacts/lo/la_T1_{fmt}_s{s} artifacts/lo/la_frozen_{fmt}_s{s}'))
elif role.startswith('d3_'):
    fmt = role.split('_')[1]
    D = 'data/p2'; common = f'--targets data/lo/targets_depth3.jsonl --transfer data/lo/transfer_depth3.jsonl --heldout {D}/heldout.jsonl --train {D}/train_depth3_f0_a1.jsonl --rounds 8 --k 32 --temperature 0.8 --batch 768'
    cks = [f'ckpts/lo/stage1_a1_{fmt}_s{s}.pt' for s in (0, 1)]
    for s in (0, 1):
        J.append((f'stage1_a1_{fmt}_s{s}', (W(cks[0]) if s == 1 else '') + f'python3 train.py --data {D}/train_depth3_f0_a1.jsonl --heldout {D}/heldout.jsonl --mode lean_{fmt} --steps 6000 --bs 128 --out {cks[s]} --cap 6 --seed {s}'))
    c1 = common.replace('--rounds 8', '--rounds 1')
    J.append((f'timing_d3_{fmt}', W(cks[0]) + W(cks[1]) + f'python3 expert_iter.py --init {cks[0]} --name lo/timing_d3_{fmt} {c1} --seed 0 --no_train'))
    for s in (0, 1):
        J.append((f'ei_d3_{fmt}_s{s}', W(f'artifacts/lo/timing_d3_{fmt}.done') + f'python3 expert_iter.py --init {cks[s]} --name lo/ei_d3_{fmt}_s{s} {common} --seed {s}'))
        J.append((f'frozen_d3_{fmt}_s{s}', W(f'artifacts/lo/timing_d3_{fmt}.done') + f'python3 expert_iter.py --init {cks[s]} --name lo/frozen_d3_{fmt}_s{s} {common} --seed {s} --no_train'))
    for s in (0, 1):
        J.append((f'base_d3_{fmt}_s{s}', W(f'artifacts/lo/timing_d3_{fmt}.done') + f'python3 eval_set.py --ckpt {cks[s]} --in data/lo/targets_depth3.jsonl --out artifacts/lo/base_d3_{fmt}_s{s}_k2000.jsonl --k 2000 --temperature 0.8 --seed {100 + s} --batch 1024 --summary artifacts/lo/base_d3_{fmt}_s{s}_k2000.json'))
    J.append((f'record_d3_{fmt}', ''.join(W(f'artifacts/lo/{a}_d3_{fmt}_s{s}.done') for a in ('ei', 'frozen') for s in (0, 1)) + f'python3 pod/lo/record.py ' + ' '.join(f'artifacts/lo/{a}_d3_{fmt}_s{s}' for a in ('ei', 'frozen') for s in (0, 1))))
else:
    raise SystemExit(f'unknown role {role}')
for n, c in J:
    print(f'{n}\t{c}')
