#!/usr/bin/env python3
"""Job list for run lean-seed2, lines '<jobname>\t<command>'.  python3 pod/ls2/jobs.py <a|b>
a : Stage-1 lean_seq seed 2 on the full cap-6 set, held-out greedy + transfer pass@16, ladder T1 s0 + frozen s0, checker of record.
b : ladder T1 s1 + frozen s1 from the copied Stage-1 checkpoint, checker of record.
'seq2' in arm names = lean_seq Stage-1 model seed 2 (proposal 8's arms la_T1_seq_s{0,1} are from Stage-1 seed 0)."""
import sys
role = sys.argv[1]
W = lambda f: f'until [ -f {f} ]; do sleep 30; done; '
ck = 'ckpts/lf/stage1_full_seq_s2.pt'
J = []
if role == 'a':
    J.append(('stage1_full_seq_s2', f'python3 train.py --data data/train.jsonl --heldout data/heldout.jsonl --mode lean_seq --steps 6000 --bs 128 --out {ck} --cap 6 --seed 2'))
    tag = 'stage1_full_seq_s2'
    J.append(('mech_full_seq_s2', W(ck) + f'python3 eval_set.py --ckpt {ck} --in data/heldout.jsonl --out artifacts/lf/{tag}_heldout_greedy.jsonl --temperature 0 --batch 512 --summary artifacts/lf/{tag}_heldout_greedy.json && '
                                  f'python3 eval_set.py --ckpt {ck} --in data/transfer.jsonl --out artifacts/lf/{tag}_transfer2_k16.jsonl --k 16 --temperature 0.8 --seed 0 --batch 512 --summary artifacts/lf/{tag}_transfer2_k16.json'))
seeds = (0,) if role == 'a' else (1,)
for s in seeds:
    J.append((f'la_T1_seq2_s{s}', W(ck) + f'python3 ladder_ei.py --init {ck} --name la_T1_seq2_s{s} --outdir artifacts/lf --seed {s} --batch 512'))
    J.append((f'la_frozen_seq2_s{s}', W(ck) + f'python3 ladder_ei.py --init {ck} --name la_frozen_seq2_s{s} --outdir artifacts/lf --seed {s} --batch 512 --no_train'))
    J.append((f'record_seq2_s{s}', W(f'artifacts/lf/la_T1_seq2_s{s}.done') + W(f'artifacts/lf/la_frozen_seq2_s{s}.done') + f'python3 pod/lf/record.py artifacts/lf/la_T1_seq2_s{s} artifacts/lf/la_frozen_seq2_s{s}'))
for n, c in J:
    print(f'{n}\t{c}')
