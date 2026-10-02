#!/usr/bin/env python3
"""Reviewer (trajectory-cap6; adapted from review_tj/splits.py): renaming-class disjointness between every training file and every evaluation pool.
Key: prompt -> (premises, conclusion) token lists; for each of the 24 permutations of the atoms P,Q,R,S (F = falsum is
not renamed), rename, sort the premise strings (premise-order insensitive), take the lexicographic minimum.
Also a weaker key: conclusion-only class, and exact-prompt match."""
import json, itertools, os
R = os.path.expanduser('~/review/trajectory-cap6')
AT = 'PQRS'
def parse(prompt):
    body = prompt.split('THM', 1)[1].rsplit('PRF', 1)[0]
    prem, concl = body.split(' SEQ ')
    ps, cur, d = [], [], 0
    for t in prem.split():
        if t == ',' and d == 0: ps.append(cur); cur = []; continue
        d += (t == '(') - (t == ')'); cur.append(t)
    if cur: ps.append(cur)
    return ps, concl.split()
def key(prompt):
    ps, c = parse(prompt); best = None
    for perm in itertools.permutations(AT):
        m = dict(zip(AT, perm)); rn = lambda f: ' '.join(m.get(t, t) for t in f)
        k = (tuple(sorted(rn(p) for p in ps)), rn(c))
        best = k if best is None or k < best else best
    return best
def rd(f): return [json.loads(l) for l in open(f) if l.strip()]
train = {'train_cap6': f'{R}/rv6/in/train_depth3_f0_a1.jsonl', 'ladder_transfer_unused': f'{R}/data/ladder/transfer.jsonl', 'rl_targets': f'{R}/data/ladder/rl_targets.jsonl'}
ev = {'textbook72': f'{R}/data/bs/textbook72.jsonl', 'holdout250': f'{R}/data/bs/holdout250.jsonl'}
TK = {n: {key(r['prompt']) for r in rd(f)} for n, f in train.items()}
TP = {n: {r['prompt'] for r in rd(f)} for n, f in train.items()}
out = {}
for en, ef in ev.items():
    E = rd(ef); ek = [key(r['prompt']) for r in E]
    for tn in train:
        hits = [r['name'] for r, k in zip(E, ek) if k in TK[tn]]
        exact = sum(r['prompt'] in TP[tn] for r in E)
        out[f'{en} vs {tn}'] = {'n_eval': len(E), 'class_overlap': len(hits), 'exact_prompt': exact, 'examples': hits[:5]}
        print(en, 'vs', tn, out[f'{en} vs {tn}'])
    # within-eval overlap
tb = {key(r['prompt']) for r in rd(ev['textbook72'])}; hb = {key(r['prompt']) for r in rd(ev['holdout250'])}
print('textbook72 & holdout250 classes shared:', len(tb & hb))
json.dump(out, open(f'{R}/rv6/splits.json', 'w'), indent=1)
