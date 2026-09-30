import json, os, collections, statistics as S
R = os.path.expanduser('~/review/search-expert')
rows = [json.loads(l) for l in open(f'{R}/rv/fullcheck.jsonl')]
print('rechecked', len(rows), 'Lean-rejected', sum(not r['ok'] for r in rows), 'size missing', sum(r['size'] is None for r in rows))
for r in rows:
    if not r['ok']: print('REJ', r['tag'], r['name'], r['info'])
by = collections.defaultdict(dict)   # tag -> name -> (min lines, min size)
for r in rows:
    d = by[r['tag']]; cur = d.get(r['name'])
    d[r['name']] = (min(cur[0], r['lines']), min(cur[1], r['size'])) if cur else (r['lines'], r['size'])
q = lambda xs: (S.median(xs), round(S.mean(xs), 2)) if xs else None
print('per tag: n solved, median/mean shortest lines, median/mean smallest term size')
for t in sorted(by):
    v = list(by[t].values()); print(t, len(v), q([x[0] for x in v]), q([x[1] for x in v]))
for pool in ('l2', 'rr1316'):
    for ex, base, seeds in (('B', 'A', range(6)), ('C', 'A2', range(2))):
        dl = []; ds = []
        for s in seeds:
            e = by[f'{ex}_s{s}__{pool}']; b = by[f'{base}_s{s}__{pool}']
            for n in set(e) & set(b): dl.append(e[n][0] - b[n][0]); ds.append(e[n][1] - b[n][1])
        c = collections.Counter((x > 0) - (x < 0) for x in dl)
        print(f'{pool} {ex}-{base} both-solved {len(dl)}: dLines median {S.median(dl)} mean {S.mean(dl):.2f} (longer {c[1]} same {c[0]} shorter {c[-1]}); dSize median {S.median(ds)} mean {S.mean(ds):.2f}')
# lines vs L_true: fraction of solved theorems whose shortest found proof is shorter than the ND label
