#!/usr/bin/env python3
"""R10 (reviewer, phase 1): (a) the run's gate rejections (prefilter rejects, artifacts/style_edl/logs/*.leanrej.jsonl)
re-checked in Lean - any Lean-valid one is a false reject (an undercount); (b) the upper bound on S_Kal theta*'s plain
pass@32 if every truncated attempt had been valid (truncation is 1.3 % of s1 S_Kal's attempts).
  python3 r10_leanrej.py [--n 600] -> out/r10_leanrej.json
"""
import argparse, collections, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C

A = f'{C.WS}/artifacts/style_edl'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=600)
    a = ap.parse_args()
    rng = random.Random(5)
    out = {}
    items = []
    for tag in ('cap', 'reads'):
        rows = C.jl(f'{A}/logs/lean_gate_{tag}.leanrej.jsonl')
        out[f'{tag}_rejects'] = len(rows)
        out[f'{tag}_keys'] = sorted(rows[0].keys())
        pick = rng.sample(rows, min(a.n, len(rows)))
        for r in pick:
            items.append((tag, r))
    srcs = [C.ls_wrap(r['prompt'], r['lean_text'], f'r{i}') for i, (_, r) in enumerate(items)]
    res = C.lean_check(srcs, tag='rej', chunk=20)
    for (tag, r), (ok, e) in zip(items, res):
        v = out.setdefault(f'{tag}_sample', [0, 0]); v[0] += ok; v[1] += 1
    out['lean_valid_examples'] = [(t, r['prompt'], r['lean_text'][:300]) for (t, r), (ok, e) in zip(items, res) if ok][:5]
    test = {r['name'] for r in C.jl(f'{C.WS}/data/style_edl/sets/test128.jsonl')}
    ub = {}
    for s in (0, 1, 2):
        rows = [r for r in C.jl(f'{A}/cap/s{s}_S_Kal__plain_k32_seed2.rows.jsonl.gz') if r['name'] in test]
        pas = sum(r['n_ok'] > 0 for r in rows) / len(rows)
        up = sum(r['n_ok'] > 0 or any('trunc' in x for x in r['status']) for r in rows) / len(rows)
        tr = sum('trunc' in x for r in rows for x in r['status'])
        ub[s] = {'pass32': pas, 'pass32_upper_if_truncated_valid': up, 'truncated_attempts_test': tr,
                 'attempts_test': 32 * len(rows)}
    out['S_Kal_truncation_upper_bound'] = ub
    json.dump(out, open(os.path.join(C.HERE, 'out', 'r10_leanrej.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
