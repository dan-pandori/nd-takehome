#!/usr/bin/env python3
"""Reviewer split-disjointness by renaming class. Key = min over all 24 renamings of {P,Q,R,S} of
(sorted premise list, conclusion); F is falsum, not an atom. Also an order-sensitive key (premise order kept)."""
import json, glob, os, itertools, re, collections, sys
R = os.path.expanduser('~/review/best-state')
AT = 'PQRS'
PERMS = [dict(zip(AT, p)) for p in itertools.permutations(AT)]
def parts(prompt):
    body = prompt.split('THM', 1)[1].rsplit('PRF', 1)[0]
    pre, concl = body.split('SEQ')
    toks = pre.split(); prem = []; cur = []; d = 0
    for t in toks:
        if t == ',' and d == 0: prem.append(' '.join(cur)); cur = []; continue
        d += (t == '(') - (t == ')'); cur.append(t)
    if cur: prem.append(' '.join(cur))
    return prem, ' '.join(concl.split())
def sub(s, m): return ' '.join(m.get(t, t) for t in s.split())
def key(prompt, ordered=False):
    prem, c = parts(prompt)
    best = None
    for m in PERMS:
        ps = [sub(p, m) for p in prem]
        k = (tuple(ps) if ordered else tuple(sorted(ps)), sub(c, m))
        if best is None or k < best: best = k
    return best
EVAL = {'tb72': f'{R}/data/bs/textbook72.jsonl', 'dev1108': f'{R}/data/bs/dev1108.jsonl',
        'holdout250': f'{R}/data/bs/holdout250.jsonl', 'rr600': f'{R}/data/ladder/transfer_long_rr600.jsonl',
        'long2': f'{R}/data/ladder/transfer_long2.jsonl', 'p2_heldout': f'{R}/data/p2/heldout.jsonl'}
ek = {}
for n, fn in EVAL.items():
    ek[n] = {key(json.loads(l)['prompt']) for l in open(fn) if l.strip()}
# self-check: a renamed + premise-permuted copy must collide
p = 'THM ( S v P ) , ( S > ( Q v P ) ) , ( P > ( ~ S ) ) SEQ ( ( Q v P ) v ( ~ S ) ) PRF'
q = 'THM ( Q > ( ~ R ) ) , ( R v Q ) , ( R > ( S v Q ) ) SEQ ( ( S v Q ) v ( ~ R ) ) PRF'
assert key(p) == key(q), 'normaliser self-test'
assert key(p) != key(p.replace('( ~ S ) ) PRF', '( ~ P ) ) PRF'))
TRAIN = {'p2_cap6': [f'{R}/data/p2/train_depth3_f0_a1.jsonl'], 'k12': [f'{R}/data/kh/train_k12.jsonl'],
         'rl_targets': [f'{R}/data/ladder/rl_targets.jsonl']}
for d in sorted(glob.glob(f'{R}/artifacts/bs/la_T1_*')):
    TRAIN['mix_' + os.path.basename(d)] = sorted(glob.glob(f'{d}/mix_*.jsonl'))
out = {}; cache = {}
for tn, fns in TRAIN.items():
    hits = collections.Counter(); n = 0
    for fn in fns:
        for l in open(fn):
            if not l.strip(): continue
            pr = json.loads(l)['prompt']; n += 1
            k = cache.get(pr)
            if k is None:
                k = key(pr)
                if len(cache) < 2_000_000: cache[pr] = k
            for en, s in ek.items():
                if k in s: hits[en] += 1
    out[tn] = dict(n_records=n, hits=dict(hits))
    print(tn, n, dict(hits), flush=True)
# pairwise eval pools
pair = {}
for a, b in itertools.combinations(EVAL, 2):
    pair[f'{a}~{b}'] = len(ek[a] & ek[b])
print('eval pairs', pair)
out['eval_pairs'] = pair; out['eval_sizes'] = {n: len(s) for n, s in ek.items()}
json.dump(out, open(f'{R}/review_bs/splits.json', 'w'), indent=1)
