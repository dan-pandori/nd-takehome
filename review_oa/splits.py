"""Reviewer split check: canonical sequent class (min over 24 atom bijections of (sorted premises, conclusion);
F = falsum, not an atom) between RL targets / training files and the 322 evaluation theorems."""
import json, itertools, re, sys, os, gzip
import rvc
def parse(prompt):
    body = prompt.split('THM', 1)[1].rsplit('PRF', 1)[0]; a, c = body.split(' SEQ ')
    prem, cur, d = [], [], 0
    for t in a.split():
        if t == ',' and d == 0: prem.append(cur); cur = []; continue
        d += (t == '(') - (t == ')'); cur.append(t)
    if cur: prem.append(cur)
    return [' '.join(p) for p in prem], c.strip()
def canon(prompt):
    prem, c = parse(prompt); best = None
    for perm in itertools.permutations('PQRS'):
        m = dict(zip('PQRS', perm)); f = lambda s: ' '.join(m.get(t, t) for t in s.split())
        k = (tuple(sorted(f(p) for p in prem)), f(c)); best = k if best is None or k < best else best
    return best
EV = {canon(p): n for n, p in rvc.prompts().items()}
print('eval classes', len(EV))
def prompt_of(d):
    if 'prompt' in d: return d['prompt']
    if 'thm' in d: return rvc.thm2prompt(d['thm'])
for f in sys.argv[1:]:
    op = gzip.open if f.endswith('.gz') else open; hit = set(); n = 0
    for l in op(f, 'rt'):
        d = json.loads(l); p = prompt_of(d)
        if not p: continue
        n += 1; k = canon(p)
        if k in EV: hit.add(EV[k])
    print(f, 'records', n, 'eval theorems hit', len(hit), sorted(hit)[:5])
