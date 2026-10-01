#!/usr/bin/env python3
"""Re-run of the flip control after fixing double-flip in nested boxes (flip only at ORI lines); 120 proofs."""
import json, glob, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rlean
E = os.path.expanduser('~/review/best-state/artifacts/bs/eval')
pool = []
for fn in sorted(glob.glob(E + '/T1_best12_s*__*.jsonl')) + sorted(glob.glob(E + '/Fz_best6_s*__*.jsonl')):
    for l in open(fn):
        r = json.loads(l)
        for p in r['proofs']: pool.append((r['prompt'], p))
rng = random.Random(7); xs = [x for x in rng.sample(pool, 2000) if 'ORI' in x[1]][:120]
res = rlean.check([(p, rlean.render(p, b, flip=('Or.inl', 'Or.inr'))) for p, b in xs])
ok = [x for x, (o, _, _) in zip(xs, res) if o]
def ori_forms(b):
    out = []
    for part in b.split(' ; '):
        t = part.split()
        if t == ['QED']: continue
        c = len(t) - 1 - t[::-1].index(':'); j = 1
        while t[j] == '|': j += 1
        if t[c + 1].startswith('ORI'): out.append(' '.join(t[j:c]))
    return out
def same_sides(f):
    # f = ( A v B ) with A == B at top level
    t = f.split()[1:-1]; d = 0
    for i, x in enumerate(t):
        d += (x == '(') - (x == ')')
        if x == 'v' and d == 0: return ' '.join(t[:i]) == ' '.join(t[i + 1:])
    return False
print('flip pass', len(ok), 'of', len(xs), '; of the passes, all ORI formulas A v A:', sum(all(same_sides(f) for f in ori_forms(b)) for _, b in ok))
for p, b in ok[:3]: print(ori_forms(b))
