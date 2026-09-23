#!/usr/bin/env python3
"""Job list of one arm's pod for ds-composition: '<jobname>\t<command>'.
    python3 pod/dsc/jobs.py <c0|a1|a2|a3|a4> [all|stage1|queue]

  all     every job (default)
  stage1  the two Stage-1 trainings only (empty for c0: the control uses the lean-format checkpoints, never retrained)
  queue   everything else, in the priority order the pod-side runner (pod/dsc/runner.sh, 3 at a time) consumes:
            held-out greedy -> dial (EI + frozen, 2 seeds) -> ladder (T1 + frozen, 2 seeds) -> coverage -> checker of record
          The tail (coverage d3sub, then d3req) is what the stop rule drops; the ladder and the dial come first because
          falsifiers 1 and 2 are read off them.

Per arm and Stage-1 seed s in {0, 1}:
  stage1_<arm>_s<s>   train.py --mode lean_seq --steps 6000 --bs 128 --cap {6|8} (A3: cap 8, labelled)
  heldout_<arm>_s<s>  eval_set.py greedy on data/p2/heldout.jsonl (5,000; Lean-gated through sample.generate)
  ei_<arm>_s<s> / frozen_<arm>_s<s>   expert_iter.py --rounds 4 --k 32 --temperature 0.8 [--no_train], depth-3 pool
  laT1_<arm>_s<s> / lafr_<arm>_s<s>   ladder_ei.py T1 / frozen, 8 x 32, --train = the arm's own set
  cov_<arm>_s<s>_<pool>  coverage_lean.py --k 2000 --temperature 0.8 --seed 0 on redreq (300), d3req (300), d3sub (250)
  record_<arm>        pod/dsc/record.py: unmodified nd2lean.py --check on every counted proof (dial, ladder, coverage)

Batch sizes are held FIXED across every arm (heldout 512, dial 768, ladder 512, coverage 1024) -- a batch change
reshuffles which proofs are accepted about as much as an RNG re-draw (run efficiency, 2026-09-23), so arms are only
comparable at one batch.  The decode path is sample.py's fast path (path=fast, early=eos, compact, rowrng) everywhere.
"""
import sys
arm = sys.argv[1]
which = sys.argv[2] if len(sys.argv) > 2 else 'all'
W = lambda f: f'until [ -f {f} ]; do sleep 30; done; '
D = 'data/p2'
train = {'c0': f'{D}/train_depth3_f0_a1.jsonl'}.get(arm, f'data/dsc/train_{arm}.jsonl')
cap = 8 if arm == 'a3' else 6
POOLS = [('redreq', f'{D}/targets_reductio_req.jsonl'), ('d3req', 'data/r3_1/depth3_req.jsonl'),
         ('d3sub', 'data/dsc/targets_depth3_sub250.jsonl')]   # d3sub: 250-target random subset (seed 0) of targets_depth3.jsonl (amendment 2)
CK = lambda s: f'ckpts/lf/stage1_a1_seq_s{s}.pt' if arm == 'c0' else f'ckpts/dsc/stage1_{arm}_s{s}.pt'

stage1 = [] if arm == 'c0' else [
    (f'stage1_{arm}_s{s}',
     f'python3 train.py --data {train} --heldout {D}/heldout.jsonl --mode lean_seq --steps 6000 --bs 128 '
     f'--out {CK(s)} --cap {cap} --seed {s}') for s in (0, 1)]

queue = []
for s in (0, 1):
    queue.append((f'heldout_{arm}_s{s}', W(CK(s)) + f'python3 eval_set.py --ckpt {CK(s)} --in {D}/heldout.jsonl '
                  f'--out artifacts/dsc/heldout_{arm}_s{s}.jsonl --temperature 0 --batch 512 '
                  f'--summary artifacts/dsc/heldout_{arm}_s{s}.json'))
dial = f'--targets {D}/targets_depth3.jsonl --transfer {D}/transfer_depth3.jsonl --heldout {D}/heldout.jsonl --train {train} --rounds 4 --k 32 --temperature 0.8 --batch 768'
for s in (0, 1):
    queue.append((f'ei_{arm}_s{s}', W(CK(s)) + f'python3 expert_iter.py --init {CK(s)} --name dsc/ei_{arm}_s{s} {dial} --seed {s}'))
    queue.append((f'frozen_{arm}_s{s}', W(CK(s)) + f'python3 expert_iter.py --init {CK(s)} --name dsc/frozen_{arm}_s{s} {dial} --seed {s} --no_train'))
la = f'--outdir artifacts/dsc --train {train} --heldout {D}/heldout.jsonl --batch 512'
for s in (0, 1):
    queue.append((f'laT1_{arm}_s{s}', W(CK(s)) + f'python3 ladder_ei.py --init {CK(s)} --name la_T1_{arm}_s{s} {la} --seed {s}'))
    queue.append((f'lafr_{arm}_s{s}', W(CK(s)) + f'python3 ladder_ei.py --init {CK(s)} --name la_frozen_{arm}_s{s} {la} --seed {s} --no_train'))
for pool, fn in POOLS:
    for s in (0, 1):
        queue.append((f'cov_{arm}_s{s}_{pool}', W(CK(s)) + f'python3 coverage_lean.py --ckpt {CK(s)} --in {fn} --k 2000 '
                      f'--temperature 0.8 --seed 0 --batch 1024 --procs 2 --out artifacts/dsc/cov_{arm}_s{s}_{pool}'))
queue.append((f'record_{arm}', f'python3 pod/dsc/record.py {arm}'))

J = {'all': stage1 + queue, 'stage1': stage1, 'queue': queue}[which]
for n, c in J:
    print(f'{n}\t{c}')
