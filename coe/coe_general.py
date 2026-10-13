#!/usr/bin/env python3
"""create-or-elicit E1 / E6: general ability, knockout vs full (and 1 % dose) bases and r16 models.

  * held-out greedy on p2/heldout (5,000; T 0, state_eval defaults 256 tokens / 48 steps): overall and on the 4,321
    theorems whose reference proof has no sigma (the other 679 have one);
  * plain k 256 reads (x0) on holdout250 and textbook72 (dev58 / train14), pend and r16, from the read summaries.
Old full seeds' held-out greedy rows are trajectory's (`~/work/trajectory/artifacts/tj/eval/heldout_best12_s{S}_b1200.jsonl`).

  python3 coe/coe_general.py --out artifacts/coe/general.json
"""
import argparse, gzip, json, os, statistics, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from coe.coe_sigma import flags


def rows(fn):
    op = gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)
    return [json.loads(l) for l in op if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    sig = set()
    for l in open('data/p2/heldout.jsonl'):
        r = json.loads(l)
        fl = flags(r['proof'])
        if fl and (fl['w']['sigma_strict'] or fl['p']['sigma_strict']):
            sig.add(r.get('name') or r['thm'])
    models = [('full', s, os.path.expanduser(f'~/work/trajectory/artifacts/tj/eval/heldout_best12_s{s}_b1200.jsonl')) for s in (0, 1, 2)] + \
             [('full', s, f'artifacts/coe/eval/heldout_full_s{s}.jsonl') for s in (3, 4, 5)] + \
             [('ko', s, f'artifacts/coe/eval/heldout_ko_s{s}.jsonl') for s in range(6)] + \
             [('dose1', s, f'artifacts/coe/eval/heldout_dose1_s{s}.jsonl') for s in range(3)]
    out = {'sigma_heldout_records': len(sig), 'models': {}}
    print(f'p2/heldout: {len(sig)} records with a sigma reference proof')
    print('| model | held-out greedy (5,000) | non-σ (4,321) | σ (679) | holdout250 pend / r16 | textbook72 pend / r16 (dev58, train14 at r16) |')
    print('|---|---|---|---|---|---|')
    for arm, s, fn in models:
        if not os.path.exists(fn) and not os.path.exists(fn + '.gz'):
            continue
        rs = rows(fn if os.path.exists(fn) else fn + '.gz')
        ok = [r for r in rs if r['solved']]
        key = lambda r: r.get('name') or r.get('thm')
        ns = [r for r in rs if key(r) not in sig]; ss = [r for r in rs if key(r) in sig]
        m = {'heldout': len(ok) / len(rs), 'heldout_nonsigma': sum(r['solved'] for r in ns) / len(ns),
             'heldout_sigma': sum(r['solved'] for r in ss) / max(1, len(ss)), 'n': len(rs)}
        def rd(ck):
            for tag in (f'{ck}_{arm}_s{s}_x0', f'{ck}_{arm}_s{s}_x0e'):
                fn2 = f'artifacts/coe/eval/{tag}.jsonl.gz'
                if os.path.exists(fn2):
                    rr = rows(fn2)
                    names = {x['name']: x['solved'] for x in rr}
                    return names
            return None
        for ck in ('pend', 'r16'):
            nm = rd(ck)
            if nm is None:
                continue
            h = [json.loads(l)['name'] for l in open('data/bs/holdout250.jsonl')]
            dev = [json.loads(l)['name'] for l in open('data/eval_only/textbook72/textbook_dev.jsonl')]
            tr = [json.loads(l)['name'] for l in open('data/eval_only/textbook72/textbook_train.jsonl')]
            if all(n in nm for n in h):
                m[f'{ck}_h250'] = sum(nm[n] for n in h)
            if all(n in nm for n in dev + tr):
                m[f'{ck}_dev58'] = sum(nm[n] for n in dev); m[f'{ck}_train14'] = sum(nm[n] for n in tr)
        out['models'][f'{arm}_s{s}'] = m
        print(f"| {arm} s{s} | {m['heldout']:.4f} | {m['heldout_nonsigma']:.4f} | {m['heldout_sigma']:.4f} | "
              f"{m.get('pend_h250', '–')} / {m.get('r16_h250', '–')} | "
              f"{(m.get('pend_dev58', 0) + m.get('pend_train14', 0)) if 'pend_dev58' in m else '–'} / "
              f"{(m.get('r16_dev58', 0) + m.get('r16_train14', 0)) if 'r16_dev58' in m else '–'} "
              f"({m.get('r16_dev58', '–')}, {m.get('r16_train14', '–')}) |")
    for arm in ('full', 'ko', 'dose1'):
        v = [m for k, m in out['models'].items() if k.startswith(arm + '_')]
        if v:
            out[f'{arm}_median'] = {q: statistics.median([x[q] for x in v if q in x]) for q in ('heldout', 'heldout_nonsigma', 'heldout_sigma')}
    json.dump(out, open(a.out, 'w'), indent=1)
    print({k: v for k, v in out.items() if k.endswith('_median')})


if __name__ == '__main__':
    main()
