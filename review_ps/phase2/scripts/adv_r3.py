"""Recompute the review's R3 table (K12) from summary_all.json; print mismatches."""
import json
S = json.load(open('/home/dan/review/proof-strategies/review_ps/out/summary_all.json'))['k12']
rev = open('/home/dan/work/proof-strategies/review_proof-strategies.md').read().split('\n')
N = S['n']; bad = 0; n = 0
def p2(x): return '%.2f' % (100 * x / N)
for ln in rev[83:97]:   # lines 84-97
    c = [x.strip() for x in ln.split('|')[1:-1]]
    name = c[1]
    if name == 'trivial':
        vals = [('curried', S['curried'].get('trivial', 0), c[6])]
    else:
        u = S['uses'].get(name, 0)
        vals = [('uses', u, c[2].replace(',', '')), ('uses%', p2(u), c[3]), ('primary', p2(S['primary'].get(name, 0)), c[5]),
                ('curried', p2(S['curried'].get(name, 0)), c[6])]
        if c[4] != '–':
            vals.append(('working', p2(S['work'].get(name, 0)), c[4]))
    for k, mine, theirs in vals:
        n += 1
        m = str(mine) if k == 'uses' else (mine if isinstance(mine, str) else p2(mine))
        if m != theirs:
            bad += 1; print('R3', name, k, 'review', theirs, 'recomputed', m)
print('R3 cells', n, 'mismatches', bad)
