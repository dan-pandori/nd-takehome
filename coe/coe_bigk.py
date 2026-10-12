#!/usr/bin/env python3
"""create-or-elicit: large-k plain sampling of one state-env checkpoint on a theorem list, in chunks, keeping every
accepted proof's MULTIPLICITY (for Good-Turing / coverage) and the per-chunk wall time (for the per-attempt cost).

Same sampler as the ladder and state_eval.py (state_sample.env_generate: T 0.8, fast path, per-row seeding), Lean alone
decides (eval_set.judge -> lean_judge).  Resumable: each finished chunk appends one line per theorem to <out>.chunks.jsonl;
a restart skips finished chunks.  A theorem stops early when it reaches --stop_successes accepted proofs (0 = never).

  python3 coe/coe_bigk.py --ckpt C --in F.jsonl --n 10240 --chunk 1024 --seed0 9000 --batch 1024 --out artifacts/coe/large/X

Writes <out>.chunks.jsonl (per theorem per chunk: tried, ok, accepted ND proofs with counts, reason counts, wall share)
and <out>.json (per theorem totals + chunk timing + env stats).
"""
import argparse, collections, json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import torch
import record
from model import load_ckpt
from eval_set import judge
from state_sample import env_generate, env_stats_json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, required=True, help='attempts per theorem (total)')
    ap.add_argument('--chunk', type=int, default=1024, help='attempts per theorem per chunk')
    ap.add_argument('--seed0', type=int, default=9000, help='chunk c uses sampling seed seed0 + c')
    ap.add_argument('--batch', type=int, default=1024)
    ap.add_argument('--temperature', type=float, default=0.8)
    ap.add_argument('--max_action', type=int, default=512)
    ap.add_argument('--max_steps', type=int, default=96)
    ap.add_argument('--stop_successes', type=int, default=0)
    ap.add_argument('--names', default=None, help='comma list or @file of names to keep')
    a = ap.parse_args()
    record.save_config(vars(a), a.out + '.json')
    recs = [json.loads(l) for l in open(a.inp) if l.strip()]
    if a.names:
        keep = set(open(a.names[1:]).read().split()) if a.names.startswith('@') else set(a.names.split(','))
        recs = [r for r in recs if r.get('name') in keep]
    model, tok, extra = load_ckpt(a.ckpt, 'cuda' if torch.cuda.is_available() else 'cpu')
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    tot = {r['name']: {'tried': 0, 'ok': 0, 'acc': collections.Counter(), 'reasons': collections.Counter(), 'chunks': 0} for r in recs}
    done_chunks = set()
    cf = a.out + '.chunks.jsonl'
    timing = []
    if os.path.exists(cf):
        for l in open(cf):
            x = json.loads(l)
            if x.get('chunk_summary'):
                done_chunks.add(x['chunk']); timing.append(x); continue
            t = tot.get(x['name'])
            if t is None:
                continue
            t['tried'] += x['tried']; t['ok'] += x['ok']; t['acc'].update(x['acc']); t['reasons'].update(x['reasons']); t['chunks'] += 1
    stats = {}
    nchunks = (a.n + a.chunk - 1) // a.chunk
    for c in range(nchunks):
        if c in done_chunks:
            continue
        live = [r for r in recs if not (a.stop_successes and tot[r['name']]['ok'] >= a.stop_successes)]
        if not live:
            break
        k = min(a.chunk, a.n - c * a.chunk)
        prompts = [r['prompt'] for r in live for _ in range(k)]
        t0 = time.time()
        with record.compute(phase='bigk', ckpt=a.ckpt, chunk=c) as rc:
            flat = env_generate(model, tok, prompts, greedy=False, temperature=a.temperature, max_action=a.max_action,
                                max_steps=a.max_steps, batch=a.batch, seed=a.seed0 + c, stats=stats)
            t_gen = time.time() - t0
            per = [flat[i * k:(i + 1) * k] for i in range(len(live))]
            rows = judge(live, per, 'n_lines')
        wall = time.time() - t0
        with open(cf, 'a') as f:
            for r, row, ps in zip(live, rows, per):
                good = set(row['proofs'])
                acc = collections.Counter(p for p in ps if p in good)
                rs = collections.Counter(row['reasons'])
                x = {'name': r['name'], 'chunk': c, 'seed': a.seed0 + c, 'tried': k, 'ok': row['n_ok'], 'acc': dict(acc), 'reasons': dict(rs)}
                f.write(json.dumps(x) + '\n')
                t = tot[r['name']]
                t['tried'] += k; t['ok'] += row['n_ok']; t['acc'].update(acc); t['reasons'].update(rs); t['chunks'] += 1
            s = {'chunk_summary': True, 'chunk': c, 'seed': a.seed0 + c, 'theorems': len(live), 'attempts': len(prompts),
                 'wall_s': round(wall, 2), 'gen_s': round(t_gen, 2), 'gpu': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu',
                 'batch': a.batch, 'peak_alloc_gb': round(torch.cuda.max_memory_allocated() / 2**30, 2) if torch.cuda.is_available() else None}
            f.write(json.dumps(s) + '\n')
        timing.append(s)
        print(f'chunk {c}: {len(live)} theorems x {k} in {wall:.0f}s ({1000 * wall / len(prompts):.2f} ms/attempt); '
              f'solved so far {sum(1 for t in tot.values() if t["ok"])}', flush=True)
    out = {'ckpt': a.ckpt, 'in': a.inp, 'n_target': a.n, 'chunk': a.chunk, 'batch': a.batch, 'temperature': a.temperature,
           'max_action': a.max_action, 'max_steps': a.max_steps, 'stop_successes': a.stop_successes,
           'attempts': sum(t['tried'] for t in tot.values()), 'wall_s': sum(x['wall_s'] for x in timing),
           'ms_per_attempt': 1000 * sum(x['wall_s'] for x in timing) / max(1, sum(x['attempts'] for x in timing)),
           'timing': timing, 'env': env_stats_json(stats) if stats else None,
           'theorems': {n: {'tried': t['tried'], 'ok': t['ok'], 'distinct': len(t['acc']), 'f1': sum(1 for v in t['acc'].values() if v == 1),
                            'acc': dict(t['acc']), 'reasons_top': dict(t['reasons'].most_common(12)),
                            'cut': sum(v for kk, v in t['reasons'].items() if 'action truncated' in kk or 'step cap' in kk)} for n, t in tot.items()}}
    json.dump(out, open(a.out + '.json', 'w'))
    print(json.dumps({k: v for k, v in out.items() if k not in ('theorems', 'timing', 'env')}))


if __name__ == '__main__':
    main()
