#!/usr/bin/env python3
"""Reviewer M3: summarise one found file -> per round: rows, distinct (name, proof-with-renumbered-lines), own box-depth histogram, rule counts."""
import sys, json, collections, re
src, dst = sys.argv[1], sys.argv[2]
def renorm(nd):
    # own start-index normaliser: renumber line labels N<k> in order of first appearance
    m = {}
    def f(x):
        m.setdefault(x.group(0), f'N{len(m)+1}'); return m[x.group(0)]
    return re.sub(r'\bN\d+\b', f, nd)
def depth(nd):
    d = 0
    for line in nd.split(' ; '):
        t = line.split(); k = 0
        for x in t[1:]:
            if x == '|': k += 1
            else: break
        d = max(d, k)
    return d
def rules(nd):
    out = []
    for line in nd.split(' ; '):
        if ' : ' in line:
            out.append(line.split(' : ')[-1].split()[0])
    return out
per = collections.defaultdict(lambda: {'rows': 0, 'd': [0, 0, 0, 0], 'rules': collections.Counter()})
seen = {}; dup = 0; bad = 0; raw_rows = collections.Counter()
for l in open(src):
    if not l.strip(): continue
    try: r = json.loads(l)
    except Exception: bad += 1; continue
    nd = r.get('proof') or ''
    if not nd or nd.startswith('LEAN'): bad += 1; continue
    k = (r['name'], renorm(nd)); rd_ = int(r['round']); raw_rows[rd_] += 1
    if k in seen:
        dup += 1
        if rd_ < seen[k][0]: seen[k] = (rd_, nd)
        continue
    seen[k] = (rd_, nd)
for (rd_, nd) in seen.values():
    p = per[rd_]; p['rows'] += 1; p['d'][min(depth(nd), 3)] += 1; p['rules'].update(rules(nd))
json.dump({'src': src, 'dup': dup, 'bad': bad, 'raw_rows': dict(raw_rows), 'per_round': {str(k): {'rows': v['rows'], 'd': v['d'], 'rules': dict(v['rules'])}
                                                        for k, v in sorted(per.items())}}, open(dst, 'w'))
