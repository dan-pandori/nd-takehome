#!/usr/bin/env python3
"""Resume phase (2026-09-23) job list of one arm as lines '<jobname>\t<dep1,dep2|->\t<command>'.
  python3 pod/dsg/jobs2.py <c0|g1|g2>

The 2026-09-22 session was cut off before any ladder job finished and the host cleanup then deleted ckpts/.
This phase therefore: (regress) checks the adopted fast decode path is a no-op against this branch's base path;
(fetch/stage1) re-fetches the arm's training set from the bucket and retrains its two Stage-1 checkpoints, with a
held-out greedy re-measurement as the reproduction check against the committed heldout_<arm>_s<seed>.json;
(ladder) runs T1 and frozen, 8 rounds x k 32, two seeds; (record) the checker of record over every counted proof.

Jobs are chained so that exactly ONE sampling job runs per GPU: run `efficiency` measured 1,395 samples/s for a
solo job at batch 4,096 against 964 for four co-tenants at batch 1,024.  The batch (4,096) and max_new (384) are
held fixed across all three arms."""
import sys
arm = sys.argv[1]
D = 'data/p2'
SET = f'{D}/train_depth3_f0_a1.jsonl' if arm == 'c0' else f'data/dsg/train_{arm}.jsonl'
CK = (lambda s: f'ckpts/lf/stage1_a1_seq_s{s}.pt') if arm == 'c0' else (lambda s: f'ckpts/dsg/stage1_{arm}_s{s}.pt')
BUCKET = 'hf://buckets/dan-pandori/nd-rl/ds-generator'
J = [('regress', '-', f'python3 dsg_regress.py {CK(0) if arm == "c0" else "ckpts/lf/stage1_a1_seq_s0.pt"}')]
prev = 'regress'
if arm != 'c0':
    J.append((f'fetch_{arm}', '-', f'hf buckets cp {BUCKET}/data/dsg/train_{arm}.jsonl {SET} && wc -l {SET}'))
    for s in (0, 1):
        J.append((f'stage1_{arm}_s{s}', f'fetch_{arm},{prev}',
                  f'python3 train.py --data {SET} --heldout {D}/heldout.jsonl --mode lean_seq --steps 6000 --bs 128 '
                  f'--out {CK(s)} --cap 6 --seed {s}'))
        prev = f'stage1_{arm}_s{s}'
    for s in (0, 1):
        J.append((f'heldout2_{arm}_s{s}', prev,
                  f'python3 eval_set.py --ckpt {CK(s)} --in {D}/heldout.jsonl --out artifacts/dsg/heldout2_{arm}_s{s}.jsonl '
                  f'--k 1 --temperature 0 --batch 512 --summary artifacts/dsg/heldout2_{arm}_s{s}.json'))
        prev = f'heldout2_{arm}_s{s}'
# ladder: one sampling job at a time on the GPU, batch 4096 / max_new 384 (fast decode path), 8 rounds x k 32
for s in (0, 1):
    la = (f'python3 ladder_ei.py --init {CK(s)} --outdir artifacts/dsg --seed {s} --batch 4096 --max_new 384 '
          f'--train {SET} --heldout {D}/heldout.jsonl')
    for kind, extra in (('la_T1', ''), ('la_frozen', ' --no_train')):
        name = f'{kind}_{arm}_s{s}'
        J.append((name, prev, f'{la} --name {name}{extra}'))
        prev = name
J.append((f'record_{arm}', prev, f'python3 pod/dsg/record.py {arm}'))
for n, d, c in J:
    print(f'{n}\t{d}\t{c}')
