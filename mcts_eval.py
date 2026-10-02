#!/usr/bin/env python3
"""mcts_eval.py -- one PUCT search read-out: a checkpoint, a pool, an arm, a wall-clock budget (run `mcts-a`).

  python mcts_eval.py --ckpt la_T1_best12_s0_r8.pt --in data/mcts/groupC_s0.jsonl --arm value \
      --value ckpts/mcts/value_s0_r8.pt --budget_s 400 --out artifacts/mcts/eval/s0_r8__C__value.jsonl

Arms: `prior` (PUCT with the policy prior and progressive sampling, v = 0 at non-terminal leaves; proposal 20's E1) and
`value` (the same with the learned value).  Every tree of the pool is searched together; the job's wall clock --
sampling, environment, Lean -- is its GPU-seconds (one job per GPU), and the budget is the matched plain-sampling
read-out's wall clock on the same pool, checkpoint and GPU.  Per theorem: solved, the wall / GPU-seconds at which the
proof was found (the anytime curve), nodes, expansions, sampled actions, tokens, Lean checks, and along the found proof
each step's prior rank and probability (where the hard steps sit).  GPU utilisation is sampled with nvidia-smi.
"""
import argparse, json, os, subprocess, sys, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import mcts


class GpuUtil:
    """nvidia-smi utilization.gpu every second, in a thread."""

    def __init__(self):
        self.x = []
        self.stop = False
        self.t = threading.Thread(target=self.run, daemon=True)

    def run(self):
        while not self.stop:
            try:
                o = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                                   capture_output=True, text=True, timeout=5).stdout.split()
                if o:
                    self.x.append(float(o[0]))
            except Exception:
                pass
            time.sleep(1.0)

    def __enter__(self):
        self.t.start(); return self

    def __exit__(self, *a):
        self.stop = True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--arm', choices=('prior', 'value'), required=True)
    ap.add_argument('--value', default=None)
    ap.add_argument('--budget_s', type=float, required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--cfg', default='{}', help='json overrides of mcts.DEFAULT')
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    from model import load_ckpt
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model, tok, extra = load_ckpt(a.ckpt, dev)
    head = None
    if a.arm == 'value':
        import value_head
        head = value_head.load(a.value, dev)
    recs = [json.loads(l) for l in open(a.inp) if l.strip()]
    if a.limit:
        recs = recs[:a.limit]
    cfg = dict(max_expansions=10 ** 9)
    cfg.update(json.loads(a.cfg))
    if head is not None:
        cfg['gamma'] = head.gamma
    log = lambda s: print(s, flush=True)
    with GpuUtil() as gu:
        out, st = mcts.run_search(model, tok, [r['prompt'] for r in recs], cfg=cfg, value=head, seed=a.seed,
                                  budget_s=a.budget_s, log=log)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    with open(a.out, 'w') as f:
        for r, o in zip(recs, out):
            o = dict(o); o['name'] = r.get('name'); o['prompt'] = r['prompt']
            f.write(json.dumps(o) + '\n')
    c = dict(mcts.DEFAULT); c.update(cfg)
    summ = dict(ckpt=a.ckpt, inp=a.inp, arm=a.arm, value=a.value, budget_s=a.budget_s, seed=a.seed, cfg=c,
                n=len(recs), solved=sum(o['solved'] for o in out), stats=st,
                gpu_util_mean=(sum(gu.x) / len(gu.x)) if gu.x else None, gpu_util_samples=len(gu.x),
                lean_checks=sum(o['lean_checks'] for o in out), sampled=sum(o['sampled'] for o in out),
                expansions=sum(o['expansions'] for o in out), nodes=sum(o['nodes'] for o in out))
    if dev == 'cuda':
        summ['peak_alloc_gb'] = torch.cuda.max_memory_allocated() / 2 ** 30
        summ['gpu'] = torch.cuda.get_device_name(0)
    json.dump(summ, open(a.out.replace('.jsonl', '.json'), 'w'), indent=1)
    print('SUMMARY', json.dumps({k: v for k, v in summ.items() if k not in ('cfg', 'stats')}))


if __name__ == '__main__':
    main()
