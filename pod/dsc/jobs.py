#!/usr/bin/env python3
"""Job list of one arm's pod for ds-composition: '<jobname>\t<command>'.   python3 pod/dsc/jobs.py <c0|a1|a2|a3|a4>
Per arm and Stage-1 seed s in {0, 1}:
  stage1_<arm>_s<s>   train.py --mode lean_seq --steps 6000 --bs 128 --cap {6|8} (A3: cap 8, labelled)      [c0: the lean-format checkpoints, not retrained]
  heldout_<arm>_s<s>  eval_set.py greedy on data/p2/heldout.jsonl (5,000; Lean-gated through sample.generate)
  cov_<arm>_s<s>_<pool>  coverage_lean.py --k 2000 --temperature 0.8 --seed 0 on depth3 (1,000), d3req (300), redreq (300)
  ei_<arm>_s<s> / frozen_<arm>_s<s>   expert_iter.py --rounds 4 --k 32 --temperature 0.8 [--no_train] on the depth-3 pool, --train = the arm's own set
  laT1_<arm>_s<s> / lafr_<arm>_s<s>   ladder_ei.py T1 / frozen, 8 x 32, --train = the arm's own set
  record_<arm>        pod/dsc/record.py: unmodified nd2lean.py --check on every counted proof (dial, ladder, coverage)
Waits (W) on checkpoint files keep the order without a queue. Every command runs under pod/dsc/job.sh (memory cap, Lean workers, gate log)."""
import sys
arm = sys.argv[1]
W = lambda f: f'until [ -f {f} ]; do sleep 30; done; '
D = 'data/p2'
train = {'c0': f'{D}/train_depth3_f0_a1.jsonl'}.get(arm, f'data/dsc/train_{arm}.jsonl')
cap = 8 if arm == 'a3' else 6
J = []
POOLS = {'depth3': f'{D}/targets_depth3.jsonl', 'd3req': 'data/r3_1/depth3_req.jsonl', 'redreq': f'{D}/targets_reductio_req.jsonl'}
for s in (0, 1):
    ck = f'ckpts/lf/stage1_a1_seq_s{s}.pt' if arm == 'c0' else f'ckpts/dsc/stage1_{arm}_s{s}.pt'
    if arm != 'c0':
        J.append((f'stage1_{arm}_s{s}', f'python3 train.py --data {train} --heldout {D}/heldout.jsonl --mode lean_seq --steps 6000 --bs 128 --out {ck} --cap {cap} --seed {s}'))
    J.append((f'heldout_{arm}_s{s}', W(ck) + f'python3 eval_set.py --ckpt {ck} --in {D}/heldout.jsonl --out artifacts/dsc/heldout_{arm}_s{s}.jsonl --temperature 0 --batch 512 --summary artifacts/dsc/heldout_{arm}_s{s}.json'))
    common = f'--targets {D}/targets_depth3.jsonl --transfer {D}/transfer_depth3.jsonl --heldout {D}/heldout.jsonl --train {train} --rounds 4 --k 32 --temperature 0.8 --batch 768'
    J.append((f'ei_{arm}_s{s}', W(ck) + f'python3 expert_iter.py --init {ck} --name dsc/ei_{arm}_s{s} {common} --seed {s}'))
    J.append((f'frozen_{arm}_s{s}', W(ck) + f'python3 expert_iter.py --init {ck} --name dsc/frozen_{arm}_s{s} {common} --seed {s} --no_train'))
    J.append((f'laT1_{arm}_s{s}', W(ck) + f'python3 ladder_ei.py --init {ck} --name la_T1_{arm}_s{s} --outdir artifacts/dsc --train {train} --heldout {D}/heldout.jsonl --seed {s} --batch 512'))
    J.append((f'lafr_{arm}_s{s}', W(ck) + f'python3 ladder_ei.py --init {ck} --name la_frozen_{arm}_s{s} --outdir artifacts/dsc --train {train} --heldout {D}/heldout.jsonl --seed {s} --batch 512 --no_train'))
    for pool, fn in POOLS.items():
        J.append((f'cov_{arm}_s{s}_{pool}', W(ck) + f'python3 coverage_lean.py --ckpt {ck} --in {fn} --k 2000 --temperature 0.8 --seed 0 --batch 1024 --procs 4 --out artifacts/dsc/cov_{arm}_s{s}_{pool}'))
J.append((f'record_{arm}', f'python3 pod/dsc/record.py {arm}'))
for n, c in J:
    print(f'{n}\t{c}')
