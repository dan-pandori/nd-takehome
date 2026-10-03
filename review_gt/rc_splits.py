#!/usr/bin/env python3
"""Reviewer split check (own canonicaliser): renaming class = atoms renamed by first occurrence, minimised over
every premise order. Eval: data/gt/*.jsonl (259). Training: Stage-1 files (K12, cap-6) and ladder targets/transfer."""
import json, os, itertools, re, glob
R = os.path.expanduser('~/review/guided-tts')
def parse(prompt):
    t = prompt.split(); i = t.index('SEQ'); prem = t[1:i]; goal = t[i + 1:-1]
    ps, cur, d = [], [], 0
    for x in prem:
        if x == ',' and d == 0: ps.append(cur); cur = []; continue
        d += (x == '(') - (x == ')'); cur.append(x)
    if cur: ps.append(cur)
    return ps, goal
def canon(prompt):
    ps, goal = parse(prompt); best = None
    perms = itertools.permutations(ps) if len(ps) <= 6 else [sorted(ps)]
    for perm in perms:
        mp = {}; out = []
        for f in list(perm) + [['|-'] + goal]:
            for x in f:
                if re.fullmatch(r'[A-EG-Z]', x):
                    mp.setdefault(x, 'abcdefghij'[len(mp)]); out.append(mp[x])
                else: out.append(x)
            out.append(',')
        s = ' '.join(out)
        if best is None or s < best: best = s
    return best
ev = {}
for f in sorted(glob.glob(f'{R}/data/gt/*.jsonl')):
    for l in open(f):
        r = json.loads(l); ev.setdefault(canon(r['prompt']), []).append((os.path.basename(f), r['name']))
print('eval classes', len(ev), 'from', sum(len(v) for v in ev.values()), 'rows')
TR = {'train_k12 (cap12 Stage-1)': os.path.expanduser('~/work/best-state/data/kh/train_k12.jsonl'),
      'train_depth3_f0_a1 (cap6 Stage-1)': os.path.expanduser('~/work/best-state/data/p2/train_depth3_f0_a1.jsonl'),
      'ladder rl_targets': '/home/dan/work/guided-tts/data/ladder/rl_targets.jsonl',
      'ladder transfer': '/home/dan/work/guided-tts/data/ladder/transfer.jsonl'}
for k, fn in TR.items():
    hit = {}
    n = 0
    for l in open(fn):
        r = json.loads(l); n += 1
        c = canon(r['prompt'])
        if c in ev: hit.setdefault(c, 0); hit[c] += 1
    rows = sorted({x for c in hit for x in ev[c]})
    print(f'{k}: {n} rows; eval classes hit {len(hit)}; eval rows {len(rows)}', rows[:12])
