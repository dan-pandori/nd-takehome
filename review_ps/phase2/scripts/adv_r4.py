"""Recompute every cell of the review's R4 table and R3 table from summary_all.json; print mismatches."""
import json, re
S = json.load(open('/home/dan/review/proof-strategies/review_ps/out/summary_all.json'))
rev = open('/home/dan/work/proof-strategies/review_proof-strategies.md').read().split('\n')
# R4 table: lines 110-128 (1-based)
hdr = rev[109]
sets = [re.match(r'\s*(\S+)', c).group(1) for c in hdr.split('|')[2:-1]]
bad = 0; n = 0
def pct(x, N): return round(100 * x / N + 1e-12, 2)
for ln in rev[111:128]:
    cells = [c.strip() for c in ln.split('|')[1:-1]]
    row = cells[0]
    for s, v in zip(sets, cells[1:]):
        k = S[s]; N = k['n']
        if row == 'working #10':
            x = k['work'].get('contradiction', 0)
        elif row == 'primary #10':
            x = k['primary'].get('contradiction', 0)
        elif row.startswith('vacuous'):
            x = k['sub'].get('cond_proof.vacuous', 0)
        elif row == 'box-free':
            x = k['boxfree']
        else:
            x = k['uses'].get(row, 0)
        n += 1
        if '%.2f' % pct(x, N) != v:
            bad += 1; print('R4 mismatch', row, s, v, '%.4f' % (100 * x / N))
print('R4 cells', n, 'mismatches', bad)
