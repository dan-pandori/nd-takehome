#!/usr/bin/env python3
"""Reviewer's renaming-class disjointness: key = min over the 24 atom permutations of (sorted premises, conclusion).
Atoms are P Q R S only (F is falsum). Premise order ignored, duplicates kept."""
import json, gzip, itertools, os, collections
R = os.path.expanduser('~/review/search-expert')
AT = 'PQRS'
PERMS = [dict(zip(AT, p)) for p in itertools.permutations(AT)]
def key(thm_or_prompt):
    s = thm_or_prompt
    if s.startswith('THM'): s = s[3:].rsplit('PRF', 1)[0]; prem, concl = s.split(' SEQ ')
    else: prem, concl = s.split('|-')
    toks = prem.split(); ps = []; cur = []; d = 0
    for t in toks:
        if t == ',' and d == 0: ps.append(cur); cur = []; continue
        d += (t == '(') - (t == ')'); cur.append(t)
    if cur: ps.append(cur)
    c = concl.split()
    best = None
    for m in PERMS:
        f = lambda ts: ' '.join(m.get(t, t) for t in ts)
        k = (tuple(sorted(f(p) for p in ps)), f(c))
        if best is None or k < best: best = k
    return best
def rd(fn):
    op = gzip.open if fn.endswith('.gz') else open
    with op(fn, 'rt') as f:
        for l in f:
            if l.strip():
                r = json.loads(l); yield r.get('thm') or r['prompt']
train = {'train_k12': f'{R}/rv/data/train_k12.jsonl.gz', 'rl_targets': f'{R}/data/ladder/rl_targets.jsonl'}
evals = {'transfer_long2_91': f'{R}/data/ladder/transfer_long2_91.jsonl', 'rr600_13to16': f'{R}/data/ladder/rr600_13to16.jsonl'}
EK = {n: collections.Counter(key(t) for t in rd(fn)) for n, fn in evals.items()}
for n, c in EK.items(): print(n, 'n', sum(c.values()), 'classes', len(c), 'within-pool dup classes', sum(1 for v in c.values() if v > 1))
print('l2 x rr classes shared', len(set(EK['transfer_long2_91']) & set(EK['rr600_13to16'])))
for tn, fn in train.items():
    tk = set(); n = 0
    for t in rd(fn): tk.add(key(t)); n += 1
    for en, c in EK.items():
        print(f'{tn} ({n} recs, {len(tk)} classes) x {en}: shared classes {len(tk & set(c))}')
