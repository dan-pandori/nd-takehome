"""Reviewer: renaming-class disjointness train vs held-out under a real canonical form (min over 24 atom bijections)."""
import json, itertools, re
ATOMS = 'PQRS'
def canon(thm):
    prem, concl = thm.split('|-')
    prem = [p.strip() for p in re.split(r' , ', prem.strip())] if prem.strip() else []
    best = None
    for perm in itertools.permutations(ATOMS):
        m = dict(zip(ATOMS, perm))
        f = lambda s: ' '.join(m.get(t, t) for t in s.split())
        k = (tuple(sorted(f(p) for p in prem)), f(concl.strip()))
        if best is None or k < best: best = k
    return best
H = [json.loads(l) for l in open('data/p2/heldout.jsonl')]
hk = {canon(r['thm']): r for r in H}
print('heldout', len(H), 'distinct classes', len(hk))
hits = 0; exact = 0; d3hits = 0; hs = set()
for l in open('data/p2/train_depth3_f0_a1.jsonl'):
    r = json.loads(l); k = canon(r['thm'])
    if k in hk:
        hits += 1; hs.add(k); d3hits += bool((hk[k].get('pat') or {}).get('depth3'))
print('train records in a held-out renaming class:', hits, 'distinct held-out theorems hit:', len(hs), 'of which depth3:', d3hits)
