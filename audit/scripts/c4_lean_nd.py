#!/usr/bin/env python3
"""C4: Lean spot-check of the inherited "ours" textbook72 reads (textbook72 run stores ND renderings, not literal texts).
nd2lean.translate is used ONLY to turn an ND proof into a Lean body; the statement is our own (c34_lean.statement) and
verdicts come from c34_lean.run (own driver).  Same four negative controls."""
import json, os, random, sys, glob
sys.path.insert(0, os.path.expanduser('~/work/claim-audit'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nd2lean
from c34_lean import statement, run, drop_last_exact

TB = os.path.expanduser('~/work/claim-audit/audit/raw/textbook72/artifacts/textbook72/eval')
rng = random.Random(20261002)
samp = []
for p in sorted(glob.glob(f'{TB}/*.jsonl')):
    rows = [r for r in map(json.loads, open(p)) if r.get('n_ok', 0) > 0 and r.get('proofs')]
    rng.shuffle(rows)
    for r in rows[:4]:
        nd = rng.choice(r['proofs'])
        try:
            src = nd2lean.translate(r['prompt'], nd, require_all_pr=False)
        except Exception as e:
            print('translate fail', os.path.basename(p), r['name'], e)
            continue
        body = src.split(':= by\n', 1)[1].rstrip('\n')
        samp.append((os.path.basename(p), r['prompt'], body))
n = len(samp)
pos = [(statement(p), b) for _, p, b in samp]
oth = []
for i in range(n):
    j = (i + 1) % n
    while samp[j][1] == samp[i][1]:
        j = (j + 1) % n
    oth.append((statement(samp[j][1]), samp[i][2]))
neg = [(statement(p, neg=True), b) for _, p, b in samp]
drp = [(statement(p), drop_last_exact(b)) for _, p, b in samp]
sry = [(statement(p), drop_last_exact(b) + '\n  exact sorry') for _, p, b in samp]
out = run(pos + oth + neg + drp + sry)
c = [sum(o for o, _ in out[k * n:(k + 1) * n]) for k in range(5)]
print(f'[c4-ours-nd] positives {c[0]}/{n}; controls accepted: other {c[1]}/{n}, negated {c[2]}/{n}, drop-exact {c[3]}/{n}, sorry {c[4]}/{n}')
for i in range(n):
    if not out[i][0]:
        print('  REJ', samp[i][0], samp[i][1][:60], out[i][1][:150], '|', samp[i][2][:200])
json.dump({'n': n, 'counts': c}, open(os.path.expanduser('~/work/claim-audit/audit/out/c34_lean_c4_ours_nd.json'), 'w'))
