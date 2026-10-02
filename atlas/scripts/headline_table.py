"""Seed-level headline table across the shared pools: textbook72 (k 256), dev1108 (k 64), holdout250 (k 256), all T 0.8.
Writes atlas/data/headline_table.csv and prints a markdown table (per-seed values / mean). Same family list and
first-read-per-seed rule as make_figures.py."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location('mf', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'make_figures.py'))
# reuse the loaders without re-drawing: exec only the definitions above the first figure
src = open(spec.origin).read().split('# ---- figure 1')[0]
ns = {'__file__': spec.origin}
exec(compile(src, spec.origin, 'exec'), ns)
tb = ns['tb']; dh = ns['dh']
cols = [('textbook72', 256, tb, 72), ('dev1108', 64, dh, 1108), ('holdout250', 256, dh, 250)]
data = {p: ns['solved_by'](rows, p, k) for p, k, rows, _ in cols}
out = []
print('| family | checker | textbook72 /72 | dev1108 /1108 | holdout250 /250 |\n|---|---|---|---|---|')
for fam, st, lab, fmt, frozen in ns['ROWS']:
    cells, ck = [], None
    for p, k, _, n in cols:
        d = data[p].get((fam, st))
        if d and d['vals']:
            v = list(d['vals'].values()); ck = ck or d['checker']
            m = sum(v) / len(v)
            cells.append(f"{' / '.join(f'{x:g}' for x in v)} → **{m:.1f}**")
            out.append(dict(family=fam, stage=st, label=lab, format=fmt, pool=p, k=k, n_pool=n, checker=d['checker'],
                            seeds=len(v), per_seed=' '.join(f'{x:g}' for x in v), mean=round(m, 2)))
        else:
            cells.append('—')
    print(f"| {lab} | {ns['CHECK_MARK'].get(ck, '?').strip() or 'Lean'} | " + ' | '.join(cells) + ' |')
with open(os.path.join(ns['D'], 'headline_table.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
