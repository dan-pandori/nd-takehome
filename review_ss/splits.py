import json, itertools
def canon(thm):
    lhs, rhs = thm.split('|-'); prem = [p.strip() for p in lhs.split(' , ') if p.strip()]; rhs = rhs.strip()
    best = None
    for perm in itertools.permutations('PQRS'):
        m = dict(zip('PQRS', perm))
        sub = lambda s: ' '.join(m.get(t, t) for t in s.split())
        k = (tuple(sorted(sub(p) for p in prem)), sub(rhs))
        if best is None or k < best: best = k
    return best
def keys(fn): return {canon(json.loads(l)['thm']): json.loads(l)['name'] for l in open(fn) if l.strip()}
ev = keys('data/sc/theorems.jsonl'); print('eval classes', len(ev))
surv = set(l.strip() for l in open('data/sc/falsifier_survivors.txt'))
for tr in ['/home/dan/work/state-env/data/p2/train_depth3_f0_a1.jsonl', 'data/ladder/rl_targets.jsonl']:
    t = keys(tr); ov = set(t) & set(ev)
    print(tr, 'train classes', len(t), 'overlap with 383 pool', len(ov), 'survivors in overlap', sum(ev[k] in surv for k in ov), [ev[k] for k in list(ov)[:5]])
