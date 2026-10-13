#!/usr/bin/env python3
"""create-or-elicit: offline Lean re-check of the counted proofs behind the arm comparison (Lean alone: the ND proofs the
reads stored, translated by nd2lean and checked by Lean 4 core through lean_judge.judge_many), with a negative control
(the same proofs with the theorem's conclusion G replaced by ( ~ G ): every one must be rejected).

  LEAN_GATE_WORKERS=2 python3 coe/coe_recheck.py --out artifacts/coe/recheck.json [--per_model 50]

Groups (strict σ-covered held-out members only, `data/coe/sigma_heldout_strict.txt`):
  ko_reads   every stored proof in the knockout plain reads (pend, r8, r16, r20, r24; x0 and x1)
  ko_large   every accepted proof in the knockout bases' large-k samples (certificate, top-up, la_transfer_916 runs)
  ko_p3a     every stored proof in the Phase 3a reads
  full_r16 / dose1_r16   a seeded sample of --per_model stored proofs per model in the r16 x0 reads
"""
import argparse, collections, glob, gzip, json, os, random, re, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import lean_judge


def rows(fn):
    op = gzip.open if fn.endswith('.gz') else open
    with op(fn, 'rt') as f:
        for line in f:
            yield json.loads(line)


def negate(prompt):
    body = prompt.strip()[4:-4]
    prem, concl = (' ' + body + ' ').split(' SEQ ')
    return f'THM {prem.strip()} SEQ ( ~ {concl.strip()} ) PRF'.replace('THM  SEQ', 'THM SEQ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--per_model', type=int, default=50)
    a = ap.parse_args()
    strict = set(open('data/coe/sigma_heldout_strict.txt').read().split())
    prompt = {}
    for fn in ('data/coe/read1054.jsonl', 'data/coe/transfer_track832.jsonl'):
        for r in rows(fn):
            prompt.setdefault(r['name'], r['prompt'])
    items = collections.defaultdict(dict)          # group -> {(name, proof): source}
    for fn in sorted(glob.glob('artifacts/coe/eval/*_ko_s*_x[01].jsonl.gz')):
        for r in rows(fn):
            if r['name'] in strict and r.get('solved'):
                for p in r.get('proofs') or []:
                    items['ko_reads'].setdefault((r['name'], p), os.path.basename(fn))
    for fn in sorted(glob.glob('artifacts/coe/large/*ko_s*.json')):
        if fn.endswith('.args.json'):
            continue
        for n, t in (json.load(open(fn)).get('theorems') or {}).items():
            if n in strict:
                for p in t.get('acc') or {}:
                    items['ko_large'].setdefault((n, p), os.path.basename(fn))
    for fn in sorted(glob.glob('artifacts/coe/p3a/*.jsonl.gz')):
        for r in rows(fn):
            if r['name'] in strict and r.get('solved'):
                for p in r.get('proofs') or []:
                    items['ko_p3a'].setdefault((r['name'], p), os.path.basename(fn))
    rng = random.Random(20261013)
    for arm in ('full', 'dose1'):
        for fn in sorted(glob.glob(f'artifacts/coe/eval/r16_{arm}_s*_x0*.jsonl.gz')):
            pool = sorted({(r['name'], p) for r in rows(fn) if r['name'] in strict and r.get('solved')
                           for p in r.get('proofs') or []})
            for k in rng.sample(pool, min(a.per_model, len(pool))):
                items[f'{arm}_r16'].setdefault(k, os.path.basename(fn))
    t0 = time.time()
    rep = {'groups': {}}
    for g, d in items.items():
        keys = sorted(d)
        pos = lean_judge.judge_many([(prompt[n], p) for n, p in keys])
        neg = lean_judge.judge_many([(negate(prompt[n]), p) for n, p in keys])
        rep['groups'][g] = {
            'proofs': len(keys), 'theorems': len({n for n, _ in keys}), 'files': sorted(set(d.values())),
            'accepted': sum(1 for x in pos if x[0]),
            'rejected': [{'name': n, 'source': d[(n, p)], 'proof': p, 'why': str(x[1])[:300]}
                         for (n, p), x in zip(keys, pos) if not x[0]],
            'negctl_accepted': [{'name': n, 'proof': p} for (n, p), x in zip(keys, neg) if x[0]],
            'negctl_rejected': sum(1 for x in neg if not x[0])}
        print(g, {k: v for k, v in rep['groups'][g].items() if k not in ('files', 'rejected', 'negctl_accepted')},
              'rejected', len(rep['groups'][g]['rejected']), 'negctl accepted', len(rep['groups'][g]['negctl_accepted']),
              f'{time.time() - t0:.0f}s', flush=True)
    rep['judge_stats'] = lean_judge.stats()
    rep['secs'] = round(time.time() - t0, 1)
    json.dump(rep, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
