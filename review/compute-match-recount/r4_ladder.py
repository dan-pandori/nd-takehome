#!/usr/bin/env python3
"""Reviewer recount (compute-match), part 4: cm12 ladders.  From found_8 / found_transfer_8 (cumulative): distinct
targets / transfer theorems solved, distinct start-index-normalised proofs (my own normaliser: renumber N<i> by order
of appearance), round of first solve per target (min `round`); 150 random target proofs and 150 random transfer
proofs per seed re-checked by Lean (my translator).  Output: recount_ladder.json"""
import json, os, sys, random, re, collections
sys.path.insert(0, os.path.dirname(__file__)); import rlean
W = os.path.expanduser('~/review/compute-match/artifacts/cm')
def norm(p):
    m = {}
    def f(x):
        k = x.group(1); m.setdefault(k, str(len(m) + 1)); return 'N' + m[k]
    return re.sub(r'N(\d+)', f, p)
out = {}
for s in (0, 1, 2):
    d = {}
    for kind in ('found_8', 'found_transfer_8'):
        names = set(); first = {}; nset = set(); recs = []; rng = random.Random(s)
        for i, l in enumerate(open(f'{W}/la_T1_cm12k64_s{s}/{kind}.jsonl')):
            r = json.loads(l); n = r['name']; names.add(n); rd = r.get('round')
            if rd is not None: first[n] = min(first.get(n, 99), rd)
            nset.add(hash((n, norm(r["proof"]))))
            if len(recs) < 150: recs.append(r)
            else:
                j = rng.randint(0, i)
                if j < 150: recs[j] = r
        res = rlean.check([(r['prompt'], r['proof']) for r in recs], rlean.translate)
        d[kind] = {'solved': len(names), 'distinct_norm_proofs': len(nset),
                   'first_round_hist': dict(sorted(collections.Counter(first.values()).items())),
                   'lean_sample': len(recs), 'lean_ok': sum(a for a, _ in res), 'lean_fail': [w for a, w in res if not a][:3]}
        print(s, kind, d[kind], flush=True)
    out[f's{s}'] = d
json.dump(out, open(os.path.join(os.path.dirname(__file__), 'recount_ladder.json'), 'w'), indent=1)
