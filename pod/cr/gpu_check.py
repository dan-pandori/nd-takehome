#!/usr/bin/env python3
"""compute-record GPU check helpers (pod/cr/gpu_job.sh).
  gpu_check.py sample --ckpt C --out F   4,000 prompts (data/lj/targets200 x 20), batch 4,096, max_new 288, inside a
                                         record.compute block: the counters vs the sampled ids, peak memory
  gpu_check.py expect --out F            expected train_tokens of the train.py jobs (whole epochs of
                                         data/lj/train_retain.jsonl) and the cost of train.py's per-step counter
"""
import argparse, json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import numpy as np, torch
import record, train
from tokenizer import make_tokenizer


def sample(a):
    from model import load_ckpt
    import sample as S
    model, tok, ex = load_ckpt(a.ckpt, 'cuda')
    model.eval()
    prompts = [json.loads(l)['prompt'] for l in open('data/lj/targets200.jsonl')] * 20
    raw = np.full((len(prompts), 288), tok.pad, dtype=np.int64)
    torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    with torch.no_grad(), record.compute(phase='sample_check', arm='gpu_check', seed=0) as c:
        out = S.generate(model, tok, prompts, greedy=False, temperature=1.0, max_new=288, batch=4096, seed=1, raw=raw)
    wall = time.time() - t0
    ind = sum(r.index(tok.eos) + 1 if tok.eos in r else 288 for r in raw.tolist())
    gl = [json.loads(l) for l in open(os.environ['LEAN_GATE_LOG'])]
    res = {'ckpt': a.ckpt, 'n_params': ex.get('n_params'), 'prompts': len(prompts), 'batch': 4096, 'max_new': 288,
           'gen_tokens': c.gen_tokens, 'independent_tokens': ind, 'attempts': c.attempts, 'lean_checks': c.lean_checks,
           'gate_lean_texts': sum(g['lean_texts'] for g in gl), 'lean_s': c.lean_s, 'gate_lean_proc_s': sum(g['lean_proc_s'] for g in gl),
           'block_s': c.active_s, 'wall_s': wall, 'hit_max_new': sum(1 for r in raw.tolist() if tok.eos not in r),
           'accepted': sum(1 for o in out if not o.startswith('LEAN')), 'peak_alloc_gb': torch.cuda.max_memory_allocated() / 2 ** 30,
           'gpu': torch.cuda.get_device_name(0)}
    json.dump(res, open(a.out, 'w'), indent=1)
    print(res)


def expect(a):
    tok = make_tokenizer('lean_seq')
    data = train.load('data/lj/train_retain.jsonl', tok, 0)
    total = sum(len(p) + len(q) for p, q in data)
    rng = random.Random(0)
    idx = [[rng.randrange(len(data)) for _ in range(500)] for _ in range(200)]
    with record.compute(phase='bench') as c:        # the exact line train.py runs once a step, at bs 500
        t0 = time.perf_counter()
        for idxs in idx:
            record.count(train_steps=1, train_tokens=sum(len(data[i][0]) + len(data[i][1]) for i in idxs))
        per_step_s = (time.perf_counter() - t0) / len(idx)
        c.n = dict.fromkeys(c.n, 0)                  # a benchmark, not work: no rows
    res = {'records': len(data), 'tokens_per_epoch': total, 'train_fast_expected': 1000 * total,
           'legacy_600_expected': 100 * total, 'ladder_ft_note': 'fine-tune mix is written by ladder_ei; see analyze.py',
           'counter_us_per_step_bs500': per_step_s * 1e6}
    json.dump(res, open(a.out, 'w'), indent=1)
    print(res)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['sample', 'expect'])
    ap.add_argument('--ckpt')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    {'sample': sample, 'expect': expect}[a.cmd](a)
