#!/usr/bin/env python3
"""Run efficiency: the before/after measurement harness.  One invocation = one sampling configuration on the
fixed 200-target / k=256 workload, with the Lean gate behind it.

  python3 bench_sampler.py --tag base --path base --rowrng 0
  python3 bench_sampler.py --tag fast --path fast --early goal --compact 1

Writes artifacts/ef/<tag>.json  (every measured number)
       artifacts/ef/<tag>_tokens.npz  (the raw sampled token ids: everything else is re-derivable from these)
       artifacts/ef/<tag>_accept.jsonl.gz  (accepted (target, lean text, term size) — the correctness-gate input)
"""
import os, sys, json, time, gzip, argparse, collections
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import load_ckpt
import sample as S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', default='ckpts/ef/stage1_full_seq_s0.pt')
    ap.add_argument('--targets', default='artifacts/ef/targets200.jsonl')
    ap.add_argument('--n_targets', type=int, default=200)
    ap.add_argument('--k', type=int, default=256)
    ap.add_argument('--temperature', type=float, default=0.8)
    ap.add_argument('--max_new', type=int, default=512)
    ap.add_argument('--batch', type=int, default=512)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--path', default='fast')
    ap.add_argument('--early', default='goal')
    ap.add_argument('--compact', type=int, default=1)
    ap.add_argument('--rowrng', type=int, default=1)
    ap.add_argument('--gate', type=int, default=1)
    ap.add_argument('--save_tokens', type=int, default=1)
    ap.add_argument('--tag', required=True)
    a = ap.parse_args()

    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model, tok, extra = load_ckpt(a.ckpt, dev)
    tg = [json.loads(l) for l in open(a.targets)][:a.n_targets]
    prompts = [t['prompt'] for t in tg for _ in range(a.k)]
    owner = [t['name'] for t in tg for _ in range(a.k)]
    print(f'[bench] {a.tag}: {len(tg)} targets x k={a.k} = {len(prompts)} samples, mode {tok.mode}, '
          f'path {a.path} early {a.early} compact {a.compact} rowrng {a.rowrng} batch {a.batch} max_new {a.max_new}', flush=True)

    raw = np.zeros((len(prompts), a.max_new), dtype=np.int16) if a.save_tokens else None
    stats = {}
    torch.cuda.reset_peak_memory_stats() if dev == 'cuda' else None
    t0 = time.time()
    texts = S.generate(model, tok, prompts, greedy=False, temperature=a.temperature, max_new=a.max_new,
                       batch=a.batch, seed=a.seed, path=a.path, early=a.early, compact=bool(a.compact),
                       rowrng=bool(a.rowrng), stats=stats, gate=False, raw=raw)
    wall = time.time() - t0

    dl = np.array(stats['declen_by_prompt'], dtype=np.int32)
    n_eos_model = int(stats.get('stop_eos', 0)) if a.path == 'fast' else int((dl < a.max_new).sum())
    rec = {'tag': a.tag, 'utc': time.strftime('%FT%TZ', time.gmtime()), 'args': vars(a), 'tok_mode': tok.mode,
           'n_targets': len(tg), 'k': a.k, 'n_samples': len(prompts),
           'sample_wall_s': round(wall, 2), 'samples_per_s': round(len(prompts) / wall, 2),
           'decoded_tokens_mean': round(float(dl.mean()), 2), 'decoded_tokens_p95': int(np.percentile(dl, 95)),
           'decoded_tokens_median': int(np.median(dl)), 'decoded_tokens_total': int(dl.sum()),
           'rowsteps': int(stats['rowsteps']), 'model_steps': int(stats['steps']), 'chunks': int(stats['chunks']),
           'frac_rows_with_eos': round(float((dl < a.max_new).mean()), 5),
           'frac_rows_model_eos': round(n_eos_model / len(prompts), 5),
           'stop_eos': int(stats.get('stop_eos', 0)), 'stop_exact': int(stats.get('stop_exact', 0)),
           'stop_goal': int(stats.get('stop_goal', 0)),
           'peak_alloc_gb': round(stats.get('peak_alloc_gb', 0), 3), 'peak_reserved_gb': round(stats.get('peak_reserved_gb', 0), 3),
           'prompt_len_max': stats['prompt_len_max'],
           'n_texts': sum(1 for x in texts if x is not None)}
    print('[bench] sampling:', json.dumps({k: rec[k] for k in ('sample_wall_s', 'samples_per_s', 'decoded_tokens_mean',
          'decoded_tokens_p95', 'frac_rows_with_eos', 'peak_alloc_gb', 'n_texts')}), flush=True)

    if a.save_tokens:
        np.savez_compressed(f'artifacts/ef/{a.tag}_tokens.npz', ids=raw, declen=dl,
                            names=np.array(owner), order=np.arange(len(prompts)))

    if a.gate:
        from lean_gate import gate as lgate, VERDICT
        os.environ.setdefault('LEAN_GATE_LOG', f'artifacts/ef/gate_{a.tag}.jsonl')
        t1 = time.time()
        res = lgate(tok, prompts, texts)
        rec['gate_wall_s'] = round(time.time() - t1, 2)
        logf = os.environ['LEAN_GATE_LOG']
        last = json.loads(open(logf).read().strip().split('\n')[-1])
        rec['gate'] = last
        acc = []
        nacc = 0
        seen = collections.defaultdict(set)
        for p, o, nm_, tx in zip(prompts, res, owner, texts):
            if o.startswith('LEANREJ') or o.startswith('LEANPARSE'):
                continue
            nacc += 1
            v = VERDICT.get((p, o))
            key = v['text'] if v else o
            if key not in seen[nm_]:
                seen[nm_].add(key)
                acc.append({'name': nm_, 'prompt': p, 'text': v['text'] if v else None, 'proof': o,
                            'size': v['size'] if v else None, 'nd_ok': v['nd'] if v else None})
        rec['accepted_samples'] = nacc
        rec['accepted_distinct'] = len(acc)
        rec['targets_solved'] = len(set(x['name'] for x in acc))
        rec['accept_rate'] = round(nacc / len(prompts), 5)
        rec['lean_proc_s'] = last['lean_proc_s']
        rec['lean_wall_s'] = last['lean_wall_s']
        rec['accepted_per_lean_proc_s'] = round(nacc / max(last['lean_proc_s'], 1e-9), 2)
        rec['distinct_checked'] = last['distinct_checked']
        rec['checked_per_lean_proc_s'] = round(last['distinct_checked'] / max(last['lean_proc_s'], 1e-9), 2)
        rec['end_to_end_s'] = round(wall + rec['gate_wall_s'], 2)
        with gzip.open(f'artifacts/ef/{a.tag}_accept.jsonl.gz', 'wt') as f:
            for x in acc:
                f.write(json.dumps(x) + '\n')
        print('[bench] gate:', json.dumps({k: rec[k] for k in ('gate_wall_s', 'accepted_samples', 'accepted_distinct',
              'targets_solved', 'lean_proc_s', 'accepted_per_lean_proc_s', 'end_to_end_s')}), flush=True)

    with open(f'artifacts/ef/{a.tag}.json', 'w') as f:
        json.dump(rec, f, indent=1)
    print('[bench] wrote artifacts/ef/' + a.tag + '.json', flush=True)


if __name__ == '__main__':
    main()
