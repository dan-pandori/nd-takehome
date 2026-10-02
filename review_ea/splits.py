"""Reviewer (evidence-atlas): split disjointness by renaming class, own canonicaliser.
Class key = min over all atom permutations of (sorted premise strings, goal) -> premise-order and renaming invariant.
Training data of the 8 re-scored checkpoints: C0 = data/p2/train_depth3_f0_a1.jsonl (+ ladder rl_targets for T1),
K12 = data/kh/train_k12.jsonl (+ rl_targets for T1). Pools: textbook72, dev1108, holdout250."""
import json, re, itertools, sys, collections
def sides(prompt):
    m = re.fullmatch(r'THM (.*?)\s*SEQ (.*) PRF', prompt.strip()); assert m, prompt
    prem = [p.strip() for p in m.group(1).split(' , ')] if m.group(1).strip() else []
    return prem, m.group(2).strip()
def key(prompt):
    prem, goal = sides(prompt)
    atoms = sorted(set(re.findall(r'\b[A-EG-Z]\b', ' '.join(prem + [goal]))))
    best = None
    for perm in itertools.permutations(atoms):
        mp = dict(zip(atoms, perm))
        f = lambda s: ' '.join(mp.get(t, t) for t in s.split())
        k = (tuple(sorted(set(f(p) for p in prem))), f(goal))
        if best is None or k < best: best = k
    return best
B = '/home/dan/work/best-state/'
train = {'C0_stage1': B + 'data/p2/train_depth3_f0_a1.jsonl', 'K12_stage1': B + 'data/kh/train_k12.jsonl', 'rl_targets': 'data/ladder/rl_targets.jsonl'}
pools = {'textbook72': 'data/bs/textbook72.jsonl', 'dev1108': 'data/bs/dev1108.jsonl', 'holdout250': 'data/bs/holdout250.jsonl'}
K = {}
for n, f in {**train, **pools}.items():
    K[n] = collections.Counter(key(json.loads(l)['prompt']) for l in open(f) if l.strip())
    print(n, sum(K[n].values()), 'classes', len(K[n]), flush=True)
res = {}
for t in train:
    for p in pools:
        ov = set(K[t]) & set(K[p]); res[f'{t}|{p}'] = len(ov)
        print(f'{t:12s} x {p:11s}: {len(ov)} shared classes ({sum(K[p][k] for k in ov)} pool rows)')
for a, b in itertools.combinations(pools, 2):
    ov = set(K[a]) & set(K[b]); res[f'{a}|{b}'] = len(ov); print(f'{a} x {b}: {len(ov)} shared classes')
json.dump(res, open('review_ea/splits.json', 'w'), indent=1)
