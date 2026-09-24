#!/usr/bin/env python3
"""Job list of one arm's pod for cap-horizon: '<jobname>\t<command>'.
    python3 pod/kh/jobs.py <k8add|k10|k12|k14> [all|stage1|queue]

Arms are the CAP arms: k8add cap 8 (217,000 records), k10 cap 10, k12 cap 12, k14 cap 14 (155,000 each).
K6 (cap 6) and K8flat (cap 8) are NOT here: they are inherited from the lean-format and ds-composition
buckets and never retrained.

Per arm and Stage-1 seed s in {0, 1}:
  stage1_<arm>_s<s>   train.py --mode lean_seq --steps 6000 --bs 128 --cap <the arm's cap>
  heldout_<arm>_s<s>  eval_set.py greedy on data/p2/heldout.jsonl (5,000) -- the CAP-6 distribution,
                      so every arm above cap 6 is measured OUT OF DISTRIBUTION on it (comparability
                      check, not a headline)
  laT1_<arm>_s0 / lafr_<arm>_s0   ladder_ei.py rung T1 / frozen at equal attempts, 8 rounds x k 32,
                      seed 0 only (budget); the frozen number is reported beside every T1 number
  cov_<arm>_s<s>_<pool>  coverage_lean.py --k 2000 --temperature 0.8 --seed 0 on redreq (300) and
                      d3req (300)
  record_<arm>        pod/kh/record.py: unmodified nd2lean.py --check on every counted proof

The depth-3 dial and the d3sub250 pool are deliberately NOT run (run brief: three runs agree EI's
round-4 endpoint is base-rate-insensitive; the budget goes to the horizon instead).

Batch sizes and decode settings are held FIXED across every arm AND equal to ds-composition's, so
the inherited K6 / K8flat numbers stay comparable: held-out 512, ladder 512, coverage 1024,
max_new 400 (coverage) / 512 (ladder), sample.py's fast path.
"""
import sys
arm = sys.argv[1]
which = sys.argv[2] if len(sys.argv) > 2 else 'all'
W = lambda f: f'until [ -f {f} ]; do sleep 30; done; '
D = 'data/p2'
CAP = {'k8add': 8, 'k10': 10, 'k12': 12, 'k14': 14}[arm]
train = f'data/kh/train_{arm}.jsonl'
POOLS = [('redreq', f'{D}/targets_reductio_req.jsonl'), ('d3req', 'data/r3_1/depth3_req.jsonl')]
CK = lambda s: f'ckpts/kh/stage1_{arm}_s{s}.pt'

stage1 = [(f'stage1_{arm}_s{s}',
           f'python3 train.py --data {train} --heldout {D}/heldout.jsonl --mode lean_seq --steps 6000 --bs 128 '
           f'--out {CK(s)} --cap {CAP} --seed {s}') for s in (0, 1)]

queue = []
for s in (0, 1):
    queue.append((f'heldout_{arm}_s{s}', W(CK(s)) + f'python3 eval_set.py --ckpt {CK(s)} --in {D}/heldout.jsonl '
                  f'--out artifacts/kh/heldout_{arm}_s{s}.jsonl --temperature 0 --batch 512 '
                  f'--summary artifacts/kh/heldout_{arm}_s{s}.json'))
la = f'--outdir artifacts/kh --train {train} --heldout {D}/heldout.jsonl --batch 512'
queue.append((f'laT1_{arm}_s0', W(CK(0)) + f'python3 ladder_ei.py --init {CK(0)} --name la_T1_{arm}_s0 {la} --seed 0'))
queue.append((f'lafr_{arm}_s0', W(CK(0)) + f'python3 ladder_ei.py --init {CK(0)} --name la_frozen_{arm}_s0 {la} --seed 0 --no_train'))
for pool, fn in POOLS:
    for s in (0, 1):
        queue.append((f'cov_{arm}_s{s}_{pool}', W(CK(s)) + f'python3 coverage_lean.py --ckpt {CK(s)} --in {fn} --k 2000 '
                      f'--temperature 0.8 --seed 0 --batch 1024 --procs 2 --out artifacts/kh/cov_{arm}_s{s}_{pool}'))
queue.append((f'record_{arm}', f'python3 pod/kh/record.py {arm}'))

J = {'all': stage1 + queue, 'stage1': stage1, 'queue': queue}[which]
for n, c in J:
    print(f'{n}\t{c}')
